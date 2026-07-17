from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def rootdir() -> Path:
    """
    Returns the root directory for test sphinx projects.
    """
    return Path(__file__).parent.resolve() / "roots"
