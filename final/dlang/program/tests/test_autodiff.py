import inspect
import itertools
import os

import pytest

from test_utils import run_interpreter as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestAutodiffScalar:
    pass


class TestAutodiffTensor:
    pass
