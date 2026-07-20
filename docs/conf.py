import os
import sys

# Ensure our local source directory is first in path so we use the local version of sphinx-asciidoctrine
sys.path.insert(0, os.path.abspath("../src"))

from importlib.metadata import version as get_version

# -- Project information -----------------------------------------------------

project = "Sphinx AsciiDoctrine"
copyright = "2026, Michael R. Bernstein"
author = "Michael R. Bernstein"
try:
    release = get_version("sphinx-asciidoctrine")
except Exception:
    release = "0.1.0a1"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx_rtd_theme",
    "sphinx_asciidoctrine",
    "sphinx.ext.githubpages",
    "autodoc2",
]

autoclass_content = "both"

autodoc2_packages = [
    "../src/sphinx_asciidoctrine",
]

autodoc2_docstring_parser_regexes = [
    (r".*", "sphinx_asciidoctrine.parser"),
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]

# -- Extension configuration --------------------------------------------------

# Our parser registers .adoc and .asciidoc suffixes automatically via setup()
