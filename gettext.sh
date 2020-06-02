#!/usr/bin/env bash
mkdir -p locale/en/LC_MESSAGES
if [ ! -f locale/__init__.py ]; then
  touch locale/__init__.py # necessary to let python package this folder in the pypi module
fi
if [ ! -f locale/en/LC_MESSAGES/django.po ]; then
  cat > locale/en/LC_MESSAGES/django.po <<EOT
# OpenIMIS translations file
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2020-05-27 22:47+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
EOT
fi
find . -name '*.py' | xargs xgettext --language=Python --language=Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --keyword=ugettext_noop --keyword=ugettext_lazy --keyword=ungettext_lazy:1,2 --keyword=pgettext:1c,2 --keyword=npgettext:1c,2,3 --keyword=pgettext_lazy:1c,2 --keyword=npgettext_lazy:1c,2,3 -o locale/en/LC_MESSAGES/django.po

