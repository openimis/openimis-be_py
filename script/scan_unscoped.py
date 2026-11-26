"""Find GraphQL read fields that are NOT covered by row security.

Two scoping mechanisms exist, and only one is automatic:

* `DjangoObjectType.get_queryset(cls, queryset, info)` -- graphene-django's
  hook. `DjangoConnectionField.resolve_queryset` calls
  `connection._meta.node.get_queryset(queryset, info)` on whatever the resolver
  returned (graphene_django/fields.py:131), and DjangoFilterConnectionField
  inherits it. So a *connection* field whose type defines the hook is scoped
  even if its resolver returns a bare `Model.objects`.
* `Model.get_queryset(cls, queryset, user)` -- openIMIS's own classmethod. Never
  called by anything automatically; a resolver must invoke it.

So a field is at risk when it is NOT a connection field (plain graphene.Field /
graphene.List, where the type hook never runs) AND neither its resolver nor its
type scopes explicitly.
"""
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path("/mnt/data/Development/openimis-dev-tools/backend-packages")
FILES = ("schema.py", "gql_queries.py", "query.py", "queries.py")

CONNECTION = re.compile(r"ConnectionField|DjangoFilterConnectionField")
SCOPED = ("get_queryset", "filter_queryset", "user_business_access", "build_user_location_filter_query")
OBJECTS = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\.objects\b")


def secured_models():
    """Models whose get_queryset takes a context arg (arity >= 3)."""
    found = set()
    for path in ROOT.rglob("*.py"):
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
            if node.name.endswith("GQLType") or node.name.endswith("Type"):
                continue  # graphene types, handled by the automatic hook
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and item.name == "get_queryset" \
                        and len(item.args.args) >= 3:
                    found.add(node.name)
    return found


def gql_types_with_hook():
    hooked = set()
    for path in ROOT.rglob("*.py"):
        if "/tests/" in str(path) or "/migrations/" in str(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef))
                and i.name == "get_queryset"
                for i in node.body
            ):
                hooked.add(node.name)
    return hooked


def main():
    secured = secured_models()
    hooked = gql_types_with_hook()
    rows = []

    for path in sorted(ROOT.rglob("*.py")):
        p = str(path)
        if "/tests/" in p or "/migrations/" in p or path.name not in FILES:
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        lines = source.splitlines()

        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            # Field declarations in this class: name -> source text.
            fields = {}
            for item in cls.body:
                if isinstance(item, ast.Assign) and len(item.targets) == 1 \
                        and isinstance(item.targets[0], ast.Name):
                    fields[item.targets[0].id] = "\n".join(
                        lines[item.lineno - 1 : item.end_lineno]
                    )
            for item in cls.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not item.name.startswith("resolve_"):
                    continue
                field_name = item.name[len("resolve_") :]
                decl = fields.get(field_name, "")
                body = "\n".join(lines[item.lineno - 1 : item.end_lineno])

                hits = sorted(set(OBJECTS.findall(body)) & secured)
                if not hits:
                    continue
                if any(m in body for m in SCOPED):
                    continue                      # scopes itself
                if CONNECTION.search(decl):
                    # Covered by the type hook -- but only if the type has one.
                    types = re.findall(r"\b([A-Z][A-Za-z0-9_]*(?:GQLType|Type))\b", decl)
                    if any(t in hooked for t in types):
                        continue
                    kind = "CONNECTION, type has NO hook"
                elif decl:
                    kind = "plain field/list"
                else:
                    kind = "no field decl found (nested/related resolver)"

                rows.append(
                    (str(path.relative_to(ROOT)), item.lineno, item.name, hits, kind)
                )

    print(f"{len(rows)} read fields are not covered by either mechanism\n")
    by_kind = {}
    for row in rows:
        by_kind.setdefault(row[4], []).append(row)
    for kind in sorted(by_kind):
        print(f"\n## {kind}  ({len(by_kind[kind])})")
        for rel, lineno, name, hits, _ in by_kind[kind]:
            print(f"  {rel}:{lineno}  {name}()  ->  {', '.join(hits)}")


if __name__ == "__main__":
    main()
