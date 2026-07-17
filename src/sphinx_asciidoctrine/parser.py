from typing import Any

import asciidocstring
from docutils.parsers import Parser as DocutilsParser
from docutils.parsers.rst import Parser as RstParser


class Parser(DocutilsParser):  # type: ignore[misc]
    """
    Docutils/Sphinx-compliant AsciiDoc parser class for docstrings.
    Translates raw AsciiDoc text to reStructuredText (reST) and delegates parsing
    to Docutils' built-in reStructuredText parser.
    """

    supported: tuple[str, ...] = ("asciidoc", "adoc")

    def parse(self, inputstring: str, document: Any) -> None:
        try:
            rst_text = asciidocstring.parse(inputstring).to_rest()
        except Exception as e:
            # Append error block or fallback to original text
            rst_text = f".. error:: AsciiDoc Docstring Error: {e}\n\n" + inputstring

        rst_parser = RstParser()
        rst_parser.parse(rst_text, document)
