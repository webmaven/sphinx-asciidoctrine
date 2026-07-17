import os
from typing import Any, ClassVar, Dict, List

from asciidoctrine.docutils_backend import DocutilsRenderer
from asciidoctrine.lark_parser import parse_to_ast
from docutils import nodes
from sphinx.errors import ExtensionError
from sphinx.parsers import Parser as SphinxParser

__version__ = "0.1.0a1"


class AsciiDocParser(SphinxParser):
    """
    Sphinx source parser for AsciiDoc (.adoc and .asciidoc) files.
    Constructs an AST using asciidoctrine and transforms it into Docutils nodes.
    """

    supported: ClassVar[tuple[str, ...]] = ("asciidoc", "adoc")

    def parse(self, inputstring: str, document: nodes.document) -> None:
        base_dir = None
        source_path = getattr(document, "attributes", {}).get("source", None)
        if source_path:
            base_dir = os.path.dirname(os.path.abspath(source_path))

        try:
            ast = parse_to_ast(inputstring, base_dir=base_dir, safe_mode=False)
            renderer = DocutilsRenderer(document)
            renderer.visit(ast)
        except Exception as e:
            error = nodes.error("", nodes.paragraph("", f"AsciiDoc Parse Error: {e}"))
            document += error


def process_docstring(
    app: Any,
    what: str,
    name: str,
    obj: Any,
    options: Any,
    lines: List[str],
) -> None:
    """
    Hook connected to Sphinx's 'autodoc-process-docstring' event.
    Detects if lines are present, parses them as an AsciiDoc docstring,
    and translates them to reStructuredText in-place.
    """
    if not lines:
        return

    docstring_text = "\n".join(lines)
    try:
        import asciidocstring

        parsed_doc = asciidocstring.parse(docstring_text)
        rest_text = parsed_doc.to_rest()

        # Modify lines in-place
        lines[:] = rest_text.splitlines()
    except ImportError:
        # If asciidocstring is not installed, leave docstring alone
        pass
    except Exception as e:
        # If parsing or translation fails, append the error context so the user can debug
        lines.append("")
        lines.append(f".. error:: AsciiDoc Docstring Error: {e}")


def setup(app: Any) -> Dict[str, Any]:
    """
    Standard Sphinx extension setup function.
    Registers source suffixes and the custom AsciiDoc parser.
    """
    if app is not None:
        # Register configuration value to enable/disable processing docstrings as AsciiDoc
        app.add_config_value("asciidoc_process_docstrings", True, "env")

        app.add_source_suffix(".adoc", "asciidoc")
        app.add_source_suffix(".asciidoc", "asciidoc")
        app.add_source_parser(AsciiDocParser)

        # Connect to the autodoc process-docstring event during config-inited when all extensions are loaded
        def on_config_inited(app: Any, config: Any) -> None:
            if not getattr(config, "asciidoc_process_docstrings", True):
                return
            try:
                app.connect("autodoc-process-docstring", process_docstring)
            except ExtensionError:
                # If sphinx.ext.autodoc is not used, skip
                pass

        app.connect("config-inited", on_config_inited)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
