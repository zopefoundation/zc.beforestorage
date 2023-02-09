##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os

from setuptools import find_packages
from setuptools import setup


name = 'zc.beforestorage'
version = '1.0'


def read(rname):
    with open(os.path.join(os.path.dirname(__file__), *rname.split('/'))) as f:
        return f.read()


entry_points = """
"""

long_description = '\n\n'.join([
    read('README.rst'),
    '.. contents::',
    read('src/zc/beforestorage/README.rst'),
    read('CHANGES.rst'),
])

tests_require = [
    'zope.testing',
    'zope.testrunner',
]

setup(
    name=name,
    version=version,
    author='Jim Fulton',
    author_email='zope-dev@zope.dev',
    description='View storage before a given time',
    long_description=long_description,
    license='ZPL 2.1',
    url='https://github.com/zopefoundation/zc.beforestorage',
    include_package_data=True,
    packages=find_packages('src'),
    namespace_packages=['zc'],
    package_dir={'': 'src'},
    python_requires='>=3.7',
    install_requires=['setuptools', 'ZODB'],
    zip_safe=False,
    entry_points=entry_points,
    tests_require=tests_require,
    extras_require=dict(test=tests_require),
    classifiers=[
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Framework :: ZODB',
    ],
)
