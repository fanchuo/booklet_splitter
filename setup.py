#!/usr/bin/env python

from setuptools import setup, find_namespace_packages
from os import getenv
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="booklet_splitter",
    version=getenv('VERSION', 'dev'),
    description="Make booklets out of pdf files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="François Sécherre",
    author_email="secherre.nospam@gmail.com",
    url="https://github.com/fanchuo/booklet_splitter",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "PyPDF2==1.26.0",
        "click==8.0.3",
    ],
    scripts=["scripts/booklets"],
    extras_require={
        "tests": [
            "coverage==6.0.2",
            "flake8==4.0.1",
            "black==21.9b0",
            "twine==3.4.2",
        ],
    },
    test_suite="tests",
    classifiers=["Programming Language :: Python :: 3"],
)
