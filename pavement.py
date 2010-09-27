# -*- Import: -*-
from paver.easy import *
from paver.setuputils import setup
from setuptools import find_packages

try:
    # Optional tasks, only needed for development
    # -*- Optional import: -*-
    from github.tools.task import *
    import paver.doctools
    import paver.virtual
    import paver.misctasks
    ALL_TASKS_LOADED = True
except ImportError, e:
    info("some tasks could not not be imported.")
    debug(str(e))
    ALL_TASKS_LOADED = False



version = '0.50p1'

classifiers = [
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    ]

install_requires = [
    # -*- Install requires: -*-
    'setuptools',
    ]

entry_points="""
    # -*- Entry points: -*-
    """

# compatible with distutils of python 2.3+ or later
setup(
    name='terms',
    version=version,
    description='versioned terms',
    long_description=open('README.md', 'r').read(),
    classifiers=classifiers,
    keywords='python library',
    author='Christian Klein',
    author_email='c.klein@hudora.de',
    url='http://hudora.github.com/terms/',
    license='BSD',
    packages = find_packages(exclude=['bootstrap', 'pavement',]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entry_points,
    )

options(
    # -*- Paver options: -*-
    minilib=Bunch(
        extra_files=[
            # -*- Minilib extra files: -*-
            ]
        ),
    virtualenv=Bunch(
        packages_to_install=[
            # -*- Virtualenv packages to install: -*-
            'github-tools',
            "pkginfo",
            "virtualenv"],
        dest_dir='./virtual-env/',
        install_paver=True,
        script_name='bootstrap.py',
        paver_command_line=None
        ),
    )

options.setup.package_data=paver.setuputils.find_package_data(
    'terms', package='terms', only_in_packages=False)

if ALL_TASKS_LOADED:
    @task
    @needs('generate_setup', 'minilib', 'setuptools.command.sdist')
    def sdist():
        """Overrides sdist to make sure that our setup.py is generated."""
