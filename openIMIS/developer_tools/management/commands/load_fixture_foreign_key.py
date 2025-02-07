from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
import json
from django.apps import apps
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Load a fixture and replace foreign keys using a natural key (like uuid, name, location, etc.) with corresponding model IDs'

    def add_arguments(self, parser):
        # Argument for the fixture file
        parser.add_argument(
            'fixture_file',
            type=str,
            help='Path to the fixture file (JSON format)'
        )
        # Argument for the field name that will be used as the natural key (e.g., "uuid", "name", "location", etc.)
        parser.add_argument(
            '--field',
            type=str,
            help="The unique field to use for resolving foreign keys (e.g., 'uuid', 'name', 'location', etc.)",
            required=True
        )

    def handle(self, *args, **kwargs):
        fixture_file = kwargs['fixture_file']
        field_name = kwargs['field']

        # Load the fixture data
        try:
            with open(fixture_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Fixture file '{fixture_file}' not found"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f"Fixture file '{fixture_file}' is not valid JSON"))
            return

        # Process the fixture data
        for obj in data:
            model = obj['model']
            if model:
                # Get the model class dynamically using the app label and model name
                app_label, model_name = model.split('.')
                try:
                    model_class = apps.get_model(app_label, model_name)
                except LookupError:
                    self.stdout.write(self.style.ERROR(f"Model '{model}' not found"))
                    continue

                # Loop through fields in the fixture and process foreign keys
                for field, field_value in obj['fields'].items():
                    # If the field value is a list (e.g., ["uuid_value"]), handle it as a list
                    if isinstance(field_value, list):
                        if len(field_value) == 1:  # If there is only one element (like with the 'role' field)
                            related_field = model_class._meta.get_field(field)

                            if related_field.is_relation:  # Check if it's a foreign key
                                # Look up the related model (e.g., Role) using the field_name (e.g., uuid, name)
                                related_model = related_field.related_model
                                try:
                                    # We fetch the related object by the unique field (e.g., uuid, name, location, etc.)
                                    related_object = related_model.objects.get(**{field_name: field_value[0]})
                                    # Replace the field value with the primary key (ID) - not a list anymore
                                    obj['fields'][field] = related_object.id
                                except ObjectDoesNotExist:
                                    self.stdout.write(self.style.ERROR(
                                        f"{related_model} with {field_name} '{field_value[0]}' not found"))
                                    continue
                    # If it's not a list, process as usual (no change needed)
                    elif isinstance(field_value, str):  # Checking if the value is a string (uuid, name, etc.)
                        related_field = model_class._meta.get_field(field)
                        if related_field.is_relation:
                            related_model = related_field.related_model
                            try:
                                # Fetch the related object
                                related_object = related_model.objects.get(**{field_name: field_value})
                                # Replace the value with the ID
                                obj['fields'][field] = related_object.id
                            except ObjectDoesNotExist:
                                self.stdout.write(
                                    self.style.ERROR(f"{related_model} with {field_name} '{field_value}' not found"))
                                continue

        # Save the modified fixture to a new file
        output_file = fixture_file.replace('.json', '_modified.json')
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

        self.stdout.write(self.style.SUCCESS(f'Successfully transformed the fixture and saved it as {output_file}'))

        # Now that unique field values are replaced with IDs, load this fixture into the database
        try:
            call_command('loaddata', output_file)  # This will load the modified fixture
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded the modified fixture into the database'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading fixture: {e}'))
