import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.utils import collect_all_gql_permissions


class Command(BaseCommand):
    help = "This command will extract role translations into po files based on GQL permissions"

    def handle(self, *args, **options):
        self.__print_info('starting extracting role translations')
        output = self.extract_role_po_files()
        self.__print_success('finished extracting role translations')
        self.__print_info(output)

    def extract_role_po_files(self):
        """
        Extract GQL permissions and create a single po file with perms parts as msgid.
        """
        permissions_dict = collect_all_gql_permissions()
        perms_parts = set()
        for app, app_perms in permissions_dict.items():
            for perm_name, perm_ids in app_perms.items():
                perms_part = app + "." + perm_name if perm_name.endswith('_perms') else perm_name
                perms_parts.add(perms_part)


        locale_dir = Path(settings.BASE_DIR) / 'openIMIS' / 'locale' / 'en' / 'LC_MESSAGES'
        locale_dir.mkdir(parents=True, exist_ok=True)

        po_file = locale_dir / 'role_permissions.po'
        with open(po_file, 'w', encoding='utf-8') as f:
            f.write('# Role permissions\n')
            f.write('# Generated automatically\n\n')
            for perms_part in sorted(perms_parts):
                f.write(f'msgid "{perms_part}"\n')
                f.write('msgstr ""\n\n')

        return f'Created 1 po file: {po_file}'

    def __print_success(self, msg: str):
        """ Print message to inform about the command progress """
        self.stdout.write(self.style.SUCCESS(msg))

    def __print_info(self, msg: str):
        """ Print message to inform about the command progress = info """
        self.stdout.write(self.style.WARNING(msg))
