import sys
import tempfile
from pathlib import Path

from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser as RstParser
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_asciidoctrine.parser import Parser as Autodoc2Parser


def test_autodoc2_parser_integration() -> None:
    """
    Test the docstrings parser integration directly by parsing an AsciiDoc docstring
    containing complex formatting, block attributes, and lists, verifying docutils output.
    """
    parser = Autodoc2Parser()
    settings = get_default_settings(RstParser)
    document = new_document("test", settings)

    docstring = """
This is a standard docstring for a function.

* Item 1
* Item 2 with *bold* formatting.

[source,python]
----
def my_func():
    return True
----
"""
    parser.parse(docstring, document)

    # Verify nodes are parsed correctly using astext()
    content = document.astext()
    assert "Item 1" in content
    assert "Item 2 with" in content
    assert "my_func" in content


def test_sphinx_autodoc_integration() -> None:
    """
    Sets up a programmatic Sphinx application and builds documentation
    for a mocked Python module with AsciiDoc docstrings, verifying doctree elements.
    """
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        source_dir = tmp_dir / "source"
        build_dir = tmp_dir / "build"
        doctree_dir = tmp_dir / "doctrees"

        source_dir.mkdir()
        build_dir.mkdir()
        doctree_dir.mkdir()

        # Write dummy Python module
        module_dir = source_dir / "mymodule"
        module_dir.mkdir()

        # We write __init__.py containing a class with AsciiDoc docstrings
        (module_dir / "__init__.py").write_text('''
"""
= My Module

This is the module docstring written in AsciiDoc.
"""

class MathHelper:
    """
    A helpful class for math.
    
    * Adds numbers
    * Multiplies numbers
    """
    
    def add(self, a: int, b: int) -> int:
        """
        Add two integers.
        
        [source,python]
        ----
        helper = MathHelper()
        helper.add(1, 2) # => 3
        ----
        """
        return a + b
''')

        # Add the temporary source directory to Python path so autodoc can import the module
        sys.path.insert(0, str(source_dir))

        try:
            # Write Sphinx conf.py
            (source_dir / "conf.py").write_text("""
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_asciidoctrine",
]
templates_path = []
exclude_patterns = []
""")

            # Write index.rst invoking autodoc (use autoclass to avoid automodule duplicates)
            (source_dir / "index.rst").write_text("""
Welcome to Test Docs
===================

.. automodule:: mymodule

.. autoclass:: mymodule.MathHelper
   :members:
""")

            # Initialize Sphinx programmatically
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

            # Build the project
            app.build()

            # Read the generated doctree for index.rst
            doctree_file = doctree_dir / "index.doctree"
            assert doctree_file.exists()

            # Verify that output files were successfully built
            index_html = build_dir / "index.html"
            assert index_html.exists()

            html_content = index_html.read_text()
            # Verify module, class, list items and source block rendered in HTML
            assert "My Module" in html_content
            assert "MathHelper" in html_content
            assert "Adds numbers" in html_content
            assert "add" in html_content

        finally:
            if str(source_dir) in sys.path:
                sys.path.remove(str(source_dir))
