import inspect
import itertools
import os

import pytest

from test_utils import run_interpreter as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestBroadcastingInterpreter:
    @pytest.mark.parametrize("binop,res", [
        ("+", "[5., 8., 11.]"),
        ("-", "[1., 4., 7.]"),
        ("*", "[6., 12., 18.]"),
        ("/", "[1.5, 3., 4.5]")
    ])
    def test_vector_and_int(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f'Vector[3., 6., 9.] {binop} 2.;')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: Vector{res}')

    @pytest.mark.parametrize("binop,res", [
        ("+", "Matrix[[3.,4.],[5.,6.]]"),
        ("-", "Matrix[[0.,1.],[2.,3.]]"),
        ("*", "Matrix[[2.,4.],[6.,8.]]"),
        ("/", "Matrix[[.5,1.],[1.5,2.]]")
    ])
    def test_matrix_and_int(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            Matrix[[1., 2.], [3., 4.]] {binop} 2.;
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("binop,res", [
        ("+", "Matrix[[2.,4.],[4.,6.]]"),
        ("-", "Matrix[[0.,0.],[2.,2.]]"),
        ("*", "Matrix[[1.,4.],[3.,8.]]"),
        ("/", "Matrix[[1.,1.],[3.,2.]]")
    ])
    def test_square_matrix_and_vector(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            Matrix[[1., 2.], [3., 4.]] {binop} Vector[1., 2.];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("binop,res", [
        ("+", "Matrix[[2.,4.],[4.,6.],[6.,8.]]"),
        ("-", "Matrix[[0.,0.],[2.,2.],[4.,4.]]"),
        ("*", "Matrix[[1.,4.],[3.,8.],[5.,12.]]"),
        ("/", "Matrix[[1.,1.],[3.,2.],[5.,3.]]")
    ])
    def test_matrix_and_vector_by_row(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            Matrix[[1., 2.], [3., 4.], [5., 6.]] {binop} Vector[1., 2.];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("binop,res", [
        ("+", "Matrix[[2.,3.],[5.,6.],[9.,10.]]"),
        ("-", "Matrix[[0.,1.],[1.,2.],[1.,2.]]"),
        ("*", "Matrix[[1.,2.],[6.,8.],[20.,24.]]"),
        ("/", "Matrix[[1.,2.],[1.5,2.],[1.25,1.5]]")
    ])
    def test_matrix_and_vector_by_col(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            Matrix[[1., 2.], [3., 4.], [5., 6.]] {binop} Vector[1., 2., 4.];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

class TestBroadcastingGradients:
    def test_vector_add(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[3., 6., 9.];
            backward(x + 2);
            grad(x);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS: Vector[1., 1., 1.]")

    def test_vector_mul(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[3., 6., 9.];
            backward(x * 2);
            grad(x);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS: Vector[2., 2., 2.]")
