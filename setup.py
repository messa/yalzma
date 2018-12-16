#!/usr/bin/env python3

from pathlib import Path
import re
from setuptools import setup, find_packages

init_file = Path(__file__).parent / 'yalzma/__init__.py'
version, = re.search(r"^__version__ = '(.*)'$", init_file.read_text(), re.M).groups()

setup(
    name='yalzma',
    version=version,
    description='Yet Another LZMA Python wrapper',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['doc', 'tests*']),
)
