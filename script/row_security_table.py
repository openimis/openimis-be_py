"""Table of openIMIS models vs row-security rules, for review.

Columns:
  own rule   -- the model declares get_queryset itself
  anchors    -- FK/O2O/M2M fields that could carry a scope: either to a known
                scope anchor (Location, HealthFacility, Insuree, ...) or to a
                model that is itself already scoped
  GQL        -- a DjangoObjectType maps this model
  hook       -- that type defines get_queryset
"""
import ast
import os
import pathlib
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openIMIS.settings")
django.setup()

from django.apps import apps                      # noqa: E402
from django.conf import settings                  # noqa: E402

ROOT = pathlib.Path("/mnt/data/Development/openimis-dev-tools/backend-packages")

# Models that define a location/facility/ownership boundary.
ANCHORS = {
    "Location", "HealthFacility", "Insuree", "Family", "PolicyHolder",
    "InteractiveUser", "Officer", "ClaimAdmin", "User", "UserDistrict",
    "OfficerVillage", "Individual", "Group",
}


def gql_type_index():
    """model name -> (type name, has get_queryset)."""
    index = {}
    for path in ROOT.rglob("*.py"):
        p = str(path)
        if "/tests/" in p or "/migrations/" in p:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            bases = {getattr(b, "attr", getattr(b, "id", "")) for b in cls.bases}
            if not any("ObjectType" in b for b in bases):
                continue
            model_name = None
            for item in cls.body:
                if isinstance(item, ast.ClassDef) and item.name == "Meta":
                    for sub in item.body:
                        if isinstance(sub, ast.Assign) and any(
                            getattr(t, "id", "") == "model" for t in sub.targets
                        ):
                            model_name = getattr(sub.value, "id", None) or getattr(
                                sub.value, "attr", None
                            )
            has_hook = any(
                isinstance(i, (ast.FunctionDef, ast.AsyncFunctionDef))
                and i.name == "get_queryset"
                for i in cls.body
            )
            if model_name:
                prev = index.get(model_name)
                # prefer a type that has the hook, if several map the model
                if prev is None or (has_hook and not prev[1]):
                    index[model_name] = (cls.name, has_hook)
    return index


def main():
    own_apps = set(settings.OPENIMIS_APPS)
    models = [
        m for m in apps.get_models()
        if m._meta.app_label in own_apps and not m.__name__.startswith("Historical")
    ]
    # A rule is either hand-written on the model or declared as a row_scope;
    # counting only __dict__ missed every declarative one.
    scoped = {
        m.__name__
        for m in models
        if "get_queryset" in m.__dict__ or getattr(m, "row_scope", None) is not None
    }
    gql = gql_type_index()

    # Audit stamps, present on every HistoryBusinessModel. They record who
    # touched a row, not which location it belongs to, so they are not a scope.
    AUDIT_FIELDS = {"user_created", "user_updated", "user_deleted"}

    rows = []
    for m in sorted(models, key=lambda x: x._meta.label):
        anchors, generic = [], []
        for f in m._meta.get_fields():
            if f.__class__.__name__ == "GenericForeignKey":
                generic.append(f.name)
                continue
            if not getattr(f, "many_to_one", False) and not getattr(f, "one_to_one", False) \
                    and not getattr(f, "many_to_many", False):
                continue
            if f.name in AUDIT_FIELDS:
                continue
            rel = getattr(f, "related_model", None)
            if rel is None or rel is m:
                continue
            if rel.__name__ in ANCHORS or rel.__name__ in scoped:
                anchors.append(f"{f.name}->{rel.__name__}")
        t_name, t_hook = gql.get(m.__name__, (None, False))
        rows.append({
            "label": m._meta.label,
            "own": m.__name__ in scoped,
            "anchors": anchors,
            "generic": generic,
            "gql": t_name,
            "hook": t_hook,
        })

    def table(subset):
        print("| Model | own rule | GQL type | type hook | could scope via |")
        print("|---|---|---|---|---|")
        for r in subset:
            parts = list(r["anchors"][:3])
            if len(r["anchors"]) > 3:
                parts.append(f"(+{len(r['anchors']) - 3})")
            for name in r["generic"]:
                parts.append(f"{name} (generic FK)")
            anchors = ", ".join(parts) or "—"
            print(
                f"| {r['label']} | {'yes' if r['own'] else '**no**'} "
                f"| {r['gql'] or '—'} | {'yes' if r['hook'] else '—'} | {anchors} |"
            )

    have = [r for r in rows if r["own"]]
    gap = [r for r in rows if not r["own"] and (r["anchors"] or r["generic"])]
    flat = [r for r in rows if not r["own"] and not r["anchors"] and not r["generic"]]

    # Priority within the gap: is it reachable over GraphQL, and is anything
    # filtering it there today?
    p1 = sorted([r for r in gap if r["gql"] and not r["hook"]], key=lambda r: r["label"])
    p2 = sorted([r for r in gap if r["gql"] and r["hook"]], key=lambda r: r["label"])
    p3 = sorted([r for r in gap if not r["gql"]], key=lambda r: r["label"])

    print(f"# Row-security review — {len(rows)} openIMIS models")
    print("\nsimple-history shadow models excluded. `could scope via` lists FK/O2O/M2M")
    print("fields pointing at a scope anchor (Location, HealthFacility, Insuree, Family,")
    print("PolicyHolder, Officer, User, Individual, Group) or at an already-scoped model —")
    print("i.e. a restriction is *expressible*. Whether it is *needed* is a product call.\n")
    print(f"| group | count |")
    print(f"|---|---|")
    print(f"| declares its own rule | {len(have)} |")
    print(f"| no rule — on GraphQL, nothing filtering it | **{len(p1)}** |")
    print(f"| no rule — on GraphQL, type hook filters it (other APIs unprotected) | {len(p2)} |")
    print(f"| no rule — not on GraphQL (REST/FHIR/services only) | {len(p3)} |")
    print(f"| no rule, nothing to scope by (reference/config) | {len(flat)} |")

    print("\n\n## 1. No rule, exposed on GraphQL, nothing filtering it")
    print("\nHighest priority: readable over the API with no restriction anywhere.\n")
    table(p1)

    print("\n## 2. No rule, but the graphene type filters it")
    print("\nScoped on GraphQL only. The rule belongs on the model so REST and FHIR")
    print("get it too — this is the 15-hook migration list.\n")
    table(p2)

    print("\n## 3. No rule, not exposed on GraphQL")
    print("\nReachable through REST/FHIR or service code only.\n")
    table(p3)

    print("\n## 4. Declares its own rule (for confirmation)\n")
    table(have)

    print("\n## 5. No rule, nothing to scope by\n")
    print("Reference and configuration tables.\n")
    table(flat)


if __name__ == "__main__":
    main()
