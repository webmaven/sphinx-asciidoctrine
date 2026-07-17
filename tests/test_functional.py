import sys
import tempfile
from pathlib import Path

from sphinx.application import Sphinx


def test_autodoc_functional_build() -> None:
    """
    Tier 3 (Functional): Perform a full HTML build using sphinx.ext.autodoc
    to compile a Python class documented with AsciiDoc, then read and verify
    the generated HTML tags and structure.
    """
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        source_dir = tmp_dir / "source"
        build_dir = tmp_dir / "build"
        doctree_dir = tmp_dir / "doctrees"

        source_dir.mkdir()
        build_dir.mkdir()
        doctree_dir.mkdir()

        # Write mocked python module
        module_dir = source_dir / "calc"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('''
"""
= Calculator Package

This is a simple calculator package.
"""

class Calculator:
    """
    A simple calculator class.
    
    * Can add values.
    * Can subtract values.
    """
    
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract `b` from `a`.
        
        [source,python]
        ----
        c = Calculator()
        c.subtract(5.0, 3.0) # => 2.0
        ----
        """
        return a - b
''')

        sys.path.insert(0, str(source_dir))

        try:
            # Write conf.py
            (source_dir / "conf.py").write_text("""
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_asciidoctrine",
]
exclude_patterns = []
""")

            # Write index.rst (use autoclass to avoid automodule duplicates)
            (source_dir / "index.rst").write_text("""
Calculator API
==============

.. automodule:: calc

.. autoclass:: calc.Calculator
   :members:
""")

            # Run Sphinx build
            app = Sphinx(
                srcdir=str(source_dir),
                confdir=str(source_dir),
                outdir=str(build_dir),
                doctreedir=str(doctree_dir),
                buildername="html",
                status=None,
                warning=sys.stderr,
                freshenv=True,
            )
            app.build()

            # Verify HTML output
            index_html = build_dir / "index.html"
            assert index_html.exists()

            html_content = index_html.read_text()

            # Check structure elements
            assert "Calculator Package" in html_content
            assert "Calculator" in html_content
            assert "Can add values." in html_content
            assert "subtract" in html_content

        finally:
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))


def test_autodoc2_functional_build() -> None:
    """
    Tier 3 (Functional): Perform a full HTML build using sphinx-autodoc2
    to compile a Python class documented with AsciiDoc, and verify output.
    """
    try:
        import autodoc2  # noqa: F401
    except ImportError:
        # Skip if autodoc2 is not installed in the current environment
        return

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        source_dir = tmp_dir / "source"
        build_dir = tmp_dir / "build"
        doctree_dir = tmp_dir / "doctrees"

        source_dir.mkdir()
        build_dir.mkdir()
        doctree_dir.mkdir()

        # Write mocked python module
        module_dir = source_dir / "simplepkg"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text('''
"""
= Simple Package

This package demonstrates *sphinx-autodoc2* static parser support.
"""

def greeting(name: str) -> str:
    """
    Say hello to someone.
    
    * Generates greeting string.
    
    [source,python]
    ----
    greeting("Alice")
    ----
    """
    return f"Hello, {name}!"
''')

        sys.path.insert(0, str(source_dir))

        try:
            # Write conf.py
            (source_dir / "conf.py").write_text("""
extensions = [
    "autodoc2",
    "sphinx_asciidoctrine",
]
autodoc2_packages = ["simplepkg"]
autodoc2_docstring_parser_regexes = [
    (r".*", "sphinx_asciidoctrine.parser"),
]
exclude_patterns = []
""")

            # Write index.rst
            (source_dir / "index.rst").write_text("""
Documentation Index
===================

.. toctree::
   :maxdepth: 2

   apidocs/index
""")

            # Run Sphinx build
            app = Sphinx(
                srcdir=str(source_dir),
                confdir=str(source_dir),
                outdir=str(build_dir),
                doctreedir=str(doctree_dir),
                buildername="html",
                status=None,
                warning=sys.stderr,
                freshenv=True,
            )
            app.build()

            # Verify HTML output
            package_html = build_dir / "apidocs" / "simplepkg" / "index.html"
            if not package_html.exists():
                package_html = build_dir / "apidocs" / "simplepkg" / "simplepkg.html"

            assert package_html.exists()

            html_content = package_html.read_text()

            # Check structure elements
            assert "Simple Package" in html_content
            assert "sphinx-autodoc2" in html_content
            assert "Say hello to someone." in html_content
            assert "Generates greeting" in html_content
            # We assert on "Alice" to be robust against HTML character entity differences
            assert "Alice" in html_content

        finally:
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))
