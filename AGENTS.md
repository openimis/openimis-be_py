# openIMIS Backend Assembly — Agent Guide

The `backend/` directory is the **Django assembly shell** (`openimis-be_py`). It does not contain most business logic; modules under `../backend-packages/` are installed as editable Python packages and registered in `openimis.json`.

## Directory map

```
backend/
├── openIMIS/              # Django project root (manage.py lives here)
├── openimis.json          # Module manifest (pip sources for CI/production)
├── openimis-dev.json      # Local dev manifest (editable installs from backend-packages/)
├── script/                # modules-requirements.py, setup helpers
├── fixtures/              # Demo and solution fixtures
├── .flake8                # Lint config for the assembly workspace
├── .vscode/launch.json    # Django runserver, migrate, and test configurations
└── requirements.txt       # Base Python dependencies
```

## How modules connect

1. Each entry in `openimis.json` / `openimis-dev.json` has a `name` (Django app label) and `pip` source.
2. `script/modules-requirements.py` turns the JSON into `script/modules-requirements.txt`.
3. `pip install -r script/modules-requirements.txt` installs all modules.
4. In local dev, `openimis-dev.json` uses paths like `-e file:/…/backend-packages/core`.
5. Django discovers apps from installed `openimis-be-*` packages; each module exposes `urls.py` (may be empty).

To work on a module locally, edit code in `../backend-packages/<module>/` — the assembly picks it up via the editable install (no reinstall needed for most changes).

## Running the backend

```bash
cd backend
pip install -r requirements.txt
cd script && python modules-requirements.py ../openimis-dev.json > modules-requirements.txt
pip install -r modules-requirements.txt
cp .env.example .env   # adjust DB settings
cd ../openIMIS
OPENIMIS_CONF=../openimis-dev.json python manage.py migrate
OPENIMIS_CONF=../openimis-dev.json python manage.py runserver
```

Use **Python 3.11** (3.14 is not supported). Set `OPENIMIS_CONF` to point at the desired JSON manifest.

## Testing — Django required

Backend module tests run through the **Django test runner** in the assembly, not in isolation (unless a module explicitly supports pytest standalone).

### VS Code (preferred)

Use configurations in `.vscode/launch.json`:

| Configuration | Purpose |
|---------------|---------|
| **Test module** | Run tests for one module (`${input:moduleName}`), with `--keepdb --debug-mode --timing` |
| **Test module (just my code)** | Same, but `justMyCode: true` |
| **Test** | Run all modules listed in the manifest |
| **migrate** / **make migration** | Schema changes |
| **Start** | `runserver` on port 8000 |

Pick the DB engine when prompted (`psql` or `mssql`). Working directory is always `openIMIS/`.

### Command line

From `backend/openIMIS/`:

```bash
OPENIMIS_CONF=../openimis-dev.json python manage.py test --keepdb --timing <module_name>
```

Example for the core module:

```bash
python manage.py test --keepdb core
```

CI runs the same pattern: `python manage.py test --keepdb $MODULE_NAME` against PostgreSQL (see `.github/workflows/ci_module.yml`).

### Test environment notes

- `--keepdb` reuses the test database between runs.
- Celery is stubbed in test configs via in-memory broker/backend (see launch.json env vars).
- Some modules need OpenSearch or other services; check module README and CI service definitions.

## Linting — flake8

Run flake8 from the **`backend/` directory** so the assembly `.flake8` config applies.

For a specific module, lint its Django app package (the directory matching the module `name`):

```bash
cd backend
flake8 core --ignore=W503,E501
```

Replace `core` with the target module's app label (e.g. `workflow`, `controls`, `claim`).

The assembly `.flake8` (in `backend/.flake8`) also ignores `E261`, `E303`, `E741`, `F401` and excludes migrations. CI uses `--ignore W503` per module directory. When in doubt, match CI:

```bash
python -m flake8 ../backend-packages/<module>/<app_name> --ignore=W503
```

## Documentation

When adding or changing backend behaviour, update documentation in the **module repository**:

- **`docs/`** — module-specific technical docs (GraphQL queries, services, configuration, etc.)
- **`README.md`** — overview, installation, test commands, ORM mapping tables

The assembly repo holds cross-cutting docs like `GraphQL.md` and `README.md` (environment variables, distributor setup). Module feature docs belong in the module's own `docs/` folder under `../backend-packages/<module>/`.

## Module development checklist

1. Create a branch in the module repo (`../backend-packages/<module>/`).
2. Implement changes in the Django app package (`<module>/<app_name>/`).
3. Add or update tests in `<app_name>/tests.py` or `tests/`.
4. Run **Test module** launch config (or `manage.py test --keepdb <module>`).
5. Run **flake8** on the app package.
6. Update **`docs/`** and **`README.md`** in the module repo.
7. Bump version in `setup.py` when releasing; open PR on the module's GitHub repo.

## Reference module

Use `../backend-packages/core/` as the reference implementation for patterns (GraphQL, services, reports, permissions). New modules should follow its structure.

## Regenerating local module links

If modules are missing or paths are stale:

```bash
# from openimis-dev-tools root
python python/setup-local-dev.py
```

This reclones/updates `backend-packages/` and regenerates `openimis-dev.json`.

## Related files

- `../AGENTS.md` — overall workspace layout
- `../frontend/AGENTS.md` — frontend assembly rules
- `.env.example` — database and runtime environment variables
- `fixtures/demo/` — demo data loadable via `load_fixtures` management command