#!/usr/bin/env python3
"""Report-only translation check for an openIMIS backend module.

Run from anywhere, pointing at the module repository (the directory with setup.py):

    python script/i18n_check.py path/to/openimis-be-<module>_py [--package <name>] [--strict]

It checks that:
  * the English catalogue (<package>/locale/en/LC_MESSAGES/django.po) has every msgid
    the code marks for translation (same xgettext keywords as script/gettext.sh);
  * locale/ lives inside the Python package and ends up in the built wheel, so pip
    installs ship the catalogue (the assembly compiles it with compilemessages);
  * every English msgid exists in the Lokalise backend project, when LOKALISE_APIKEY
    is set (read-only token is enough; skipped otherwise).

Findings are printed as GitHub annotations when GITHUB_ACTIONS is set. The exit code
is 0 unless --strict is given and there is at least one error.
Requires GNU gettext (xgettext) and, for the wheel check, pip. Standard library only.
"""
import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

LOKALISE_PROJECT = "539322845d9e1249837338.65707886"
LOKALISE_API = "https://api.lokalise.com/api2"
CATALOGUE = os.path.join("locale", "en", "LC_MESSAGES", "django.po")
# Same keywords as script/gettext.sh, on top of the xgettext Python defaults (gettext, _, ngettext, ...).
XGETTEXT_KEYWORDS = [
    "gettext_noop", "gettext_lazy", "ngettext_lazy:1,2", "ugettext_noop", "ugettext_lazy",
    "ungettext_lazy:1,2", "pgettext:1c,2", "npgettext:1c,2,3", "pgettext_lazy:1c,2", "npgettext_lazy:1c,2,3",
]
KEY_LIKE = re.compile(r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_-]+)+$")  # e.g. claim.validation.foo
SKIP_DIRS = {".git", ".github", "build", "dist", "node_modules", "__pycache__", ".venv", "venv", ".worktrees"}


class Report:
    def __init__(self, root):
        self.root = root
        self.counts = {"error": 0, "warning": 0, "notice": 0}
        self.github = bool(os.environ.get("GITHUB_ACTIONS"))

    def add(self, level, message, path=None, line=None):
        self.counts[level] += 1
        rel = os.path.relpath(path, self.root) if path else None
        if self.github:
            props = []
            if rel:
                props.append(f"file={rel}")
                if line:
                    props.append(f"line={line}")
            # Annotation messages must stay on one line.
            text = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::{level} {','.join(props)}::{text}" if props else f"::{level}::{text}")
        else:
            where = f"{rel}:{line}: " if rel and line else f"{rel}: " if rel else ""
            print(f"{level.upper():8} {where}{message}")


# --------------------------------------------------------------------------- .po parsing

def _unquote(token):
    return ast.literal_eval(token) if token.startswith('"') else ""


def parse_po(path):
    """Return {(msgctxt, msgid): {"msgstr": str, "line": int, "refs": [..], "fuzzy": bool}}.

    Obsolete entries (#~) and the header are left out. Enough for catalogues written
    by xgettext/msgmerge; not a general-purpose .po parser.
    """
    entries = {}
    current, field, refs, flags = {}, None, [], []

    def flush():
        nonlocal current, refs, flags
        if "msgid" in current and current["msgid"]:
            msgstrs = [v for k, v in current.items() if k.startswith("msgstr")]
            entries[(current.get("msgctxt"), current["msgid"])] = {
                "msgstr": msgstrs[0] if msgstrs else "",
                "all_msgstr": msgstrs,
                "line": current.get("_line"),
                "refs": refs,
                "fuzzy": "fuzzy" in flags,
            }
        current, refs, flags = {}, [], []

    with open(path, encoding="utf-8") as po:
        for number, raw in enumerate(po, 1):
            line = raw.strip()
            if not line:
                flush()
                field = None
            elif line.startswith("#~"):
                continue
            elif line.startswith("#:"):
                refs.extend(line[2:].split())
            elif line.startswith("#,"):
                flags.extend(f.strip() for f in line[2:].split(","))
            elif line.startswith("#"):
                continue
            elif line.startswith('"'):
                if field:
                    current[field] += _unquote(line)
            else:
                keyword, _, value = line.partition(" ")
                if keyword in ("msgctxt", "msgid") and "msgid" in current:
                    flush()  # a new entry without the usual blank line before it
                field = keyword
                current[field] = _unquote(value.strip())
                if keyword == "msgid":
                    current["_line"] = number
    flush()
    return entries


# --------------------------------------------------------------------------- module layout

def find_package(root, explicit):
    if explicit:
        return explicit
    candidates = [
        d for d in sorted(os.listdir(root))
        if d not in SKIP_DIRS and os.path.isfile(os.path.join(root, d, "__init__.py"))
        and os.path.isfile(os.path.join(root, d, "apps.py"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    repo = os.path.basename(os.path.abspath(root))
    match = re.match(r"^openimis-be-(.+)_py$", repo)
    if match and match.group(1) in candidates:
        return match.group(1)
    sys.exit(f"Cannot tell which package to check among {candidates or 'none'}: pass --package")


def python_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if name.endswith(".py"):
                yield os.path.relpath(os.path.join(dirpath, name), root)


def extract_msgids(root, tmp):
    if not shutil.which("xgettext"):
        sys.exit("xgettext not found: install GNU gettext")
    files = list(python_files(root))
    out = os.path.join(tmp, "extracted.po")
    if not files:
        return {}
    cmd = ["xgettext", "--from-code=utf-8", "--language=Python", "--no-wrap", "-o", out, "-f", "-"]
    cmd += [f"--keyword={k}" for k in XGETTEXT_KEYWORDS]
    subprocess.run(cmd, cwd=root, input="\n".join(files), text=True, check=True, capture_output=True)
    return parse_po(out) if os.path.isfile(out) else {}


def first_ref(root, refs):
    for ref in refs:
        path, _, line = ref.rpartition(":")
        if path and line.isdigit():
            return os.path.join(root, path), int(line)
    return None, None


# --------------------------------------------------------------------------- checks

def check_layout(report, root, package):
    inside = os.path.join(root, package, CATALOGUE)
    legacy = os.path.join(root, CATALOGUE)
    if os.path.isfile(inside):
        return inside
    if os.path.isfile(legacy):
        report.add(
            "warning",
            f"locale/ sits next to setup.py, outside the '{package}' package: pip installs ship no "
            f"catalogue and the API answers with raw msgids. Move it to {package}/locale/ and declare "
            f"package_data={{'{package}': ['locale/*/LC_MESSAGES/*.po']}} in setup.py.",
            legacy, 1,
        )
        return legacy
    return None


def check_catalogue(report, root, catalogue, extracted):
    committed = parse_po(catalogue) if catalogue else {}
    if not catalogue and extracted:
        report.add("error", f"{len(extracted)} msgid(s) marked for translation but no en catalogue "
                            f"({CATALOGUE}): run script/gettext.sh from the package directory.")
    if catalogue:
        for key, entry in sorted(extracted.items(), key=lambda kv: kv[0][1]):
            if key not in committed:
                path, line = first_ref(root, entry["refs"])
                ctx = f" (context '{key[0]}')" if key[0] else ""
                report.add("error", f"msgid '{key[1]}'{ctx} is missing from the en catalogue.", path, line)
        for key, entry in sorted(committed.items(), key=lambda kv: kv[0][1]):
            if key not in extracted:
                report.add("notice", f"msgid '{key[1]}' is no longer used in the code (obsolete).",
                           catalogue, entry["line"])
            elif not all(entry["all_msgstr"]) and KEY_LIKE.match(key[1]):
                # A sentence msgid falls back to itself; a key-like one reaches the user as is.
                report.add("warning", f"msgid '{key[1]}' is a key with no English text (empty msgstr).",
                           catalogue, entry["line"])
            elif entry["fuzzy"]:
                report.add("warning", f"msgid '{key[1]}' is marked fuzzy and is ignored at runtime.",
                           catalogue, entry["line"])
    return committed


def check_wheel(report, root, package, tmp):
    if not os.path.isfile(os.path.join(root, "setup.py")) and not os.path.isfile(
        os.path.join(root, "pyproject.toml")
    ):
        return
    dist = os.path.join(tmp, "wheel")
    build = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "-q", "-w", dist, root],
        capture_output=True, text=True,
    )
    wheels = [f for f in os.listdir(dist) if f.endswith(".whl")] if os.path.isdir(dist) else []
    if build.returncode or not wheels:
        report.add("warning", f"Could not build the wheel to check what it ships: {build.stderr.strip()[-300:]}")
        return
    with zipfile.ZipFile(os.path.join(dist, wheels[0])) as wheel:
        shipped = [n for n in wheel.namelist() if re.match(rf"^{re.escape(package)}/locale/.+\.po$", n)]
    if not shipped:
        report.add(
            "warning",
            f"The built wheel ships no {package}/locale/**/*.po: declare "
            f"package_data={{'{package}': ['locale/*/LC_MESSAGES/*.po']}} in setup.py.",
            os.path.join(root, "setup.py"), 1,
        )


def lokalise_keys(token):
    keys, cursor = set(), None
    while True:
        query = {"limit": 500, "pagination": "cursor"}
        if cursor:
            query["cursor"] = cursor
        request = urllib.request.Request(
            f"{LOKALISE_API}/projects/{LOKALISE_PROJECT}/keys?{urllib.parse.urlencode(query)}",
            headers={"x-api-token": token, "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
            cursor = response.headers.get("X-Pagination-Next-Cursor")
        for key in payload.get("keys", []):
            names = key.get("key_name")
            keys.update(names.values() if isinstance(names, dict) else [names])
        if not cursor or not payload.get("keys"):
            return keys


def check_lokalise(report, catalogue, committed):
    token = os.environ.get("LOKALISE_APIKEY")
    if not token:
        report.add("warning", "LOKALISE_APIKEY is not set: Lokalise check skipped.")
        return
    try:
        known = lokalise_keys(token)
    except (urllib.error.URLError, ValueError) as exc:
        # Never echo the request: the token is in its headers.
        report.add("warning", f"Lokalise check skipped, the API call failed: {getattr(exc, 'code', '')} "
                              f"{getattr(exc, 'reason', type(exc).__name__)}")
        return
    for (_, msgid), entry in sorted(committed.items(), key=lambda kv: kv[0][1]):
        if msgid not in known:
            report.add("warning", f"msgid '{msgid}' is not in Lokalise: upload the en catalogue "
                                  f"(script/lokalise-upload.py) so it gets translated.", catalogue, entry["line"])


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("module", help="module repository root (the directory with setup.py)")
    parser.add_argument("--package", help="Python package to check (default: guessed from the layout)")
    parser.add_argument("--strict", action="store_true", help="exit 1 when there is at least one error")
    parser.add_argument("--no-wheel", action="store_true", help="skip building the wheel")
    parser.add_argument("--no-lokalise", action="store_true", help="skip the Lokalise check")
    args = parser.parse_args()

    root = os.path.abspath(args.module)
    package = find_package(root, args.package)
    report = Report(root)
    with tempfile.TemporaryDirectory() as tmp:
        extracted = extract_msgids(root, tmp)
        catalogue = check_layout(report, root, package)
        committed = check_catalogue(report, root, catalogue, extracted)
        if not args.no_wheel:
            check_wheel(report, root, package, tmp)
    if not args.no_lokalise and committed:
        check_lokalise(report, catalogue, committed)

    summary = (f"i18n check of '{package}': {len(extracted)} msgid(s) in the code, {len(committed)} in the "
               f"en catalogue; {report.counts['error']} error(s), {report.counts['warning']} warning(s), "
               f"{report.counts['notice']} notice(s).")
    print(summary)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as out:
            out.write(f"### Translations\n\n{summary}\n")
    return 1 if args.strict and report.counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
