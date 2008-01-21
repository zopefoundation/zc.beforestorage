from setuptools import setup, find_packages

entry_points = """
"""

setup(
    name = 'zc.beforestorage',
    version = '0.1',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = '',
    license = 'ZPL 2.1',
    
    packages = find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = ['ZODB3', 'setuptools'],
    zip_safe = False,
    entry_points=entry_points,
    )
