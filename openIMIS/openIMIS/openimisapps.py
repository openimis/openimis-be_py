import os
import logging
from importlib import resources

from .openimisconf import load_openimis_conf

logger = logging.getLogger(__name__)


def extract_app(module):
    return "%s" % (module["name"])

def openimis_apps():
    OPENIMIS_CONF = load_openimis_conf()
    return order_modules([*map(extract_app, OPENIMIS_CONF["modules"])])


def get_locale_folders():
    """
    Get locale folders for the modules in a reverse order to make it easy to override the translations
    """
    apps = []
    basedirs = []
    for mod_name in openimis_apps():
        try:
            with resources.path(mod_name, "__init__.py") as path:
                apps.append(path.parent.parent)
        except ModuleNotFoundError:
            logger.error(f"Module \"{mod_name}\" not found.")

    for topdir in ["."] + apps:
        for dirpath, dirnames, filenames in os.walk(topdir, topdown=True):
            for dirname in dirnames:
                if dirname == "locale":
                    basedirs.insert(0, os.path.join(dirpath, dirname))
    return basedirs

import importlib
import os
import ast
import warnings
from typing import List, Dict, Set

def clean_name(name):
    if 'openimis-be-' in name:
        return name[12:]
    else:
        return name
    
def find_module_path(module_name: str):
    """
    Find the path to a module without importing it.
    Returns the directory path or None if not found.
    """
    # Try to find the module spec without loading it
    spec = importlib.util.find_spec(module_name)
    if spec and spec.origin:
        # Get the directory containing the module's __init__.py or file
        module_path = os.path.dirname(spec.origin)
        return module_path
    else:
        # Module not found in standard paths
        warnings.warn(f"Could not find path for module '{module_name}' without importing")
        return None
    
    
def extract_dependencies_from_setup_py(module_name: str, module_list: Set[str]) -> List[str]:
    """
    Extract dependencies from a module's setup.py that are also in the module_list.
    Finds the module path without loading it.
    """
    module_list_extented = [f'openimis-be-{dep}' for dep in module_list if 'openimis-be-' not in dep]
    module_path = find_module_path(module_name)
    if not module_path:
        return []
    
    setup_path = os.path.join(module_path, "setup.py")
    if not os.path.exists(setup_path):
        # Fallback: Check parent directory (e.g., editable installs)
        setup_path = os.path.join(os.path.dirname(module_path), "setup.py")
        if not os.path.exists(setup_path):
            return []
    
    try:
        with open(setup_path, "r") as f:
            content = f.read()
        
        # Parse setup.py as an AST to find install_requires
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "setup":
                for keyword in node.keywords:
                    if keyword.arg == "install_requires":
                        if isinstance(keyword.value, ast.List):
                            deps = [elt.s for elt in keyword.value.elts if isinstance(elt, ast.Str)]
                            # Filter only dependencies present in module_list
                            return [clean_name(dep) for dep in deps if (dep in module_list or dep in module_list_extented)]
        return []
    except ImportError:
        warnings.warn(f"Could not import module '{module_name}' to find setup.py")
        return []
    except Exception as e:
        warnings.warn(f"Error processing setup.py for '{module_name}': {e}")
        return []

def build_dependency_dict(module_list: List[str]) -> List[Dict[str, List[str]]]:
    """
    Build a dependency dictionary where each item is {'name': [dependencies]}.
    Dependencies are extracted from setup.py dynamically.
    """
    module_set = set(module_list)
    dependency_dict = []
    
    for module in module_list:
        deps = extract_dependencies_from_setup_py(module, module_set)
        dependency_dict.append({"name": module, "dependencies": deps})
    
    return dependency_dict

def order_modules(module_list: List[str]) -> List[str]:
    """
    Order modules based on dependencies, popping those without dependencies first.
    Remove popped modules from others' dependency lists. Handle circular dependencies.
    """
    # Build the initial dependency dictionary
    module_list.remove('core')
    dep_list = build_dependency_dict(module_list)
    ordered_modules = ['core']
    remaining = dep_list.copy()

    while remaining:
        # Find modules with no dependencies
        no_deps = [m for m in remaining if not m["dependencies"]]
        
        if not no_deps:
            # Circular dependency detected
            # warnings.warn("Circular dependency detected among: " + ", ".join(m["name"] for m in remaining))
            # Break the loop by removing one dependency from the first remaining module
            if remaining[0]["dependencies"]:
                removed_dep = remaining[0]["dependencies"].pop(0)
                logger.info(f"Breaking circular dependencies by removing dependency '{removed_dep}' from '{remaining[0]['name']}'")
            continue
        
        # Process all modules with no dependencies in this pass
        for module in no_deps:
            module_name = module["name"]
            ordered_modules.append(module_name)
            remaining.remove(module)
            
            # Remove this module from all other dependency lists
            for other_module in remaining:
                if module_name in other_module["dependencies"]:
                    other_module["dependencies"].remove(module_name)
    
    return ordered_modules