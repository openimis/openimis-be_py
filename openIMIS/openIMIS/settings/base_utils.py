"""Small, Django-independent helpers for the settings package, kept out of
base.py so they can be unit-tested in isolation (see test_base_utils.py)."""

import importlib.util
import sys
from pathlib import Path


def locate_module_file(module_dotted_path):
    """Find a module's source file without importing it.

    Scans ``sys.path``, and also resolves the top-level package through the
    import system, so editable installs exposed via an import finder (PEP 660) —
    whose package directory is not on ``sys.path`` — are still found.
    ``find_spec`` on the top-level package does not execute its ``__init__.py``.
    """
    parts = module_dotted_path.split(".")
    relative = Path(*parts)

    bases = [Path(entry) for entry in sys.path]
    try:
        top_spec = importlib.util.find_spec(parts[0])
    except (ImportError, ValueError):
        top_spec = None
    if top_spec and top_spec.submodule_search_locations:
        bases.extend(Path(loc).parent for loc in top_spec.submodule_search_locations)

    for base in bases:
        for candidate in (
            base / relative.with_suffix(".py"),
            base / relative / "__init__.py",
        ):
            if candidate.is_file():
                return candidate
    return None
