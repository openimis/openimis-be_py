#!/usr/bin/env bash
mkdir -p locale/en/LC_MESSAGES
# --join-existing requires the file to be there
if [ ! -f locale/en/LC_MESSAGES/django.po ]; then
  touch locale/en/LC_MESSAGES/django.po
fi
if [ ! -f locale/__init__.py ]; then
  touch locale/__init__.py # necessary to let python package this folder in the pypi module
fi
find . -name '*.py' -print0 | xargs -0 xgettext --from-code utf-8 --join-existing --language=Python --language=Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --keyword=ugettext_noop --keyword=ugettext_lazy --keyword=ungettext_lazy:1,2 --keyword=pgettext:1c,2 --keyword=npgettext:1c,2,3 --keyword=pgettext_lazy:1c,2 --keyword=npgettext_lazy:1c,2,3 -o locale/en/LC_MESSAGES/django.po

# xgettext forces a content-type charset=CHARSET and has no option to override it in the command line, so fix it:
sed -e 's/charset=CHARSET/charset=UTF-8/' < locale/en/LC_MESSAGES/django.po > locale/en/LC_MESSAGES/django.po.tmp
mv locale/en/LC_MESSAGES/django.po.tmp locale/en/LC_MESSAGES/django.po