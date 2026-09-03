# core/management/commands/load_fixtures.py
import json
from pathlib import Path
from collections import defaultdict

import networkx as nx  # pip install networkx (required for dependency graph + cycle detection)

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.db import transaction
from django.db.utils import IntegrityError
from django.db.models import ForeignKey
from django.core.exceptions import FieldDoesNotExist


class Command(BaseCommand):
    help = (
        "Load JSON fixtures (supporting both django/Python field names from the model file "
        "and legacy fixtures that used raw db_column names). "
        "Smart skipping + full dependency-aware multi-pass save (mandatory FKs first, "
        "then nullable, then updates for cycles). In-memory construction (not objects.create) "
        "so we can order saves correctly and resolve FKs across the batch."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            type=str,
            default='../fixtures',
            help='Directory containing .json fixtures (default: ../fixtures)'
        )
        parser.add_argument(
            '--solution',
            type=str,
            help='Load fixtures from a cloned solution (e.g. "openIMIS")'
        )

    def handle(self, *args, **options):
        solution = options['solution']
        if solution and solution != 'openIMIS':
            fixture_dir = self.clone_solution(solution)
        else:
            fixture_dir = Path(options['dir'])

        if not fixture_dir.exists():
            self.stdout.write(self.style.ERROR(f"Fixture directory does not exist: {fixture_dir}"))
            return

        json_files = sorted(fixture_dir.rglob("*.json"))
        if not json_files:
            self.stdout.write("No .json fixtures found.")
            return

        self.stdout.write(f"Loading fixtures from: {fixture_dir}")

        # Phase 1: Collect raw data
        raw_data = self.phase1_collect_raw(json_files)

        # Phase 2: Instantiate models
        collected_objects = self.phase2_instantiate(raw_data)

        # Phase 3: dependency-aware save (mandatory FKs → non-mandatory FKs → update remaining)
        self.phase3_resolve_save(collected_objects)

        self.stdout.write(self.style.SUCCESS("All fixtures processed."))

    def clone_solution(self, solution_name):
        """Clone openIMIS solutions repo and return fixture path"""
        init_dir = Path("./initialization")
        solution_path = init_dir / solution_name
        fixtures_dir = solution_path / "fixtures"

        if fixtures_dir.exists():
            return fixtures_dir

        self.stdout.write(f"Cloning solution '{solution_name}' from openIMIS/solutions...")
        init_dir.mkdir(exist_ok=True)
        import subprocess
        result = subprocess.run([
            "git", "clone", "--depth", "1",
            "https://github.com/openimis/solutions.git",
            str(init_dir / "tmp_solutions")
        ], capture_output=True, text=True)

        if result.returncode != 0:
            self.stdout.write(self.style.ERROR(f"Git clone failed: {result.stderr}"))
            raise SystemExit(2)

        src = init_dir / "tmp_solutions" / solution_name
        if not src.exists():
            self.stdout.write(self.style.ERROR(f"Solution '{solution_name}' not found."))
            raise SystemExit(2)

        src.rename(solution_path)
        (init_dir / "tmp_solutions").rmdir()
        return fixtures_dir

    def phase1_collect_raw(self, json_files):
        raw_data = defaultdict(list)
        for fixture_path in json_files:
            name = fixture_path.name
            self.stdout.write(f"Reading {name}...")
            try:
                with open(fixture_path, encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Cannot read {name}: {e}"))
                raise SystemExit(5)
            if not data:
                self.stdout.write(f"Empty file {name} – skipping")
                continue
            for obj in data:
                model = obj.get('model')
                if not model:
                    self.stdout.write(self.style.ERROR(f"No model in object in {name}"))
                    continue
                fields = dict(obj.get('fields') or {})
                fields['pk'] = obj.get('pk')
                # Store with source for better error reporting
                raw_data[model].append((fields, name))
        self.stdout.write(f"Phase 1: Collected raw data for {len(raw_data)} models")
        return raw_data

    def phase2_instantiate(self, raw_data, keep_id=False):
        collected_objects = defaultdict(list)
        for model_name, fields_list in raw_data.items():
            app_label, model_short = model_name.split('.', 1)
            try:
                Model = apps.get_model(app_label, model_short)
            except LookupError:
                self.stdout.write(self.style.ERROR(f"Model '{model_name}' not found"))
                continue
            
            for raw_item in fields_list:
                # raw_item is now (fields_dict, source_file_name) for better diagnostics
                if isinstance(raw_item, tuple):
                    raw_fields, source_file = raw_item
                else:
                    raw_fields, source_file = raw_item, "unknown"
                fields = dict(raw_fields)  # copy to avoid mutating shared raw data
                # Remove 'id' if present
                if not keep_id:
                    fields.pop('id', None)
                # Normalize keys from the fixture (which may use django names or legacy db_column
                # names) to the canonical Python/django names from the model metadata.
                # We prefer to keep the django names for Model(**...) etc.
                fields = self._normalize_fields(Model, fields)
                # Handle FK fields (now using normalized python names)
                raw_fks = {}
                for field in Model._meta.get_fields():
                    if isinstance(field, ForeignKey) and not getattr(field, 'parent_link', False):
                        raw_value = fields.get(field.name)
                        if raw_value is not None:
                            raw_fks[field.name] = raw_value
                            fields[field.name] = None
                # Drop any remaining unknown keys to prevent TypeError on Model(**)
                valid_names = {
                    f.name for f in Model._meta.get_fields()
                    if not getattr(f, 'auto_created', False)
                }
                valid_names.update(['pk', 'id'])
                fields = {k: v for k, v in fields.items() if k in valid_names}

                # Safely remap fixture 'pk' (top-level natural key value) to the model's actual PK field name.
                # This prevents "Model() got unexpected keyword argument: 'pk'" on models whose PK field
                # is not literally named 'pk' (most openIMIS models use 'id' + db_column).
                if 'pk' in fields:
                    pk_value = fields.pop('pk')
                    if pk_value is not None:
                        pk_name = Model._meta.pk.name
                        if pk_name not in fields or fields.get(pk_name) in (None, ''):
                            fields[pk_name] = pk_value

                try:
                    # We construct in-memory using the (normalized) django/Python field names.
                    # We do NOT use Model.objects.create() here because:
                    # - We must collect *all* objects first to build the full dep graph.
                    # - Saves happen later in strict topological order (mandatory FKs first,
                    #   then nullable, then a 3rd pass for cycles/forward refs).
                    # - We attach _raw_fks for deferred resolution and do in-memory PK injection.
                    # - We support skipping on IntegrityError and temporary NULLs for cycles.
                    # Using create() would immediately hit the DB, break ordering, and cause
                    # FK violations or lost _raw_fks state.
                    # We always keep/resolve to the django names (from model metadata) for the
                    # constructor and all subsequent operations.
                    instance = Model(**fields)
                except TypeError as exc:
                    if "unexpected keyword arguments" in str(exc):
                        extra = [k for k in fields.keys() if k not in valid_names]
                        self.stdout.write(self.style.ERROR(
                            f"Model instantiation failed for {model_name} (source: {source_file}). "
                            f"Fields passed: {list(fields.keys())}. "
                            f"Possible extra keys: {extra}. Original error: {exc}"
                        ))
                    raise
                instance._raw_fks = raw_fks
                collected_objects[model_name].append(instance)
        self.stdout.write(f"Phase 2: Instantiated {sum(len(v) for v in collected_objects.values())} objects")
        return collected_objects

    def _normalize_fields(self, Model, fields):
        """Ensure all keys coming from the fixture end up as the Python/Django field names
        declared in the model file (what Model(**kwargs) and the rest of Django expect).

        We use the model's field metadata (f.name, f.db_column, f.attname) to build the
        mapping dynamically. This way we tolerate fixtures that (wrongly) used raw DB
        column names as the keys in "fields", while always preferring/keeping the django
        names for the actual instance construction and later FK resolution.
        """

        if not fields:
            return {}
        # Map from "whatever key appears in the fixture JSON" -> django/Python field name
        # (from the model definition). We build this from the actual field metadata
        # (f.name + db_column + attname). We ALWAYS resolve to (and keep) the django names.
        fixture_key_to_django_name = {}
        for f in Model._meta.get_fields():
            if getattr(f, 'auto_created', False):
                continue
            py = f.name
            fixture_key_to_django_name[py] = py
            dbcol = getattr(f, 'db_column', None)
            if dbcol and dbcol not in fixture_key_to_django_name:
                fixture_key_to_django_name[dbcol] = py
            attname = getattr(f, 'attname', None)
            if attname and attname not in fixture_key_to_django_name:
                fixture_key_to_django_name[attname] = py

        # Small number of extra aliases for real-world weird legacy fixtures.
        # Prefer the dynamic metadata above.
        common_legacies = {
            'ValidityFrom': 'validity_from',
            'ValidityTo': 'validity_to',
            'LegacyID': 'legacy_id',
            'RoleUUID': 'uuid',
            'RoleName': 'name',
            'roleName': 'name',
            'AltLanguage': 'alt_language',
            'IsSystem': 'is_system',
            'IsBlocked': 'is_blocked',
            'AuditUserID': 'audit_user_id',
        }
        for leg, py in common_legacies.items():
            fixture_key_to_django_name.setdefault(leg, py)

        # Normalize: every key coming out is a django name from the model file.
        normalized = {}
        for k, v in fields.items():
            target = fixture_key_to_django_name.get(k)
            if target is None:
                # case-insensitive fallback
                k_lower = k.lower()
                for leg_key, py_name in fixture_key_to_django_name.items():
                    if leg_key.lower() == k_lower:
                        target = py_name
                        break
            if target is None:
                target = k  # unknown -> will be dropped by the caller filter
            if target not in normalized or normalized.get(target) is None:
                normalized[target] = v
        return normalized

    def phase3_resolve_save(self, collected_objects):
        """3-PASS dependency-aware saving with cycle detection"""
        self.stdout.write("Phase 3: Building dependency graph + saving in topological order...")

        # Build full dependency graph (model → models it depends on via any FK)
        G = self._build_dependency_graph(collected_objects)

        with transaction.atomic():
            # ====================== PASS 1: Mandatory FKs only (strict order) ======================
            self.stdout.write(self.style.NOTICE("Pass 1: Saving models with mandatory FKs (topological order)"))
            G_mandatory = self._build_dependency_graph(collected_objects, mandatory_only=True)

            try:
                if not nx.is_directed_acyclic_graph(G_mandatory):
                    raise nx.NetworkXUnfeasible("Cycle detected in mandatory FKs")
                order = list(nx.topological_sort(G_mandatory))
                self._bulk_create_in_order(order, collected_objects, mandatory_only=True)
            except (nx.NetworkXUnfeasible, nx.HasACycle):
                self.stdout.write(self.style.WARNING("Cycle detected in mandatory FKs – falling back to arbitrary order"))
                self._bulk_create_in_order(list(collected_objects.keys()), collected_objects, mandatory_only=True)

            # ====================== PASS 2: Non-mandatory (nullable) FKs ======================
            self.stdout.write(self.style.NOTICE("Pass 2: Saving models with nullable FKs (topological order)"))
            try:
                if not nx.is_directed_acyclic_graph(G):
                    raise nx.NetworkXUnfeasible("Cycle detected")
                order = list(nx.topological_sort(G))
                self._bulk_create_in_order(order, collected_objects, mandatory_only=False)
            except (nx.NetworkXUnfeasible, nx.HasACycle):
                self.stdout.write(self.style.WARNING("Cycle detected in full graph – creating with temporary NULL for nullable FKs"))
                # Fallback: create everything, setting unresolved nullable FKs to None
                self._bulk_create_with_temporary_nulls(collected_objects)

            # ====================== PASS 3: Update FKs that failed in Pass 2 (forward refs / cycles) ======================
            self.stdout.write(self.style.NOTICE("Pass 3: Updating remaining FKs (cycles or forward references)"))
            self._update_remaining_fks(collected_objects)

        self.stdout.write(self.style.SUCCESS("Phase 3 completed – all objects saved with dependencies resolved."))

    def _build_dependency_graph(self, collected_objects, mandatory_only=False):
        """Build DiGraph: child_model depends on parent_model"""
        G = nx.DiGraph()
        for model_name in collected_objects:
            G.add_node(model_name)

        for model_name, instances in collected_objects.items():
            if not instances:
                continue
            Model = instances[0].__class__

            for field in Model._meta.get_fields():
                if isinstance(field, ForeignKey) and not getattr(field, 'parent_link', False):
                    if mandatory_only and field.null:  # nullable fk not consider if only mandatory fk should be linked
                        continue
                    related_model_name = field.related_model._meta.label_lower
                    if related_model_name in collected_objects:
                        G.add_edge(related_model_name, model_name)  # depends on
        return G

    def _bulk_create_in_order(self, order, collected_objects, mandatory_only=False):
        """Save models in topological order and inject pks immediately"""
        for model_name in order:
            objects = collected_objects.get(model_name)
            if not objects:
                continue

            Model = objects[0].__class__

            # Resolve FKs (now safer because previous models have real pks)
            for instance in objects:
                self._resolve_instance_fks(instance, collected_objects, mandatory_only=mandatory_only)

            # Bulk create
            self.stdout.write(f"   → Bulk to be created {len(objects)} {model_name} objects")
            # Save individually to ensure PKs are set
            saved_count = 0
            for instance in objects:
                try:
                    instance.save()
                    saved_count += 1
                except IntegrityError:
                    self.stdout.write(f"   → Skipped existing {model_name} instance")
            self.stdout.write(f"   → Saved {saved_count} {model_name} objects")

            # PKs are set by save()

    def _bulk_create_with_temporary_nulls(self, collected_objects):
        """Fallback when cycle exists – create everything, nullable FKs set to None temporarily"""
        for model_name, objects in collected_objects.items():
            if not objects:
                continue
            Model = objects[0].__class__

            for instance in objects:
                # Only resolve mandatory FKs + already-created objects
                self._resolve_instance_fks(instance, collected_objects, mandatory_only=True)

            # Save individually
            saved_count = 0
            for instance in objects:
                try:
                    instance.save()
                    saved_count += 1
                except IntegrityError:
                    self.stdout.write(f"   → Skipped existing {model_name} instance")
            self.stdout.write(f"   → Saved {saved_count} {model_name} objects (nullable FKs deferred)")

    def _resolve_instance_fks(self, instance, collected_objects, mandatory_only=False):
        """Resolve FKs preferring ID maps (fast + reliable)"""
        raw_fks = getattr(instance, '_raw_fks', {})
        Model = instance.__class__

        for field_name, raw_value in list(raw_fks.items()):
            try:
                field = Model._meta.get_field(field_name)
            except FieldDoesNotExist:
                continue
            if not isinstance(field, ForeignKey):
                continue
            if mandatory_only and field.null:
                continue

            if isinstance(raw_value, list) and len(raw_value) == 1:
                raw_value = raw_value[0]
            elif isinstance(raw_value, list):
                continue

            related_model = field.related_model
            related_name = related_model._meta.label_lower

            match = None

            # 1. Try in-memory candidates (from objects we have already processed in this run)
            candidates = collected_objects.get(related_name, [])
            for key in ['uuid', 'code', 'name', 'pk']:
                if hasattr(related_model, key):
                    match = next((c for c in candidates if getattr(c, key, None) == raw_value), None)
                    if match:
                        break
            if match and getattr(match, 'pk', None):
                setattr(instance, f"{field_name}_id", match.pk)
                continue

            # 2. If still no match and we need the FK, fall back to DB lookup (by natural key)
            if not field.null or not mandatory_only:
                if isinstance(raw_value, str):
                    for key in ['uuid', 'code', 'name']:
                        if hasattr(related_model, key):
                            match = related_model.objects.filter(**{key: raw_value}).first()
                            if match:
                                setattr(instance, f"{field_name}_id", match.pk)
                                break
                if not match and not field.null:
                    # Last resort: try by pk if raw_value looks like an int id
                    try:
                        if str(raw_value).isdigit():
                            match = related_model.objects.filter(pk=int(raw_value)).first()
                            if match:
                                setattr(instance, f"{field_name}_id", match.pk)
                    except Exception:
                        pass

                if not match and not field.null:
                    raise ValueError(
                        f"Missing mandatory FK {field_name}={raw_value} for {Model._meta.label_lower} "
                        f"(no match in collected objects or DB by uuid/code/name/pk)"
                    )

    def _update_remaining_fks(self, collected_objects):
        """Pass 3: Update any FKs that were still None (cycles / forward references)"""
        updated_count = 0
        for model_name, objects in collected_objects.items():
            if not objects:
                continue
            Model = objects[0].__class__

            update_fields = []
            for instance in objects:
                raw_fks = getattr(instance, '_raw_fks', {})
                changed = False
                for field_name, raw_value in raw_fks.items():
                    if getattr(instance, field_name) is None:  # was deferred
                        # Re-resolve now that everything exists
                        self._resolve_instance_fks(instance, collected_objects, mandatory_only=False)
                        if getattr(instance, field_name) is not None:
                            changed = True
                            if field_name not in update_fields:
                                update_fields.append(field_name)

                if changed:
                    updated_count += 1

            if update_fields:
                # Bulk update only the FK fields that changed
                Model.objects.bulk_update(objects, update_fields, batch_size=1000)
                self.stdout.write(f"   → Updated FKs for {len(objects)} {model_name} objects")

        if updated_count:
            self.stdout.write(self.style.SUCCESS(f"Pass 3: Updated {updated_count} objects with deferred FKs"))
        else:
            self.stdout.write("Pass 3: No deferred FKs needed")