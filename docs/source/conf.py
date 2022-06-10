import os
import sys
sys.path.insert(0, os.path.abspath('./../..'))

# -- Project information -----------------------------------------------------

import libmidi

project = 'libmidi'
copyright = '2022, Sebastiano Barezzi'
author = 'Sebastiano Barezzi'
release = libmidi.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

autosummary_generate = True

add_function_parentheses = True

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

# -- Setup function ----------------------------------------------------------

import types

def setup(app):
    app.connect('autodoc-skip-member', special_methods_callback)
    app.outdir = "_build/html"

def special_methods_callback(app, what, name, obj, skip, options):
    """
    https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method/35493334#35493334
    """
    if getattr(obj, '__doc__', None) and isinstance(obj, (types.FunctionType, types.MethodType)):
        return False
    else:
        return skip
