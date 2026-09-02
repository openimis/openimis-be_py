"""Regression test for locate_module_file (OP-3125).

Loads base_utils directly from its file so the test stays hermetic — no Django
settings / celery import chain.
"""

import importlib.abc
import importlib.util
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

_MODULE_PATH = Path(__file__).with_name("base_utils.py")
_spec = importlib.util.spec_from_file_location("_base_utils_under_test", _MODULE_PATH)
_base_utils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_utils)
locate_module_file = _base_utils.locate_module_file


class _FinderOnly(importlib.abc.MetaPathFinder):
    """Expose a package through find_spec only — like a PEP 660 editable install
    — without putting its directory on sys.path."""

    def __init__(self, name, pkg_dir):
        self._name = name
        self._spec = importlib.util.spec_from_file_location(
            name,
            pkg_dir / "__init__.py",
            submodule_search_locations=[str(pkg_dir)],
        )

    def find_spec(self, fullname, path=None, target=None):
        return self._spec if fullname == self._name else None


def _make_pkg(root, name, submodule):
    pkg = Path(root) / name
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / f"{submodule}.py").write_text("class A:\n    pass\n")
    return pkg


class LocateModuleFileTests(unittest.TestCase):
    def test_finds_module_on_sys_path(self):
        with TemporaryDirectory() as tmp:
            pkg = _make_pkg(tmp, "pathpkg", "sub")
            sys.path.insert(0, tmp)
            try:
                found = locate_module_file("pathpkg.sub")
            finally:
                sys.path.remove(tmp)
            self.assertEqual(found, pkg / "sub.py")

    def test_finds_finder_based_module_not_on_sys_path(self):
        # Regression (OP-3125): editable installs (PEP 660) expose the package
        # through an import finder, not a sys.path entry, so a sys.path-only
        # scan misses the source.
        with TemporaryDirectory() as tmp:
            pkg = _make_pkg(tmp, "finderpkg", "mod")
            self.assertNotIn(tmp, sys.path)
            finder = _FinderOnly("finderpkg", pkg)
            sys.meta_path.insert(0, finder)
            try:
                found = locate_module_file("finderpkg.mod")
            finally:
                sys.meta_path.remove(finder)
            self.assertEqual(found, pkg / "mod.py")


if __name__ == "__main__":
    unittest.main()
