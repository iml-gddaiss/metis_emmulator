import os
from setuptools import find_packages, setup

VERSION = "0.0.1"


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="mitis",
    version=VERSION,
    author="JeromeJGuay,",
    author_email="jerome.guay@dfo-mpo.gc.ca",
    description="""Oceanographic instrument emulator""",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    classifiers=["Programming Language :: Python :: 3"],
    python_requires="~=3.9",
    entry_points={"console_scripts": ["mitis=mitis_emulator.main:root", ]},
)
