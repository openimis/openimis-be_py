import os
import json

from ...skeletons import get_skeleton_yaml_ci_run
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from git import Repo
from openIMIS.openimisapps import openimis_apps
from pathlib import Path


class Command(BaseCommand):
    help = "This command will add yaml file which allows to execute CI on every PR"

    def add_arguments(self, parser):
        parser.add_argument('module_name', type=str)

    def handle(self, *args, **options):
        pass
