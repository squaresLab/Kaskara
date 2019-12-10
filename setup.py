# -*- coding: utf-8 -*-
import os
import re
from glob import glob
from setuptools import setup, find_packages

MODULE_FILE = \
    os.path.join(os.path.dirname(__file__), 'python/kaskara/version.py')
VERSION_REGEX = \
    r"__version__\s+=\s+['|\"](.*)['|\"]\s*"

with open(MODULE_FILE, 'r') as f:
    contents = f.read()
    VERSION = re.search(VERSION_REGEX, contents).group(1)

setup(version=VERSION)
