#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools_scm

extensions = [
    'sphinx.ext.autodoc',
]

# General information about the project.
project = 'tempora'
copyright = '2005, 2007-2015 Jason R. Coombs'

# The short X.Y version.
version = setuptools_scm.get_version()
# The full version, including alpha/beta/rc tags.
release = version

master_doc = 'index'
