import inspect
import itertools
import os

import pytest

from test_utils import run_interpreter, run_typechecker


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestAutodiffScalarLPTSuccess:
    def test_track_grad_tag(self, compiler_bin):
        prog = inspect.cleandoc('x:track_grad = 5.;')
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")

    def test_backward_builtin(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x);
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")

    def test_backward_builtin_arbitrary_expr(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(2. * x + 5.);
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")


    def test_grad_builtin(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x);
            grad(x);
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")

    def test_grad_builtin_ret_type(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a;
            }
            x:track_grad = 5.;
            backward(x);
            f(grad(x));
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")



class TestAutodiffScalarLPTError:
    @pytest.mark.parametrize("target", [
        '1. + 2.',
    ])
    def test_track_grad_bad_target(self, compiler_bin, target):
        prog = inspect.cleandoc(f'{target}:track_grad;')
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    @pytest.mark.parametrize("target", [
        'x = 10.',
    ])
    def test_backward_builtin_stmt_target(self, compiler_bin, target):
        prog = inspect.cleandoc(f'backward({target});')
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    @pytest.mark.parametrize("target", [
        'sum(Vector[1., 2.])',
        'numcols(Vector[x])',
        'numrows(Vector[x])',
        'addrow(Vector[x], 0, 0.)',
        'addcol(Vector[x], 0, 0.)',
        'backward(x + 1)'
        'grad(x)'
    ])
    def test_backward_bad_expr_target(self, compiler_bin, target):
        prog = inspect.cleandoc(f"""
            x:track_grad = 5;
            backward({target});
        """)
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    def test_grad_builtin_bad_target_expr(self, compiler_bin):
        prog = inspect.cleandoc('grad(4 + 6);')
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    def test_grad_builtin_bad_target_expr_with_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 10;
            grad(x * 2);
        """)
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1


    def test_grad_builtin_untracked_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 10;
            y:track_grad = 10;
            z:track_grad = 10;
            w = 5;
            grad(w);
        """)
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    def test_grad_builtin_untracked_var_set_to_tracked_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 10;
            y = x;
            grad(y);
        """)
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

class TestAutodiffScalarSuccess:
    def test_backward_without_track_grad(self, compiler_bin):
        prog = inspect.cleandoc("""
            x = 5.;
            backward(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS:")


    def test_var_only(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1.")

    def test_var_only_int(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5;
            backward(x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1.")

    @pytest.mark.parametrize("binop,res", [
        ('+', '1.'),
        ('-', '1.'),
        ('*', '2.'),
        ('/', '0.5'),
    ])
    def test_binop_dvar_on_left(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = 10.;
            backward(x {binop} 2.);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: {res}")

    @pytest.mark.parametrize("binop,res", [
        ('+', '1.'),
        ('-', '-1.'),
        ('*', '10.'),
        ('/', '-0.1'),
    ])
    def test_binop_dvar_on_right(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = 10.;
            backward(10. {binop} x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: {res}")


    def test_dvar_set_to_intermediate_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x;
            backward(y);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1.")

    def test_intermediate_var_with_dvar_expr(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x * 10.;
            backward(y);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 10.")


    def test_dvar_shadowing(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 10.;
            x:track_grad = 5.;
            backward(10. / x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: -0.4")

    def test_func_return_grad(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(x: float) {
                backward(x);
                grad(x);
            }

            x:track_grad = 10.;
            f(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1.")


    def test_func_return_var_of_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a;
            }

            x:track_grad = 10.;
            backward(f(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1.")

    def test_func_return_expr_of_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a * 10.;
            }

            x:track_grad = 10.;
            backward(f(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 10.")

    def test_func_with_intermediate_var_of_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                b = a * 10.;
                b * 5.;
            }

            x:track_grad = 10.;
            backward(f(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 50.")


    @pytest.mark.parametrize("binop,res", [
        ('+', '2.'),
        ('-', '0.'),
        ('*', '20.'),
        ('/', '0.'),
    ])
    def test_binop_dvar_both_sides(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = 10.;
            backward(x {binop} x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: {res}")


    def test_expr_with_intermediate_var_of_dvar_and_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x * 10.;
            backward(y + x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 11.")


    def test_no_backwards_call(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS:")

    def test_multiple_dvars_add(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y:track_grad = 5.;
            backward(x + y);
            grad(x) + grad(y);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 2.")

    def test_multiple_dvars_mult(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 10.;
            y:track_grad = 1.;
            backward(x * y);
            grad(x) + grad(y);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 11.")


    def test_multiple_backward_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x + 2.);
            backward(x + 5.);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 2.")


class TestAutodiffTensor:
    pass
