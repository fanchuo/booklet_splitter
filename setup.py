#!/usr/bin/env python

from setuptools import setup, find_namespace_packages
from os import getenv
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="booklet_splitter",
    version=getenv("VERSION"),
    description="Make booklets out of pdf files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="François Sécherre",
    author_email="secherre.nospam@gmail.com",
    url="https://github.com/fanchuo/booklet_splitter",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "pypdf==6.6.2",
        "click==8.3.1",
    ],
    scripts=["scripts/pdf_splitter"],
    extras_require={
        "tests": [
            "coverage==7.13.1",
            "flake8==7.3.0",
            "black==26.1.0",
            "twine==6.2.0",
            "pre_commit==4.5.1",
            "mypy==1.19.1",
            "pytest==9.0.2",
            "pytest-cov==7.0.0",
        ]
    },
    classifiers=["Programming Language :: Python :: 3"],
)
