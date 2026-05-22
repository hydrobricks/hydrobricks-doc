# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Mock modules -------------------------------------------------------------
# Use autodoc_mock_imports (set below) instead of manual sys.modules patching
# so that Sphinx 9.x does not attempt Path(Mock()) and raise TypeError.


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

sys.path.insert(0, os.path.abspath(r'.'))
BASE_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "python", "src"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "python", "src", "hydrobricks"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "python", "src", "preprocessing"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "core", "src"))
sys.path.insert(0, os.path.join(BASE_PATH, "_deps", "hydrobricks", "core", "bindings"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'hydrobricks'
copyright = '2022, Pascal Horton'
author = 'Pascal Horton'
release = '0.8.7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinxcontrib.bibtex',
]

bibtex_bibfiles = ['doc/references.bib']
bibtex_default_style = 'plain'
bibtex_reference_style = 'author_year'

autosummary_generate = True

autodoc_mock_imports = [
    'numpy', 'matplotlib', 'matplotlib.pyplot', 'pandas', 'netCDF4',
    'pytest', 'pyyaml', 'yaml', 'HydroErr', '_hydrobricks',
    'hydrobricks._hydrobricks',  # C++ extension: not available without building
    'cftime',  # direct import in forcing.py (num2date)
    'scipy', 'scipy.ndimage',  # real scipy has broken internal import on this machine
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]