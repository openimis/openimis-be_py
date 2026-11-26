#!/usr/bin/env bash
# Refresh the English catalogue of a backend module. Run from the module repository
# root (the directory with setup.py).
#
# The catalogue lives inside the Python package (<package>/locale/), so pip installs
# ship it; setup.py declares package_data={'<package>': ['locale/*/LC_MESSAGES/*.po']}.
# A module still on the legacy root-level locale/ keeps using it until it moves.
set -e
if [ -n "$1" ]; then
  LOCALE_DIR="$1/locale"
elif [ -d locale ]; then
  LOCALE_DIR="locale"
  echo "warning: root-level locale/ is not shipped by pip; move it into the package" >&2
else
  PACKAGE=$(for d in */; do d=${d%/}; [ -f "$d/__init__.py" ] && [ -f "$d/apps.py" ] && echo "$d"; done)
  if [ "$(echo "$PACKAGE" | wc -w)" != "1" ]; then
    echo "Cannot tell the package among: $PACKAGE. Usage: $0 <package>" >&2
    exit 1
  fi
  LOCALE_DIR="$PACKAGE/locale"
fi
PO="$LOCALE_DIR/en/LC_MESSAGES/django.po"
mkdir -p "$(dirname "$PO")"
# --join-existing requires the file to be there
[ -f "$PO" ] || touch "$PO"
find . -name '*.py' -not -path './build/*' -not -path './.*' -print0 | xargs -0 xgettext --from-code utf-8 --join-existing --language=Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --keyword=ugettext_noop --keyword=ugettext_lazy --keyword=ungettext_lazy:1,2 --keyword=pgettext:1c,2 --keyword=npgettext:1c,2,3 --keyword=pgettext_lazy:1c,2 --keyword=npgettext_lazy:1c,2,3 -o "$PO"

# xgettext forces a content-type charset=CHARSET and has no option to override it in the command line, so fix it:
sed -i -e 's/charset=CHARSET/charset=UTF-8/' "$PO"
echo "Updated $PO"
