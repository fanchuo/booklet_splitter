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
        "pypdf>=6.7.0,<7",
        "click>=8.3.0,<9",
    ],
    scripts=["scripts/pdf_splitter"],
    extras_require={
        "tests": [
            "coverage>=7.13.1,<8",
            "flake8>=7.3.0,<8",
            "black>=26.1.0,<27",
            "twine>=6.2.0,<7",
            "pre_commit>=4.5.1,<5",
            "mypy>=1.19.1,<2",
            "pytest>=9.0.2,<10",
            "pytest-cov>=7.0.0,<8",
        ]
    },
    classifiers=["Programming Language :: Python :: 3"],
)
