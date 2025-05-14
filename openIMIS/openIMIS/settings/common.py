import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODE = os.environ.get("MODE", 'prod').lower()
if MODE == "dev":
    DEBUG = True
else:
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
