#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='yalzma',
    version='0.0.1',
    description='Yet Another LZMA Python wrapper',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['doc', 'tests*']),
)
