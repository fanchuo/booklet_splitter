#!/usr/bin/env python

from setuptools import setup, find_namespace_packages

setup(
    name="booklet_splitter",
    version="1.0",
    description="Make booklets out of pdf files",
    author="François Sécherre",
    author_email="secherre.nospam@gmail.com",
    url="https://github.com/fanchuo/booklet_splitter",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "PyPDF2==1.26.0",
    ],
    scripts=["scripts/booklets"],
    extras_require={
        "tests": [
            "coverage==6.0.2",
            "flake8==4.0.1",
            "black==21.9b0",
        ],
    },
    test_suite="tests",
    classifiers=["Programming Language :: Python :: 3"],
)
