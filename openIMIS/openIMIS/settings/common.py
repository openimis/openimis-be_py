import os
import sys
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).absolute().parent.parent.parent

MODE = os.environ.get("MODE", 'prod').lower()
if MODE == "dev" or "test" in sys.argv:
    DEBUG = True
else:
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"