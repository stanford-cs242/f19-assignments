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

    def test_backward_builtin_intermediate_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = 2. * x;
            z = y + 5.;
            backward(z);
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")

    def test_backward_builtin_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a:float) {
                a * 2.;
            }

            x:track_grad = 5.;
            backward(f(x));
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

    def test_grad_builtin_multiple_dvars(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y:track_grad = x;
            backward(y);
            grad(x);
            grad(y);
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")

    def test_backward_builtin_outside_of_backprop(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = sum(Vector[1., 2.]);
            backward(x);
        """)
        assert run_typechecker(compiler_bin, prog).startswith("SUCCESS")


class TestAutodiffScalarLPTError:
    @pytest.mark.parametrize("target", [
        '1. + 2.',
        'Vector[1.]',
        'def f(a:int){a;} f(15.)'
    ])
    def test_track_grad_bad_target(self, compiler_bin, target):
        prog = inspect.cleandoc(f'{target}:track_grad;')
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    @pytest.mark.parametrize("target", [
        'x = 10.',
        'def f(){2.;}',
        '10.;'
    ])
    def test_backward_builtin_stmt_target(self, compiler_bin, target):
        prog = inspect.cleandoc(f'backward({target});')
        assert run_typechecker(compiler_bin, prog).find("ERROR") != -1

    @pytest.mark.parametrize("target", [
        'sum(Vector[x, 2.])',
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

    def test_grad_builtin_bad_target_expr_with_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
                a:track_grad = 10;
                a;
            }
            grad(f());
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

    def test_backward_without_track_grad_set_to_tracked_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x;
            backward(y);
            grad(x);
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

    @pytest.mark.parametrize("x,y,res", [
        ('10', '2', '2.'),
        ('10.', '2', '2.'),
        ('10', '2.', '2.'),
    ])
    def test_binop_int_float_coercion(self, compiler_bin, x, y, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = {x};
            backward(x * {y});
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

    def test_dvar_set_to_multiple_intermediate_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x;
            z = y;
            w = z;
            backward(w);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1.")

    def test_multiple_intermediate_var_with_dvar_expr(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x * 10.;
            z = y + 2.;
            w = z / 5.;
            backward(w);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 2.")

    def test_dvar_shadowing(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 10.;
            x:track_grad = 5.;
            backward(10. / x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: -0.4")

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

    def test_func_with_many_statements(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                b = a * 10.;
                c = b + 15. * a;
                d = c / 12.5;
                d;
            }

            x:track_grad = 10.;
            backward(f(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 2.")

    def test_func_with_nested_func_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a * 10.;
            }

            def g(b: float) {
                f(b) * 5.;
            }

            x:track_grad = 10.;
            backward(g(x));
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

    def test_binop_dvar_multiple_uses(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(x: float) {
                x + x;
            }

            x:track_grad = 10.;
            backward(f(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS:")

    def test_func_calls_multiple_uses_of_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a * 10.;
            }

            x:track_grad = 5.;
            backward(f(x) * f(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 1000.")

    def test_expr_with_intermediate_var_of_dvar_and_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y = x * 10.;
            backward(y + x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 11.")

    def test_expr_with_multiple_intermediate_uses_of_dvar(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a;
            }

            x:track_grad = 5.;
            y = x * 10.;
            z = y + f(y);
            backward(z + x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 21.")

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

    def test_multiple_dvars_composite(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(w:int, x:int, b:int) {
                w * x + b;
            }

            w:track_grad = 10;
            x = 5;
            b:track_grad = 1;
            backward(f(w, x, b));
            grad(w) + grad(b);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 6.")

    def test_multiple_backward_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x + 2.);
            backward(x + 5.);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 2.")

    def test_multiple_backward_calls_mult(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x * 2.);
            backward(x * 5.);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 7.")

    def test_multiple_backward_calls_intermediaries(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            backward(x * 2.);
            y = (x + 10.) * x;
            backward(y);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 22.")

    def test_multiple_backward_calls_in_funcs(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                backward(a * 2.);
            }

            def g(a: float) {
                backward(a * 5.);
            }
            x:track_grad = 5.;
            f(x);
            g(x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 7.")

    def test_multiple_backward_multiple_dvars(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = 5.;
            y:track_grad = 10.;
            backward(x * y);
            backward(x * y);
            grad(x) + grad(y);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 30.")


class TestAutodiffTensorElemwiseVectors:
    def test_vector_only(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5., 5.];
            backward(x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[1., 1.]")

    def test_vector_only_int(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5, 5];
            backward(x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[5., 5.]")

    @pytest.mark.parametrize("binop,res", [
        ('+', 'Vector[1., 1.]'),
        ('-', 'Vector[1., 1.]'),
        ('*', 'Vector[2., 2.]'),
        ('/', 'Vector[0.5, 0.5]'),
    ])
    def test_binop_dvar_on_left(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = Vector[10., 10.];
            backward(x {binop} Vector[2., 2.]);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: {res}")

    def test_binop_dvar_on_right(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[10., 10.];
            backward(Vector[10., 10.] + x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[1., 1.]")

    @pytest.mark.parametrize("binop,res", [
        ('+', 'Vector[2.]'),
        ('-', 'Vector[0.]'),
        ('*', 'Vector[20.]'),
        ('/', 'Vector[0.]'),
    ])
    def test_binop_dvar_both_sides(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = Vector[10.];
            backward(x {binop} x);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: {res}")

    @pytest.mark.parametrize("x,y,res", [
        ('Vector[10]', 'Vector[2]', 'Vector[2.]'),
        ('Vector[10.]', 'Vector[2]', 'Vector[2.]'),
        ('Vector[10]', 'Vector[2.]', 'Vector[2.]'),
    ])
    def test_binop_int_float_coercion(self, compiler_bin, x, y, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = {x};
            backward(x * {y});
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith(f"SUCCESS: {res}")

    def test_chained_binops(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5.];
            y = x * Vector[10.];
            z = y + Vector[2.];
            w = z / Vector[5.];
            backward(w);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[2.]")

    def test_multiple_dvars_add(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5.];
            y:track_grad = Vector[5.];
            backward(x + y);
            grad(x) + grad(y);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[2.]")

    def test_multiple_dvars_mult(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[10.];
            y:track_grad = Vector[1.];
            backward(x * y);
            grad(x) + grad(y);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[11.]")

    def test_multiple_backward_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5.];
            backward(x + Vector[2.]);
            backward(x - Vector[5.]);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[2.]")

    def test_multiple_backward_calls_mult(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5.];
            backward(x * Vector[2.]);
            backward(x * Vector[5.]);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[7.]")

    def test_multiple_backward_calls_intermediaries(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5., 5.];
            backward(x * Vector[2., 2.]);
            y = (x + Vector[10., 10.]) * x;
            backward(y);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[22., 22.]")

    def test_multiple_backward_multiple_dvars(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Vector[5., 6.];
            y:track_grad = Vector[10., 11.];
            backward(x * y);
            backward(x * y);
            grad(x) + grad(y);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[30., 34.]")


class TestAutodiffTensorElemwiseMatrices:
    def test_matrix_only(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5., 5.], [5., 5.]];
            backward(x);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[1.,1.],[1.,1.]]")

    def test_matrix_only_int(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5, 5], [5, 5]];
            backward(x);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[5. 5.],[5.,5.]]")

    @pytest.mark.parametrize("binop,res", [
        ('+', 'Matrix[[1.,1.],[1.,1.]]'),
        ('-', 'Matrix[[1.,1.],[1.,1.]]'),
        ('*', 'Matrix[[2.,2.],[2.,2.]]'),
        ('/', 'Matrix[[0.5,0.5],[0.5,0.5]]'),
    ])
    def test_binop_dvar_on_left(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[10., 10.], [10., 10.]];
            backward(x {binop} Matrix[[2., 2.], [2., 2.]]);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(f"SUCCESS:{res}")

    def test_binop_dvar_on_right(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[10.,10.],[10.,10.]];
            backward(Matrix[[10.,10.],[10.,10.]] + x);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[1.,1.],[1.,1.]]")

    @pytest.mark.parametrize("binop,res", [
        ('+', 'Matrix[[2.]]'),
        ('-', 'Matrix[[0.]]'),
        ('*', 'Matrix[[20.]]'),
        ('/', 'Matrix[[0.]]'),
    ])
    def test_binop_dvar_both_sides(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[10.]];
            backward(x {binop} x);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(f"SUCCESS:{res}")

    @pytest.mark.parametrize("x,y,res", [
        ('Matrix[[10]]', 'Matrix[[2]]', 'Matrix[[2.]]'),
        ('Matrix[[10.]]', 'Matrix[[2]]', 'Matrix[[2.]]'),
        ('Matrix[[10]]', 'Matrix[[2.]]', 'Matrix[[2.]]'),
    ])
    def test_binop_int_float_coercion(self, compiler_bin, x, y, res):
        prog = inspect.cleandoc(f"""
            x:track_grad = {x};
            backward(x * {y});
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(f"SUCCESS:{res}")

    def test_chained_binops(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5.]];
            y = x * Matrix[[10.]];
            z = y + Matrix[[2.]];
            w = z / Matrix[[5.]];
            backward(w);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[2.]]")

    def test_multiple_dvars_add(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5.]];
            y:track_grad = Matrix[[5.]];
            backward(x + y);
            grad(x) + grad(y);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS: Matrix[[2.]]")

    def test_multiple_dvars_mult(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[10.]];
            y:track_grad = Matrix[[1.]];
            backward(x * y);
            grad(x) + grad(y);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[11.]]")

    def test_multiple_backward_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5.]];
            backward(x + Matrix[[2.]]);
            backward(x + Matrix[[5.]]);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[2.]]")

    def test_multiple_backward_calls_mult(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5.]];
            backward(x * Matrix[[2.]]);
            backward(x * Matrix[[5.]]);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[7.]]")

    def test_multiple_backward_calls_intermediaries(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5., 5.], [5., 5.]];
            backward(x * Matrix[[2., 2.], [2., 2.]]);
            y = (x + Matrix[[10., 10.], [10., 10.]]) * x;
            backward(y);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[22.,22.],[22.,22.]]")

    def test_multiple_backward_multiple_dvars(self, compiler_bin):
        prog = inspect.cleandoc("""
            x:track_grad = Matrix[[5., 6.], [7., 8.]];
            y:track_grad = Matrix[[10., 11.], [12., 13.]];
            backward(x * y);
            backward(x * y);
            grad(x) + grad(y);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[30.,34.],[38.,42.]]")


class TestAutodiffTensorAccessorsVectors:
    @pytest.mark.parametrize("i,sol", [
        ('0', 'Vector[1., 0., 0.]'),
        ('1', 'Vector[0., 1., 0.]'),
        ('2', 'Vector[0., 0., 1.]'),
    ])
    def test_basic_accessor_use(self, compiler_bin, i, sol):
        prog = inspect.cleandoc(f"""
            x:track_grad = Vector[1., 2., 3.];
            backward(x[{i},]);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: {sol}")

    def test_using_accessors(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Vector[1., 2., 3.];
            z = x[0,] + 3 * x[1,] + 5 * x[2,];
            backward(z);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[1, 3, 5]")

    def test_using_accessors_alternate_access(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Vector[1., 2., 3.];
            z = x[,0] + 3 * x[,1] + 5 * x[,2];
            backward(z);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[1, 3, 5]")

    def test_using_accessors_with_intermediates(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Vector[1., 2., 3.];
            z = x[0,] + 3. * x[1,] + 5. * x[2,];
            y = z + x[2,];
            backward(y);
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[1, 3, 6]")


class TestAutodiffTensorAccessorsMatrices:
    @pytest.mark.parametrize("i,sol", [
        ('0,0', 'Matrix[[1.,0.,0.],[0.,0.,0.],[0.,0.,0.]]'),
        ('0,1', 'Matrix[[0.,1.,0.],[0.,0.,0.],[0.,0.,0.]]'),
        ('0,2', 'Matrix[[0.,0.,1.],[0.,0.,0.],[0.,0.,0.]]'),
        ('1,0', 'Matrix[[0.,0.,0.],[1.,0.,0.],[0.,0.,0.]]'),
        ('1,1', 'Matrix[[0.,0.,0.],[0.,1.,0.],[0.,0.,0.]]'),
        ('1,2', 'Matrix[[0.,0.,0.],[0.,0.,1.],[0.,0.,0.]]'),
        ('2,0', 'Matrix[[0.,0.,0.],[0.,0.,0.],[1.,0.,0.]]'),
        ('2,1', 'Matrix[[0.,0.,0.],[0.,0.,0.],[0.,1.,0.]]'),
        ('2,2', 'Matrix[[0.,0.,0.],[0.,0.,0.],[0.,0.,1.]]'),
    ])
    def test_access_one_element(self, compiler_bin, i, sol):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]];
            backward(x[{i}]);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:{sol}")

    @pytest.mark.parametrize("i,sol", [
        ('0,', 'Matrix[[1.,1.,1.],[0.,0.,0.],[0.,0.,0.]]'),
        ('1,', 'Matrix[[0.,0.,0.],[1.,1.,1.],[0.,0.,0.]]'),
        ('2,', 'Matrix[[0.,0.,0.],[0.,0.,0.],[1.,1.,1.]]'),
    ])
    def test_access_rows(self, compiler_bin, i, sol):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1.,0.,0.],[0.,0.,0.],[0.,0.,0.]];
            backward(x[{i}]);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:{sol}")

    @pytest.mark.parametrize("i,sol", [
        (',0', 'Matrix[[1.,0.,0.],[1.,0.,0.],[1.,0.,0.]]'),
        (',1', 'Matrix[[0.,1.,0.],[0.,1.,0.],[0.,1.,0.]]'),
        (',2', 'Matrix[[0.,0.,1.],[0.,0.,1.],[0.,0.,1.]]'),
    ])
    def test_access_columns(self, compiler_bin, i, sol):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1.,0.,0.],[0.,0.,0.],[0.,0.,0.]];
            backward(x[{i}]);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:{sol}")

    def test_using_elements(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]];
            z = x[0,0] + 2 * x[0,2] + 3 * x[1,1] + 4 * x[1,2] + 5 * x[2,2];
            y = z + x[2,2];
            backward(y);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[1.,0.,2.],[0.,3.,4.],[0.,0.,6.]]")

    def test_using_rows(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]];
            z = x[0,] + Vector[2.,2.,2.] * x[0,] + Vector[3.,3.,3.] * x[1,] + Vector[4.,4.,4.] * x[1,] + Vector[5.,5.,5.] * x[2,];
            y = z + x[2,];
            backward(y);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[3.,3.,3.],[7.,7.,7.],[6.,6.,6.]]")

    def test_using_cols(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]];
            z = x[,0] + Vector[2.,2.,2.] * x[,2] + Vector[3.,3.,3.] * x[,1] + Vector[4.,4.,4.] * x[,2] + Vector[5.,5.,5.] * x[,2];
            y = z + x[,2];
            backward(y);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[1.,3.,12.],[1.,3.,12.],[1.,3.,12.]]")

    def test_using_all_accessors(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            x:track_grad = Matrix[[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]];
            rows = x[0,] + Vector[2.,2.,2.] * x[0,] + Vector[3.,3.,3.] * x[1,] + Vector[4.,4.,4.] * x[1,] + Vector[5.,5.,5.] * x[2,];
            cols = x[,0] + Vector[2.,2.,2.] * x[,2] + Vector[3.,3.,3.] * x[,1] + Vector[4.,4.,4.] * x[,2] + Vector[5.,5.,5.] * x[,2];
            y = cols[0,] * cols[,2] + rows[,1] * 12 + x[0,0] * 2 + x[1,2] + x[0,1];
            backward(y);
            grad(x);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith("SUCCESS:Matrix[[132.,427.,1430.],[0.,84.,1.],[40.,180.,440.]]")


class TestAutodiffTensorMatrixMultiply:
    def test_empty_matrices(self, compiler_bin):
        prog = inspect.cleandoc("""
            m1:track_grad = Matrix[[]];
            backward(m1 @ Matrix[[]]);
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:Matrix[[]]")

    @pytest.mark.parametrize("m1,m2,res", [
        ('Matrix[[1.]]', 'Matrix[[2.]]', 'Matrix[[2.]]'),
        ('Matrix[[1.]]', 'Matrix[[2., 3., 4., 5.]]', 'Matrix[[14.]]'),
        ('Matrix[[1., 2., 3.]]', 'Matrix[[2.], [2.], [2.]]', 'Matrix[[2., 2., 2.]]'),
        ('Matrix[[1.], [2.], [3.]]', 'Matrix[[2., 2., 2.]]', 'Matrix[[6., 6., 6.]]'),
    ])
    def test_flat_matrices(self, compiler_bin, m1, m2, res):
        prog = inspect.cleandoc(f"""
            m1:track_grad = {m1};
            backward(m1 @ {m2});
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:{res}")

    @pytest.mark.parametrize("m2,res", [
        ('Matrix[[0., 0.], [0., 0.]]', 'Matrix[[0., 0.], [0., 0.]]'),
        ('Matrix[[1., 0.], [0., 1.]]', 'Matrix[[1., 1.], [1., 1.]]'),
        ('Matrix[[1., 1.], [1., 1.]]', 'Matrix[[2., 2.], [2., 2.]]'),
        ('Matrix[[2., 2.], [2., 2.]]', 'Matrix[[4., 4.], [4., 4.]]'),
        ('Matrix[[1., 2.], [3., 4.]]', 'Matrix[[3., 7.], [3., 7.]]'),
    ])
    def test_square_matrices(self, compiler_bin, m2, res):
        prog = inspect.cleandoc(f"""
            m1:track_grad = Matrix[[1., 2.], [3., 4.]];
            backward(m1 @ {m2});
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:{''.join(res.split())}")

    def test_decimals(self, compiler_bin):
        prog = inspect.cleandoc("""
            m1:track_grad = Matrix[[1.5, 2.0], [3.213, 4.12]];
            m2 = Matrix[[1.5, 2.0], [3.213, 4.12]];
            backward(m1 @ m2);
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            "SUCCESS:Matrix[[3.5,7.333],[3.5,7.333]]")

    def test_negatives(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            m1:track_grad = Matrix[[1., -2.], [-3., -4.]];
            m2 = Matrix[[-1., 2.], [3., -4.]];
            backward(m1 @ m2);
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            "SUCCESS:Matrix[[1.,-1.],[1.,-1.]]")

    @pytest.mark.parametrize("m2,res", [
        ('Matrix[[1., 0.], [0., 1.]]', 'Matrix[[1., 1.], [1., 1.], [1., 1.], [1., 1.]]'),
        ('Matrix[[2., 2.], [2., 2.]]', 'Matrix[[4., 4.], [4., 4.], [4., 4.], [4., 4.]]'),
        ('Matrix[[1., 2.], [3., 4.]]', 'Matrix[[3., 7.], [3., 7.], [3., 7.], [3., 7.]]'),
    ])
    def test_one_square_one_not(self, compiler_bin, m2, res):
        prog = inspect.cleandoc(f"""
            m1:track_grad = Matrix[[1., 2.], [3., 4.], [5., 6.], [7., 8.]];
            backward(m1 @ {m2});
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:{''.join(res.split())}")

    @pytest.mark.parametrize("m1,m2,res", [
        (
            'Matrix[[1., 2., 3.],[4., 5., 6.]]',
            'Matrix[[11., 12.],[13., 14.],[15., 16.]]',
            'Matrix[[23., 27., 31.], [23., 27., 31.]]'
        ),
        (
            'Matrix[[1., 2., 3.],[4., 5., 6.]]',
            'Matrix[[11., 12., 13., 14.], [15., 16., 17., 18.], [19., 20., 21., 22.]]',
            'Matrix[[50., 66., 82.], [50., 66., 82.]]'
        ),
        (
            'Matrix[[1., 2., 3.]]',
            'Matrix[[11., 12.],[13., 14.],[15., 16.]]',
            'Matrix[[23., 27., 31.]]'
        ),
        (
            'Matrix[[1., 2., 3.], [4., 5., 6.]]',
            'Matrix[[11.], [12.], [13.]]',
            'Matrix[[11., 12., 13.], [11., 12., 13.]]'
        ),
    ])
    def test_no_square_matrices(self, compiler_bin, m1, m2, res):
        prog = inspect.cleandoc(f"""
            m1:track_grad = {m1};
            backward(m1 @ {m2});
            grad(m1);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:{''.join(res.split())}")

    def test_right_matrix_tracked(self, compiler_bin):
        prog = inspect.cleandoc("""
            m1 = Matrix[[1., 2., 3.],[4., 5., 6.]];
            m2:track_grad = Matrix[[11., 12.],[13., 14.],[15., 16.]];
            backward(m1 @ m2);
            grad(m2);
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            "SUCCESS:Matrix[[5.,5.],[7.,7.],[9.,9.]]")

    def test_both_matrices_tracked(self, compiler_bin):
        prog = inspect.cleandoc("""
            m1:track_grad = Matrix[[1., 2., 3.],[4., 5., 6.]];
            m2:track_grad = Matrix[[11., 12.],[13., 14.],[15., 16.]];
            backward(m1 @ m2);
            sum(grad(m1)) + sum(grad(m2));
        """)
        assert run_interpreter(compiler_bin, prog).startswith(
            "SUCCESS: 204.")

    @pytest.mark.parametrize("m1_tg,m2_tg,m3_tg,tg_var,res", [
        (':track_grad', '', '', 'm1', 'Matrix[[2718., 3393., 4068.], [2718., 3393., 4068.], [2718., 3393., 4068.]]'),
        ('', ':track_grad', '', 'm2', 'Matrix[[792., 900., 1008.], [990., 1125., 1260.], [1188., 1350., 1512.]]'),
        ('', '', ':track_grad', 'm3', 'Matrix[[648., 648., 648.], [693., 693., 693.], [738., 738., 738.]]'),
    ])
    def test_chained_matmul_all_square(self, compiler_bin, m1_tg, m2_tg, m3_tg, tg_var, res):
        prog = inspect.cleandoc(f"""
            m1{m1_tg} = Matrix[[1., 2., 3.],[4., 5., 6.],[7., 8., 9.]];
            m2{m2_tg} = Matrix[[11., 12., 13.],[14., 15., 16.],[17., 18., 19.]];
            m3{m3_tg} = Matrix[[21., 22., 23.],[24., 25., 26.],[27., 28., 29.]];
            backward((m1 @ m2) @ m3);
            grad({tg_var});
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:{''.join(res.split())}")

    @pytest.mark.parametrize("m1_tg,m2_tg,m3_tg,tg_var,res", [
        (':track_grad', '', '', 'm1', 'Matrix[[2945., 3455.], [2945., 3455.], [2945., 3455.]]'),
        ('', ':track_grad', '', 'm2', 'Matrix[[1035., 1260.], [1380., 1680.]]'),
        ('', '', ':track_grad', 'm3', 'Matrix[[255., 255., 255., 255., 255.], [276., 276., 276., 276., 276.]]'),
    ])
    def test_chained_matmul_all_diff(self, compiler_bin, m1_tg, m2_tg, m3_tg, tg_var, res):
        prog = inspect.cleandoc(f"""
            m1{m1_tg} = Matrix[[1., 2.],[3., 4.],[5., 6.]];
            m2{m2_tg} = Matrix[[11., 12.],[13., 14.]];
            m3{m3_tg} = Matrix[[21., 22., 23., 24., 25.],[26., 27., 28., 29., 30.]];
            backward((m1 @ m2) @ m3);
            grad({tg_var});
        """)
        assert "".join(run_interpreter(compiler_bin, prog).split()).startswith(
            f"SUCCESS:{''.join(res.split())}")


class TestAutodiffTensorComposite:
    def test_linear_layer(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(W: Matrix, X: Matrix, b: Matrix) {
                X @ W + b;
            }

            W:track_grad = Matrix[[0., 5.], [10., 2.]];
            X = Matrix[[0.123, 0.1], [0.423, 0.179], [0.246, 0.937]];
            b = Matrix[[0.1, 0.1], [0.1, 0.1], [0.1, 0.1]];
            backward(f(W, X, b));
            sum(grad(W)) + sum(grad(b));
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 10.0160")

    def test_nested_func_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(b: Matrix) {
                b[,0] / Vector[5., 5.];
            }

            def g(b: Matrix) {
                f(b) * Vector[5., 2.];
            }

            W:track_grad = Matrix[[10., 5.], [5., 2.]];
            backward(g(W)[0,] * 10);
            grad(W)[0,];
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: Vector[10., 0.]")

    def test_scalar_target(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(b: Matrix) {
                b[,0] / Vector[5., 5.];
            }

            def g(b: Matrix, x: int) {
                f(b) * Vector[x, x];
            }

            def h(b:int) {
                b + 1;
            }

            x:track_grad = 4;
            W = Matrix[[10., 5.], [5., 2.]];
            backward(g(W, x)[0,] + h(x));
            grad(x);
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 3.")

    def test_accessor_juggling(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(b: Matrix) {
                b[0,] * b[,1];
            }

            def g(b: Vector) {
                b[0,] * b[,1];
            }

            def h(b: float) {
                b * 5;
            }

            W:track_grad = Matrix[[10., 5.], [5., 2.]];
            backward(h(g(f(W))));
            sum(grad(W));
        """)
        assert run_interpreter(compiler_bin, prog).startswith("SUCCESS: 2500.")
