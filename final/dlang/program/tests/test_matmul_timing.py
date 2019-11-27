import inspect
import itertools
import os
import time

import pytest

from test_utils import run_interpreter as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))

class TestMatmulTiming:
    @pytest.mark.parametrize("input_dim,hidden_dim,output_dim,seconds", [
        (16, 64, 16, 0.2),
        (32, 256, 64, 0.5),
        (64, 768, 256, 1)
    ])
    def test_matmul_timing(self, compiler_bin, input_dim, hidden_dim,
      output_dim, seconds):
        prog = inspect.cleandoc(f"""
            m1 = rand({input_dim}, {hidden_dim});
            m2 = rand({hidden_dim}, {output_dim});
            m1 @ m2;
        """)
        start = time.perf_counter()
        output = run(compiler_bin, prog)
        end = time.perf_counter()
        assert output.startswith('SUCCESS:')
        assert (end - start) < seconds
