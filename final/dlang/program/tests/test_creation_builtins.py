import inspect
import itertools
import os
import re

import pytest

from test_utils import run_typechecker, run_interpreter


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestBuiltinsCreation:
    def test_rand_type(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: Matrix) {a[0,0];}
            f(rand(2, 2));
        """)
        assert run_typechecker(compiler_bin, prog).startswith('SUCCESS')

    @pytest.mark.parametrize("rows,cols", [
        ("8", "8"),
    ])
    def test_rand_dims(self, compiler_bin, rows, cols):
        prog = inspect.cleandoc(f"""
            m = rand({rows}, {cols});
            numrows(m) * 10 + numcols(m);
        """)
        expected = int(rows) * 10 + int(cols)
        assert run_interpreter(compiler_bin, prog).startswith(f'SUCCESS: {expected}')

    def test_rand_values(self, compiler_bin):
        dim = 4
        for _ in range(3):  # Perform multiple random trials.
            prog = inspect.cleandoc(f"""
                m = rand({dim}, {dim});
                sum(m);
            """)
            match = re.match(r'SUCCESS: (\d+\.(?:\d+)?)', run_interpreter(compiler_bin, prog))
            assert match is not None
            assert 0 <= float(match.group(1)) <= dim ** 2

    def test_rand_type(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: Matrix) {a[0,0];}
            f(fill(2, 2, 1.0));
        """)
        assert run_typechecker(compiler_bin, prog).startswith('SUCCESS')

    @pytest.mark.parametrize("rows,cols", [
        ("8", "8"),
    ])
    def test_fill_dims(self, compiler_bin, rows, cols):
        prog = inspect.cleandoc(f"""
            m = fill({rows}, {cols}, 0.0);
            numrows(m) * 10 + numcols(m);
        """)
        expected = int(rows) * 10 + int(cols)
        assert run_interpreter(compiler_bin, prog).startswith(f'SUCCESS: {expected}')

    @pytest.mark.parametrize("val", [
        "1",
    ])
    def test_rand_values(self, compiler_bin, val):
        dim = 4
        for _ in range(3):  # Perform multiple random trials.
            prog = inspect.cleandoc(f"""
                m = fill({dim}, {dim}, {val});
                sum(m);
            """)
            match = re.match(r'SUCCESS: (\d+\.(?:\d+)?)', run_interpreter(compiler_bin, prog))
            assert match is not None
            assert float(match.group(1)) == (dim ** 2) * float(val)
