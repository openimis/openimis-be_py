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

