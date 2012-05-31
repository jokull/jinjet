#!/usr/bin/env python
# encoding=utf-8

from setuptools import setup

requires = ['jinja2', 'babel', 'watchdog']

try:
    import argparse
except ImportError:
    requires.append('argparse')

entry_points = {
    'console_scripts': [
        'jinjet = jinjet:main',
   ]
}

setup(
    name = 'jinjet',
    version = '0.1',
    url='https://github.com/jokull/jinjet',
    license='BSD',
    author = u'Jökull Sólberg Auðunsson',
    author_email = 'jokull@solberg.is',
    description = 'A mini static generator with Jinja2/Babel integration.',
    long_description=open('README.md').read(),
    py_modules=['jinjet'],
    zip_safe=False,
    include_package_data=True,
    install_requires = requires,
    entry_points = entry_points,
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
