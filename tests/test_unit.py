from unittest.mock import MagicMock

from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser as RstParser
from docutils.utils import new_document

from sphinx_asciidoctrine import AsciiDocParser, process_docstring, setup
from sphinx_asciidoctrine.parser import Parser as Autodoc2Parser


def test_setup_registration() -> None:
    """
    Test that the Sphinx setup function registers suffixes, parser, and events.
    """
    app = MagicMock()
    result = setup(app)

    assert result["version"] == "0.1.0a1"
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True

    # Verify suffix and parser registration
    app.add_source_suffix.assert_any_call(".adoc", "asciidoc")
    app.add_source_suffix.assert_any_call(".asciidoc", "asciidoc")
    app.add_source_parser.assert_called_once_with(AsciiDocParser)

    from unittest.mock import ANY

    app.connect.assert_any_call("config-inited", ANY)


def test_process_docstring_empty() -> None:
    """
    Test that process_docstring does nothing if the docstring lines list is empty.
    """
    lines: list[str] = []
    process_docstring(None, "module", "test", None, None, lines)
    assert lines == []


def test_process_docstring_translation() -> None:
    """
    Test that process_docstring successfully translates AsciiDoc docstring lines to reST.
    """
    lines = [
        "= Document Title",
        "",  # Blank line required after document title in AsciiDoc
        "This is an AsciiDoc paragraph.",
        "",
        "[source,python]",
        "----",
        "print('hello')",
        "----",
    ]

    process_docstring(None, "class", "MyClass", None, None, lines)

    # Verify that the lines have been translated to reST in-place
    translated_text = "\n".join(lines)
    assert "Document Title" in translated_text
    assert "This is an AsciiDoc paragraph." in translated_text
    assert ".. code-block:: python" in translated_text
    assert "print('hello')" in translated_text


def test_process_docstring_exception() -> None:
    """
    Test that process_docstring appends an error message if the translation fails.
    """
    import asciidocstring

    old_parse = asciidocstring.parse
    try:
        asciidocstring.parse = MagicMock(side_effect=ValueError("Mocked Parse Error"))
        lines = ["Some docstring"]
        process_docstring(None, "class", "MyClass", None, None, lines)
        assert len(lines) > 1
        assert "Mocked Parse Error" in "\n".join(lines)
        assert ".. error::" in "\n".join(lines)
    finally:
        asciidocstring.parse = old_parse


def test_autodoc2_parser_docstrings() -> None:
    """
    Test that the sphinx_asciidoctrine.parser.Parser (for sphinx-autodoc2)
    properly compiles raw AsciiDoc into reST nodes.
    """
    input_text = "= Hello\n\nThis is a *bold* statement."
    settings = get_default_settings(RstParser)
    document = new_document("test", settings)

    parser = Autodoc2Parser()
    parser.parse(input_text, document)

    # Verify document structure and nodes using astext()
    content = document.astext()
    assert "Hello" in content
    assert "bold" in content


def test_asciidoc_parser_sphinx() -> None:
    """
    Test the standard Sphinx AsciiDocParser on basic markup.
    """
    input_text = "= Title\n\nFirst paragraph."
    settings = get_default_settings(RstParser)
    document = new_document("test", settings)

    parser = AsciiDocParser()
    parser.parse(input_text, document)

    # Verify document nodes populated by DocutilsRenderer
    content = document.astext()
    assert "Title" in content
    assert "First paragraph." in content


def test_asciidoc_parser_error() -> None:
    """
    Test that AsciiDocParser appends an error node if the parser crashes.
    """
    input_text = "= Title"
    settings = get_default_settings(RstParser)
    document = new_document("test", settings)

    parser = AsciiDocParser()
    # Mock parse_to_ast to raise an error
    from unittest.mock import patch

    with patch(
        "sphinx_asciidoctrine.parse_to_ast", side_effect=Exception("Critical Failure")
    ):
        parser.parse(input_text, document)

    content = document.astext()
    assert "AsciiDoc Parse Error: Critical Failure" in content


def test_setup_config_inited_hook() -> None:
    """
    Test that setup connects 'autodoc-process-docstring' depending on
    the value of 'asciidoc_process_docstrings' configuration.
    """
    app = MagicMock()
    setup(app)

    # Get the on_config_inited callback registered to config-inited
    on_config_inited_callback = None
    for call in app.connect.call_args_list:
        if call[0][0] == "config-inited":
            on_config_inited_callback = call[0][1]
            break

    assert on_config_inited_callback is not None

    # Scenario A: asciidoc_process_docstrings is True (default)
    app.reset_mock()
    config_enabled = MagicMock()
    config_enabled.asciidoc_process_docstrings = True
    on_config_inited_callback(app, config_enabled)
    app.connect.assert_any_call("autodoc-process-docstring", process_docstring)

    # Scenario B: asciidoc_process_docstrings is False
    app.reset_mock()
    config_disabled = MagicMock()
    config_disabled.asciidoc_process_docstrings = False
    on_config_inited_callback(app, config_disabled)

    # Verify autodoc-process-docstring was NOT connected
    for call in app.connect.call_args_list:
        assert call[0][0] != "autodoc-process-docstring"
