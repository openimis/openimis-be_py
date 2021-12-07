import os


def get_skeleton_setup(module_name, author, author_email):
    return \
        F"import os{os.linesep}" \
        F"from setuptools import find_packages, setup{os.linesep}" \
        F"{os.linesep}" \
        F"with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:{os.linesep}" \
        F"    README = readme.read(){os.linesep}" \
        F"{os.linesep}" \
        F"# allow setup.py to be run from any path{os.linesep}" \
        F"os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))){os.linesep}" \
        F"{os.linesep}" \
        F"setup({os.linesep}" \
        F"    name='openimis-be-{module_name}',{os.linesep}" \
        F"    version='1.0.0',{os.linesep}" \
        F"    packages=find_packages(),{os.linesep}" \
        F"    include_package_data=True,{os.linesep}" \
        F"    license='GNU AGPL v3',{os.linesep}" \
        F"    description='The openIMIS Backend {module_name} reference module.',{os.linesep}" \
        F"    long_description=README,{os.linesep}" \
        F"    long_description_content_type='text/markdown',{os.linesep}" \
        F"    author='{author}',{os.linesep}" \
        F"    author_email='{author_email}',{os.linesep}" \
        F"    install_requires=[ {os.linesep}" \
        F"        'django',{os.linesep}" \
        F"        'django-db-signals',{os.linesep}" \
        F"        'openimis-be-core',{os.linesep}" \
        F"        'openimis-be-core',{os.linesep}" \
        F"    ],{os.linesep}" \
        F"    classifiers=[{os.linesep}" \
        F"        'Environment :: Web Environment',{os.linesep}" \
        F"        'Framework :: Django',{os.linesep}" \
        F"        'Framework :: Django :: 2.1',{os.linesep}" \
        F"        'Intended Audience :: Developers',{os.linesep}" \
        F"        'License :: OSI Approved :: GNU Affero General Public License v3',{os.linesep}" \
        F"        'Programming Language :: Python',{os.linesep}" \
        F"        'Programming Language :: Python :: 3.6',{os.linesep}" \
        F"        'Programming Language :: Python :: 3.7',{os.linesep}" \
        F"    ],{os.linesep}" \
        F"){os.linesep}" \
        F"{os.linesep}"


def get_skeleton_urls():
    return \
        F"urlpatterns = []{os.linesep}" \
        F"{os.linesep}"


def get_skeleton_readme(module_name):
    return \
        F"# openIMIS Backend {module_name} reference module{os.linesep}" \
        F"{os.linesep}"


def get_skeleton_yaml_ci_run():
    return \
        F"name: Automated CI testing{os.linesep}" \
        F"# This workflow run automatically for every commit on github it checks the syntax and launch the tests.{os.linesep}" \
        F"# | grep . | uniq -c filters out empty lines and then groups consecutive lines together with the number of occurrences{os.linesep}" \
        F"on:{os.linesep}" \
        F"  pull_request:{os.linesep}" \
        F"  workflow_dispatch::{os.linesep}" \
        F"    inputs:{os.linesep}" \
        F"      comment:{os.linesep}" \
        F"        description:{os.linesep}" \
        F"          required:{os.linesep}" \
        F"{os.linesep}" \
        F"jobs:{os.linesep}" \
        F"  run_test:{os.linesep}" \
        F"    runs-on: ubuntu-latest:{os.linesep}" \
        F"    services:{os.linesep}" \
        F"      mssql:{os.linesep}" \
        F"        image: mcr.microsoft.com/mssql/server:2017-latest:{os.linesep}" \
        F"        env:{os.linesep}" \
        F"          ACCEPT_EULA: Y{os.linesep}" \
        F"          SA_PASSWORD: GitHub999{os.linesep}" \
        F"        ports:{os.linesep}" \
        F"          - 1433:1433{os.linesep}" \
        F"        # needed because the mssql container does not provide a health check{os.linesep}" \
        F"        options: --health-interval=10s --health-timeout=3s --health-start-period=10s --health-retries=10 --health-cmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P {_strings('$SA_PASSWORD')} -Q 'SELECT 1' || exit 1'{os.linesep}" \
        F"{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \
        F"    steps:{os.linesep}" \        
        F"    steps:{os.linesep}" \        
        F"    steps:{os.linesep}" \         
        F"    steps:{os.linesep}" \         
        F"    steps:{os.linesep}" \

















def _strings(string):
    return '{'+string+'}'