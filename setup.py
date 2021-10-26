#!/usr/bin/env python

from setuptools import setup, find_namespace_packages

setup(name='booklet_splitter',
      version='1.0',
      description='Make booklets out of pdf files',
      author='François Sécherre',
      author_email='secherre.nospam@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      package_dir = {'': 'src'},
      packages=find_namespace_packages(where='src'),
      install_requires=[
        'PyPDF2==1.26.0',
      ],
      scripts=['scripts/booklets'],
     )