# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Mock modules -------------------------------------------------------------

from mock import Mock as MagicMock


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return Mock()


MOCK_MODULES = ['numpy', 'matplotlib', 'matplotlib.pyplot', 'pandas', 'netCDF4',
                'pytest', 'pyyaml',
                ]

# -- Import _hydrobricks -----------------------------------------------------

import _hydrobricks


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

sys.path.insert(0, os.path.abspath(r'.'))
BASE_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "python", "src"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "python", "src", "hydrobricks"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "core", "src"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "core", "bindings"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'hydrobricks'
copyright = '2022, Pascal Horton'
author = 'Pascal Horton'
release = '0.0.7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
