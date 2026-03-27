# core/management/commands/load_fixtures.py
import os
import json
from datetime import date
from pathlib import Path
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction
from django.core.management import call_command

class Command(BaseCommand):
    help = "Load JSON fixtures with smart skipping (skip if current data exists)"

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

        for fixture_path in json_files:
            self.load_single_fixture(fixture_path)

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

    def count_current_records(self, Model):
        """
        Count records that are *currently active* based on openIMIS soft-delete convention:
            - validity_from < today  → record is active now
            - validity_to IS NULL    → not soft-deleted

        If the model does NOT have these fields → just count all records.
        """
        today = date.today()

        # Check if model has both fields
        has_validity_from = any(f.name == 'validity_from' for f in Model._meta.get_fields())
        has_validity_to = any(f.name == 'validity_to' for f in Model._meta.get_fields())

        qs = Model.objects.all()

        if has_validity_from and has_validity_to:
            qs = qs.filter(validity_from__lt=today, validity_to__isnull=True)
        elif has_validity_from:
            qs = qs.filter(validity_from__lt=today)
        # else: no validity fields → count all

        return qs.count()

    def load_single_fixture(self, fixture_path):
        name = fixture_path.name
        self.stdout.write(f"Checking {name}...")

        try:
            with open(fixture_path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Cannot read {name}: {e}"))
            raise SystemExit(5)

        if not data:
            self.stdout.write(f"Empty file {name} – skipping")
            return

        model_name = data[0].get('model')
        if not model_name:
            self.stdout.write(f"No model in {name} – skipping")
            return

        app_label, model_name = model_name.split('.', 1)
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            self.stdout.write(self.style.ERROR(f"Model '{model_name}' not found"))
            return

        count = self.count_current_records(Model)

        force_models = {'core.role'}
        force_files = {'interactive-user.json'}

        if count == 0:
            do_load = True
        elif count == 1 and (model_name in force_models or name in force_files):
            self.stdout.write(self.style.WARNING(
                f"Overwriting single record for {model_name} ({name})"
            ))
            do_load = True
        else:
            self.stdout.write(
                f"Skipping {model_name} ({name}): {count} current record(s)"
            )
            do_load = False

        if not do_load:
            return

        self.stdout.write(f"Loading {name}...")
        try:
            with transaction.atomic():
                if model_name == 'core.roleright':
                    call_command('load_fixture_foreign_key', str(fixture_path), field='name')
                else:
                    call_command('loaddata', str(fixture_path))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to load {name}: {e}"))
            raise SystemExit(5)