# core/management/commands/load_fixtures.py
import os
import json
import uuid
from datetime import date
from pathlib import Path
from collections import defaultdict

import networkx as nx  # pip install networkx (required for dependency graph + cycle detection)

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from django.db.utils import IntegrityError
from django.db.models import ForeignKey
from django.core.management import call_command
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = "Load JSON fixtures with smart skipping (skip if current data exists) + dependency-aware bulk_create"

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

        # Phase 3: NEW dependency-aware save (mandatory FKs → non-mandatory FKs → update remaining)
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
                fields = obj['fields']
                fields['pk'] = obj.get('pk')
                if not model:
                    self.stdout.write(self.style.ERROR(f"No model in object in {name}"))
                    continue
                raw_data[model].append(fields)
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
            
            for fields in fields_list:
                # Remove 'id' if present
                if not keep_id:
                    fields.pop('id', None)
                # Handle FK fields
                raw_fks = {}
                for field in Model._meta.get_fields():
                    if field.is_relation and field.many_to_one:
                        raw_value = fields.get(field.name)
                        if raw_value is not None:
                            raw_fks[field.name] = raw_value
                            fields[field.name] = None
                instance = Model(**fields)
                instance._raw_fks = raw_fks
                collected_objects[model_name].append(instance)
        self.stdout.write(f"Phase 2: Instantiated {sum(len(v) for v in collected_objects.values())} objects")
        return collected_objects

    def phase3_resolve_save(self, collected_objects):
        """3-PASS dependency-aware saving with cycle detection"""
        self.stdout.write("Phase 3: Building dependency graph + saving in topological order...")

        # Build full dependency graph (model → models it depends on via any FK)
        G = self._build_dependency_graph(collected_objects)

        # Separate models by whether they have mandatory FKs
        mandatory_models, nullable_models = self._classify_models(collected_objects)

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

    def _classify_models(self, collected_objects):
        """Return two lists: models with at least one mandatory FK, and the rest"""
        mandatory = []
        nullable = []
        for model_name, instances in collected_objects.items():
            if not instances:
                continue
            Model = instances[0].__class__
            has_mandatory_fk = any(
                isinstance(f, ForeignKey) and not f.null and not getattr(f, "parent_link", None)
                for f in Model._meta.get_fields()
            )
            if has_mandatory_fk:
                mandatory.append(model_name)
            else:
                nullable.append(model_name)
        return mandatory, nullable

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

    def _inject_pks_after_bulk_create(self, Model, objects):
        """
        After bulk_create(ignore_conflicts=True), inject the real primary keys
        back into the in-memory model instances.
        """
        if not objects:
            return

        model_name = Model._meta.label_lower

        # Choose the best lookup field (natural key)
        lookup_field = None
        for fname in ['uuid', 'code', 'name', 'slug']:
            if hasattr(Model, fname):
                lookup_field = fname
                break

        if not lookup_field:
            lookup_field = 'pk'  # fallback

        # Collect lookup values
        lookup_values = []
        value_to_instance = {}

        for instance in objects:
            val = getattr(instance, lookup_field, None)
            if val is not None:
                lookup_values.append(val)
                value_to_instance[val] = instance

        if not lookup_values:
            self.stdout.write(f"   → No lookup values for {model_name}")
            return

        # Query DB to get real pks
        qs = Model.objects.filter(**{f"{lookup_field}__in": lookup_values})

        injected = 0
        for db_obj in qs:
            key = getattr(db_obj, lookup_field)
            instance = value_to_instance.get(key)
            if instance:
                instance.pk = db_obj.pk
                instance.id = db_obj.pk   # for convenience
                injected += 1

        self.stdout.write(
            f"   → Injected real pk into {injected}/{len(objects)} {model_name} instances "
            f"(using {lookup_field})"
        )

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

            # 1. Try in-memory candidates (fallback)
            candidates = collected_objects.get(related_name, [])
            for key in ['uuid', 'code', 'name', 'pk']:
                if hasattr(related_model, key):
                    match = next((c for c in candidates if getattr(c, key, None) == raw_value), None)
                    if match:
                        break
            if match and getattr(match, 'pk', None):
                setattr(instance, f"{field_name}_id", match.pk)
            elif not field.null:
            # Fallback to DB query (slow but safe)
                try:
                    for key in ['uuid', 'code', 'name', 'pk']:
                        if hasattr(related_model, key) and isinstance(raw_value, str):
                            match = related_model.objects.filter(**{key: raw_value}).first()
                        if match:
                            setattr(instance, f"{field_name}_id", match.pk)
                            break
                except related_model.DoesNotExist:
                    if not field.null:
                        raise ValueError(f"Missing mandatory FK {field_name}={raw_value} in {Model._meta.label_lower}")
            else:
                pass

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