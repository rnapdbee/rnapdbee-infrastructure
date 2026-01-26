import os

import pytest

from . import helpers


@pytest.fixture(scope="session")
def base_url() -> str:
    return helpers.get_base_url()


@pytest.fixture(scope="session")
def examples_root() -> str:
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "rnapdbee-frontend",
        "src",
        "assets",
        "examples",
    )
