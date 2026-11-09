"""Model classes defining the row-security get_queryset(cls, queryset, <ctx>).

Two naming conventions are in use for the third parameter -- `user` and `info`
-- plus variants taking extra kwargs, so match on arity rather than name. The
Django manager's own get_queryset(self) has arity 1 and is excluded.
"""
import ast
import json
import pathlib
import sys

ROOT = pathlib.Path("/mnt/data/Development/openimis-dev-tools/backend-packages")


def main():
    scoped = {}
    variants = {}
    for path in sorted(ROOT.rglob("*.py")):
        p = str(path)
        if "/tests/" in p or "/migrations/" in p:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if item.name != "get_queryset":
                    continue
                args = [a.arg for a in item.args.args]
                if len(args) < 3:
                    continue  # manager get_queryset(self)
                scoped.setdefault(node.name, f"{path.relative_to(ROOT)}:{item.lineno}")
                variants.setdefault(args[2], []).append(node.name)

    if "--json" in sys.argv:
        print(json.dumps(sorted(scoped)))
        return

    print(f"{len(scoped)} classes define a row-security get_queryset\n")
    for name in sorted(scoped):
        print(f"  {name:36} {scoped[name]}")
    print("\nthird-parameter name -> class count:")
    for name, classes in sorted(variants.items(), key=lambda kv: -len(kv[1])):
        print(f"  {name:10} {len(classes)}")


if __name__ == "__main__":
    main()
