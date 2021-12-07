def get_skeleton_setup(module_name, author, author_email):
    return \
        F"import os\n" \
        F"from setuptools import find_packages, setup\n" \
        F"\n" \
        F"with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:\n" \
        F"    README = readme.read()\n" \
        F"\n" \
        F"# allow setup.py to be run from any path\n" \
        F"os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))\n" \
        F"\n" \
        F"setup(\n" \
        F"    name='openimis-be-{module_name}',\n" \
        F"    version='1.0.0',\n" \
        F"    packages=find_packages(),\n" \
        F"    include_package_data=True,\n" \
        F"    license='GNU AGPL v3',\n" \
        F"    description='The openIMIS Backend {module_name} reference module.',\n" \
        F"    long_description=README,\n" \
        F"    long_description_content_type='text/markdown',\n" \
        F"    author='{author}',\n" \
        F"    author_email='{author_email}',\n" \
        F"    install_requires=[ \n" \
        F"        'django',\n" \
        F"        'django-db-signals',\n" \
        F"        'openimis-be-core',\n" \
        F"        'openimis-be-core',\n" \
        F"    ],\n" \
        F"    classifiers=[\n" \
        F"        'Environment :: Web Environment',\n" \
        F"        'Framework :: Django',\n" \
        F"        'Framework :: Django :: 2.1',\n" \
        F"        'Intended Audience :: Developers',\n" \
        F"        'License :: OSI Approved :: GNU Affero General Public License v3',\n" \
        F"        'Programming Language :: Python',\n" \
        F"        'Programming Language :: Python :: 3.6',\n" \
        F"        'Programming Language :: Python :: 3.7',\n" \
        F"    ],\n" \
        F")\n" \
        F"\n"


def get_skeleton_urls():
    return \
        F"urlpatterns = []\n" \
        F"\n"


def get_skeleton_readme(module_name):
    return \
        F"# openIMIS Backend {module_name} reference module\n" \
        F"\n"

