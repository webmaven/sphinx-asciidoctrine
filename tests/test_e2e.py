import subprocess
import sys
import tempfile
from pathlib import Path


def test_sphinx_build_cli_e2e() -> None:
    """
    Tier 4 (E2E): Spawn a standard CLI sphinx-build process with the -W (warnings-as-errors) flag,
    verifying a clean zero exit code and correct HTML file production.
    """
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        source_dir = tmp_dir / "source"
        build_dir = tmp_dir / "build"

        source_dir.mkdir()
        build_dir.mkdir()

        # Write index.adoc
        (source_dir / "index.adoc").write_text("""
= Comprehensive Project Docs
:toc:

== Introduction
Welcome to the E2E verification document parsed natively by sphinx-asciidoctrine!

== Code Block
[source,python]
----
def greet():
    print("E2E is success!")
----
""")

        # Write conf.py
        (source_dir / "conf.py").write_text("""
extensions = [
    "sphinx_asciidoctrine",
]
templates_path = []
exclude_patterns = []
""")

        # Execute sphinx-build via subprocess
        # Using the current virtual environment's sphinx-build executable
        sphinx_build_bin = Path(sys.executable).parent / "sphinx-build"
        if not sphinx_build_bin.exists():
            sphinx_build_bin = "sphinx-build"  # Fallback to PATH search

        cmd = [
            str(sphinx_build_bin),
            "-W",  # Treat warnings as errors
            "-b",
            "html",  # HTML builder
            str(source_dir),
            str(build_dir),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)

        # Assert correct exit code and file generation
        assert result.returncode == 0, (
            f"sphinx-build failed with exit code {result.returncode}\nStderr: {result.stderr}"
        )
        assert (build_dir / "index.html").exists()

        html_content = (build_dir / "index.html").read_text()
        assert "Comprehensive Project Docs" in html_content
        assert "E2E is success!" in html_content
