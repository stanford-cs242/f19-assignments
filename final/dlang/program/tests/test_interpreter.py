import inspect
import itertools
import os

import pytest

from test_utils import run_interpreter as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestDLangBaseInterpreterSuccess:
    @pytest.mark.parametrize("binop,res", [
        ("+", "9"), ("-", "3"), ("*", "18"), ("/", "2")
    ])
    def test_binop_scalar_ints(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f'6 {binop} 3;')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("binop,res", [
        ("+", "9.3"), ("-", "3.1"), ("*", "19.22"), ("/", "2.")
    ])
    def test_binop_scalar_floats(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f'6.2 {binop} 3.1;')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("binop,res", [
        ("+", "9."), ("-", "3."), ("*", "18."), ("/", "2.")
    ])
    def test_binop_scalar_mixed(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f'6. {binop} 3;')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("expr,res", [
        ("6 * 3 - 3", "15"),
        ("3 + 6 * 3", "21"),
        ("6 / 3 - 3", "-1"),
        ("3 + 6 / 3", "5"),
        ("6 * (3 - 3)", "0"),
        ("(3 + 6) * 3", "27"),
        ("6 / (3 - 2)", "6"),
        ("(3 + 6) / 3", "3"),
    ])
    def test_ooo(self, compiler_bin, expr, res):
        prog = inspect.cleandoc(f'{expr};')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("vector,res", [
        ("Vector[]", "Vector[]"),
        ("Vector[1.]", "Vector[1.]"),
        ("Vector[1., 2.6, 5.]", "Vector[1., 2.6, 5.]"),
    ])
    def test_vector_def(self, compiler_bin, vector, res):
        prog = inspect.cleandoc(f'{vector};')
        assert run(compiler_bin, prog).startswith(f"SUCCESS: {res}")

    @pytest.mark.parametrize("vector,res", [
        ("Vector[1]", "Vector[1.]"),
        ("Vector[1, 2, 3]", "Vector[1., 2., 3.]"),
    ])
    def test_vector_int_coercion(self, compiler_bin, vector, res):
        prog = inspect.cleandoc(f'{vector};')
        assert run(compiler_bin, prog).startswith(f"SUCCESS: {res}")

    def test_vector_reduction(self, compiler_bin):
        prog = inspect.cleandoc('Vector[4. + 4., 3. * 3., 2. / 2., 1. - 1.];')
        assert run(compiler_bin, prog).startswith(
            "SUCCESS: Vector[8., 9., 1., 0.]")

    @pytest.mark.parametrize("binop,res", [
        ("+", "[4., 8., 12.]"),
        ("-", "[2., 4., 6.]"),
        ("*", "[3., 12., 27.]"),
        ("/", "[3., 3., 3.]")
    ])
    def test_binop_vector(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f'Vector[3., 6., 9.] {binop} Vector[1., 2., 3.];')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: Vector{res}')

    def test_binop_empty_vector(self, compiler_bin):
        prog = inspect.cleandoc('Vector[] + Vector[];')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: Vector[]')

    def test_binop_vector_by_copy(self, compiler_bin):
        prog = inspect.cleandoc("""
            x = Vector[1., 2., 3.];
            y = Vector[1., 2., 3.];
            x * y;
            sum(x) + sum(y);
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: 12.')

    @pytest.mark.parametrize("tensor,row,res", [
        ("Vector[1.]", "0", "1."),
        ("Vector[1., 2., 3.]", "0", "1."),
        ("Vector[1., 2., 3.]", "2", "3."),
    ])
    def test_row_accessor(self, compiler_bin, tensor, row, res):
        prog = inspect.cleandoc(f'{tensor}[{row},];')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("tensor,col,res", [
        ("Vector[1.]", "0", "1."),
        ("Vector[1., 2., 3.]", "0", "1."),
        ("Vector[1., 2., 3.]", "2", "3."),
    ])
    def test_col_accessor(self, compiler_bin, tensor, col, res):
        prog = inspect.cleandoc(f'{tensor}[,{col}];')
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    def test_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x = 10;
            x + 2;
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 12')

    def test_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            x = 10 + Vector[12, 10][,1];
            x + 2;
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 22.')

    def test_func_def(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            def g() {
                6;
            }
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: No output')

    def test_no_args_func_app(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
                10;
            }

            f();
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 10')

    def test_func_app_with_args(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 15')

    def test_func_app_with_arg_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: float) {
                a + b;
            }

            f(3 + 2, Vector[10][0,]);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 15')

    def test_func_app_in_expr(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            f(5, 10) + 5;
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 20')

    def test_func_def_with_vars(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                c = a + b;
                c * 2;
            }

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 30')

    def test_func_app_with_var_shadowing_above(self, compiler_bin):
        prog = inspect.cleandoc("""
            c = 10;

            def f(a: int, b: int) {
                c = a + b;
                c * 2;
            }

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 30')

    def test_func_app_with_var_shadowing_above(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                c = a + b;
                c * 2;
            }

            c = 10;

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 30')

    def test_func_app_with_closure(self, compiler_bin):
        prog = inspect.cleandoc("""
            c = 10;

            def f(a: int, b: int) {
                a + b + c;
            }

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 25')

    def test_func_app_chained(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            def g(a: int, b: int) {
                a * b;
            }

            f(5, 10) + g(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 65')

    def test_func_app_nested(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            def g(a: int, b: int) {
                a * b;
            }

            g(f(5, 10), 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 150')

    def test_func_app_in_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            def g(a: int, b: int) {
                f(a, b) * b;
            }

            g(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 150')

    def test_func_name_equals_var_name(self, compiler_bin):
        prog = inspect.cleandoc("""
            def a(a: int) {
                a;
            }

            a = 10;
            a(a);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 10')

    @pytest.mark.parametrize("vector,res", [
        ("Vector[]", "0"),
        ("Vector[1.]", "1"),
        ("Vector[1., 2., 3.]", "3")
    ])
    def test_num_rows(self, compiler_bin, vector, res):
        prog = inspect.cleandoc(f"""
            numrows({vector});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("vector,res", [
        ("Vector[]", "0"),
        ("Vector[1.]", "1"),
        ("Vector[1., 2., 3.]", "3")
    ])
    def test_num_cols(self, compiler_bin, vector, res):
        prog = inspect.cleandoc(f"""
            numcols({vector});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("vector,res", [
        ("Vector[]", "0."),
        ("Vector[1.]", "1."),
        ("Vector[1.1, 2.2, 3.3]", "6.6")
    ])
    def test_sum(self, compiler_bin, vector, res):
        prog = inspect.cleandoc(f"""
            sum({vector});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("builtin,vector,idx,item,res", [(b, *a) for b, a in itertools.product(
        ['addrow', 'addcol'],
        [
            ("Vector[]", "0", "1.", "Vector[1.]"),
            ("Vector[1.]", "0", "0.", "Vector[0., 1.]"),
            ("Vector[1.]", "1", "2.", "Vector[1., 2.]"),
            ("Vector[1., 2., 4.]", "2", "3.", "Vector[1., 2., 3., 4.]"),
            ("Vector[1., 2., 4.]", "0", "0.", "Vector[0., 1., 2., 4.]"),
            ("Vector[1., 2., 4.]", "3", "5.", "Vector[1., 2., 4., 5.]"),
        ]
    )])
    def test_add_row_add_col(self, compiler_bin, builtin, vector, idx, item, res):
        prog = inspect.cleandoc(f"""
            {builtin}({vector}, {idx}, {item});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')


class TestMatrixInterpreterSuccess:
    @pytest.mark.parametrize("matrix,res", [
        ("Matrix[[]]", "Matrix[[]]"),
        ("Matrix[[1.]]", "Matrix[[1.]]"),
        ("Matrix[[1., 2., 3.]]", "Matrix[[1.,2.,3.]]"),
        ("Matrix[[1.], [2.], [3.]]", "Matrix[[1.],[2.],[3.]]"),
        ("Matrix[[1., 2.], [3., 4.]]", "Matrix[[1.,2.],[3.,4.]]"),
        ("Matrix[[1., 2., 3.], [4., 5., 6.]]", "Matrix[[1.,2.,3.],[4.,5.,6.]]")
    ])
    def test_matrix_def(self, compiler_bin, matrix, res):
        prog = inspect.cleandoc(f'{matrix};')
        assert "".join(run(compiler_bin, prog).split()).startswith(f"SUCCESS:{res}")

    @pytest.mark.parametrize("matrix,res", [
        ("Matrix[[1]]", "Matrix[[1.]]"),
        ("Matrix[[1, 2, 3]]", "Matrix[[1.,2.,3.]]"),
        ("Matrix[[1], [2], [3]]", "Matrix[[1.],[2.],[3.]]"),
        ("Matrix[[1, 2], [3, 4]]", "Matrix[[1.,2.],[3.,4.]]"),
    ])
    def test_matrix_int_coercion(self, compiler_bin, matrix, res):
        prog = inspect.cleandoc(f'{matrix};')
        assert "".join(run(compiler_bin, prog).split()).startswith(f"SUCCESS:{res}")

    def test_matrix_reduction(self, compiler_bin):
        prog = inspect.cleandoc('Matrix[[4. + 4., 3. * 3.], [2. / 2., 1. - 1.]];')
        assert "".join(run(compiler_bin, prog).split()).startswith(
            "SUCCESS:Matrix[[8.,9.],[1.,0.]]")

    @pytest.mark.parametrize("binop,res", [
        ("+", "Matrix[[2.,4.],[6.,8.]]"),
        ("-", "Matrix[[0.,0.],[0.,0.]]"),
        ("*", "Matrix[[1.,4.],[9.,16.]]"),
        ("/", "Matrix[[1.,1.],[1.,1.]]")
    ])
    def test_binop_matrix(self, compiler_bin, binop, res):
        prog = inspect.cleandoc(f"""
            Matrix[[1, 2], [3, 4]] {binop} Matrix[[1., 2.], [3., 4.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("matrix,res", [
        ("Matrix[[]]", "Matrix[[]]"),
        ("Matrix[[1.]]", "Matrix[[2.]]"),
        ("Matrix[[1., 2., 3.]]", "Matrix[[2.,4.,6.]]"),
        ("Matrix[[1.], [2.], [3.]]", "Matrix[[2.],[4.],[6.]]"),
    ])
    def test_binop_matrix_edge_cases(self, compiler_bin, matrix, res):
        prog = inspect.cleandoc(f"""
            {matrix} + {matrix};
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    def test_matrix_multiply_empty(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[]] @ Matrix[[]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:Matrix[[]]')

    def test_matrix_multiply_singletons(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[2.]] @ Matrix[[6.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:Matrix[[12.]]')

    def test_matrix_multiply_singleton_and_single_dim(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[2.]] @ Matrix[[2., 3., 4.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:Matrix[[4.,6.,8.]]')

    def test_matrix_multiply_inner_product(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[2., 3., 4.]] @ Matrix[[2.], [3.], [4.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:Matrix[[29.]]')

    def test_matrix_multiply_outer_product(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[2.], [3.], [4.]] @ Matrix[[2., 3., 4.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(
            f'SUCCESS:Matrix[[4.,6.,8.],[6.,9.,12.],[8.,12.,16.]]')

    def test_matrix_multiply_square(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1., 2.], [3., 4.]] @ Matrix[[5., 6.], [7., 8.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(
            f'SUCCESS:Matrix[[19.,22.],[43.,50.]]')

    def test_matrix_multiply_diff_dims(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1., 2., 3.], [1., 2., 3.]] @ Matrix[[6., 7.], [4., 5.], [2., 3.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(
            f'SUCCESS:Matrix[[20.,26.],[20.,26.]]')

    def test_matrix_stress_test_dims(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1., 2., 3., 4., 5., 6., 7., 8., 9., 10.]] @ Matrix[[1., 2.], [3., 4.], [5., 6.],
                [7., 8.], [9., 10.], [11., 12.], [13., 14.], [15., 16.], [17., 18.], [19., 20.]];
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:Matrix[[715.,770.]]')

    @pytest.mark.parametrize("matrix,row,res", [
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[1.]"),
        ("Matrix[[1.], [2.], [3.]]", "2", "Vector[3.]"),
        ("Matrix[[1., 2., 3.]]", "0", "Vector[1.,2.,3.]"),
        ("Matrix[[1., 2., 3.], [4., 5., 6.]]", "1", "Vector[4.,5.,6.]")
    ])
    def test_row_accessor(self, compiler_bin, matrix, row, res):
        prog = inspect.cleandoc(f'{matrix}[{row},];')
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("matrix,col,res", [
        ("Matrix[[1., 2., 3.]]", "0", "Vector[1.]"),
        ("Matrix[[1., 2., 3.]]", "2", "Vector[3.]"),
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[1.,2.,3.]"),
        ("Matrix[[1., 2., 3.], [4., 5., 6.]]", "1", "Vector[2.,5.]")
    ])
    def test_col_accessor(self, compiler_bin, matrix, col, res):
        prog = inspect.cleandoc(f'{matrix}[,{col}];')
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("matrix,row,col,res", [
        ("Matrix[[1.]]", "0", "0", "1."),
        ("Matrix[[1., 2., 3.]]", "0", "1", "2."),
        ("Matrix[[1.], [2.], [3.]]", "1", "0", "2."),
        ("Matrix[[1., 2.], [3., 4.]]", "0", "1", "2."),
        ("Matrix[[1., 2.], [3., 4.]]", "1", "0", "3."),
        ("Matrix[[1., 2.], [3., 4.], [5., 6.]]", "2", "1", "6."),
        ("Matrix[[1., 2., 3.], [4., 5., 6.]]", "1", "2", "6."),
    ])
    def test_elem_accessor(self, compiler_bin, matrix, row, col, res):
        prog = inspect.cleandoc(f'{matrix}[{row},{col}];')
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("matrix,res", [
        ("Matrix[[1.]]", "1"),
        ("Matrix[[1., 2., 3.]]", "1"),
        ("Matrix[[1.], [2.], [3.]]", "3"),
        ("Matrix[[1., 1.], [2., 2.], [3., 3.]]", "3"),
        ("Matrix[[]]", "0")
    ])
    def test_num_rows(self, compiler_bin, matrix, res):
        prog = inspect.cleandoc(f"""
            numrows({matrix});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("matrix,res", [
        ("Matrix[[1.]]", "1"),
        ("Matrix[[1.], [2.], [3.]]", "1"),
        ("Matrix[[1., 2., 3.]]", "3"),
        ("Matrix[[1., 1.], [2., 2.], [3., 3.]]", "2"),
        ("Matrix[[]]", "0")
    ])
    def test_num_cols(self, compiler_bin, matrix, res):
        prog = inspect.cleandoc(f"""
            numcols({matrix});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("matrix,res", [
        ("Matrix[[1.]]", "1."),
        ("Matrix[[1.], [2.], [3.]]", "6."),
        ("Matrix[[1., 2., 3.]]", "6."),
        ("Matrix[[1., 1.], [2., 2.], [3., 3.]]", "12."),
        ("Matrix[[]]", "0.")
    ])
    def test_sum(self, compiler_bin, matrix, res):
        prog = inspect.cleandoc(f"""
            sum({matrix});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    @pytest.mark.parametrize("vector,idx,item,res", [
        ("Matrix[[]]", "0", "Vector[]", "Matrix[[]]"),
        ("Matrix[[]]", "0", "Vector[1.]", "Matrix[[1.]]"),
        ("Matrix[[]]", "0", "Vector[1., 2., 3.]", "Matrix[[1.,2.,3.]]"),
        ("Matrix[[1.]]", "0", "Vector[0.]", "Matrix[[0.],[1.]]"),
        ("Matrix[[1.]]", "1", "Vector[2.]", "Matrix[[1.],[2.]]"),
        ("Matrix[[1., 2., 3.]]", "0", "Vector[-2., -1., 0.]",
            "Matrix[[-2.,-1.,0.],[1.,2.,3.]]"),
        ("Matrix[[1., 2., 3.]]", "1", "Vector[4., 5., 6.]",
            "Matrix[[1.,2.,3.],[4.,5.,6.]]"),
        ("Matrix[[1.], [2.], [4.]]", "0", "Vector[0.]", "Matrix[[0.],[1.],[2.],[4.]]"),
        ("Matrix[[1.], [2.], [4.]]", "2", "Vector[3.]", "Matrix[[1.],[2.],[3.],[4.]]"),
        ("Matrix[[1.], [2.], [4.]]", "3", "Vector[5.]", "Matrix[[1.],[2.],[4.],[5.]]"),
    ])
    def test_add_row(self, compiler_bin, vector, idx, item, res):
        prog = inspect.cleandoc(f"""
            addrow({vector}, {idx}, {item});
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')

    @pytest.mark.parametrize("vector,idx,item,res", [
        ("Matrix[[]]", "0", "Vector[]", "Matrix[[]]"),
        ("Matrix[[]]", "0", "Vector[1.]", "Matrix[[1.]]"),
        ("Matrix[[]]", "0", "Vector[1., 2., 3.]", "Matrix[[1.],[2.],[3.]]"),
        ("Matrix[[1.]]", "0", "Vector[0.]", "Matrix[[0.,1.]]"),
        ("Matrix[[1.]]", "1", "Vector[2.]", "Matrix[[1.,2.]]"),
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[-2.,-1.,0.]",
            "Matrix[[-2.,1.],[-1.,2.],[0.,3.]]"),
        ("Matrix[[1.], [2.], [3.]]", "1", "Vector[4.,5.,6.]",
            "Matrix[[1.,4.],[2.,5.],[3.,6.]]"),
        ("Matrix[[1., 2., 4.]]", "0", "Vector[0.]", "Matrix[[0.,1.,2.,4.]]"),
        ("Matrix[[1., 2., 4.]]", "2", "Vector[3.]", "Matrix[[1.,2.,3.,4.]]"),
        ("Matrix[[1., 2., 4.]]", "3", "Vector[5.]", "Matrix[[1.,2.,4.,5.]]")
    ])
    def test_add_col(self, compiler_bin, vector, idx, item, res):
        prog = inspect.cleandoc(f"""
            addcol({vector}, {idx}, {item});
        """)
        assert "".join(run(compiler_bin, prog).split()).startswith(f'SUCCESS:{res}')


class TestDLangBaseInterpreterError:
    @pytest.mark.parametrize("e1,e2", [
        ("10", "0"),
        ("0", "0"),
        ("Vector[10, 10, 10]", "Vector[0, 0, 0]"),
        ("Vector[10, 10, 10]", "Vector[10, 0, 10]"),
    ])
    def test_zero_div(self, compiler_bin, e1, e2):
        prog = inspect.cleandoc(f'{e1} / {e2};')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("binop", ["+", "-", "*", "/"])
    def test_vec_size_mismatch(self, compiler_bin, binop):
        prog = inspect.cleandoc(f'Vector[10, 12] {binop} Vector[4, 8, 12];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("idx", ["-1", "3"])
    def test_row_accessor_out_of_bounds(self, compiler_bin, idx):
        prog = inspect.cleandoc(f'Vector[10, 10, 10][{idx},];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_row_accessor_empty_vec(self, compiler_bin):
        prog = inspect.cleandoc('Vector[][0,];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("idx", ["-1", "3"])
    def test_col_accessor_out_of_bounds(self, compiler_bin, idx):
        prog = inspect.cleandoc(f'Vector[10, 10, 10][,{idx}];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_col_accessor_empty_vec(self, compiler_bin):
        prog = inspect.cleandoc('Vector[][,0];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("builtin,vector,idx", [(b, *a) for b, a in itertools.product(
        ['addrow', 'addcol'],
        [
            ("Vector[]", "-1"),
            ("Vector[]", "1"),
            ("Vector[1.]", "-1"),
            ("Vector[1.]", "2"),
            ("Vector[1., 2., 4.]", "-1"),
            ("Vector[1., 2., 4.]", "4"),
        ]
    )])
    def test_add_row_add_col_bad_idx(self, compiler_bin, builtin, vector, idx):
        prog = inspect.cleandoc(f"""
            {builtin}({vector}, {idx}, 1.);
        """)
        assert run(compiler_bin, prog).startswith('EVAL ERROR')


class TestMatrixInterpreterError:
    @pytest.mark.parametrize("e1,e2", [
        ("Matrix[[1, 1], [1, 1]]", "Matrix[[0, 1], [1, 1]]"),
        ("Matrix[[1, 1], [1, 1]]", "Matrix[[1, 0], [1, 1]]"),
        ("Matrix[[1, 1], [1, 1]]", "Matrix[[1, 1], [0, 1]]"),
        ("Matrix[[1, 1], [1, 1]]", "Matrix[[1, 1], [1, 0]]"),
        ("Matrix[[1, 1], [1, 1]]", "Matrix[[0, 0], [0, 0]]"),
        ("Matrix[[1, 1], [1, 1]]", "Matrix[[0, 1], [0, 0]]")
    ])
    def test_zero_div(self, compiler_bin, e1, e2):
        prog = inspect.cleandoc(f'{e1} / {e2};')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_matrix_diff_row_vec_sizes(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1], [1, 1], [], [1, 1, 1, 1]];
        """)
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("binop", ["+", "-", "*", "/"])
    def test_matrix_binop_size_mismatch(self, compiler_bin, binop):
        prog = inspect.cleandoc(f"""
            Matrix[[1, 1], [1, 1]] {binop} Matrix[[1, 1]];
        """)
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_matrix_matmul_size_mismatch_1(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1, 1]] @ Matrix[[1, 1]];
        """)
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_matrix_matmul_size_mismatch_2(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1]] @ Matrix[[1], [1]];
        """)
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_matrix_matmul_size_mismatch_3(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1, 1], [1, 1]] @ Matrix[[1, 1], [1, 1], [1, 1]];
        """)
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("idx", ["-1", "3"])
    def test_row_accessor_out_of_bounds(self, compiler_bin, idx):
        prog = inspect.cleandoc(f'Matrix[[1, 1], [1, 1]][{idx},];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_row_accessor_empty_matrix(self, compiler_bin):
        prog = inspect.cleandoc('Matrix[[]][0,];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("idx", ["-1", "3"])
    def test_col_accessor_out_of_bounds(self, compiler_bin, idx):
        prog = inspect.cleandoc(f'Matrix[[1, 1], [1, 1]][,{idx}];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_col_accessor_empty_matrix(self, compiler_bin):
        prog = inspect.cleandoc('Matrix[[]][,0];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("row,col", [
        ("2", "1"),
        ("1", "2"),
        ("-1", "-1"),
        ("2", "2"),
    ])
    def test_elem_accessor_failure(self, compiler_bin, row, col):
        prog = inspect.cleandoc(f'Matrix[[1, 1], [1, 1]][{row},{col}];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    def test_elem_accessor_empty_matrix(self, compiler_bin):
        prog = inspect.cleandoc('Matrix[[]][0,0];')
        assert run(compiler_bin, prog).startswith("EVAL ERROR")

    @pytest.mark.parametrize("matrix,idx,vector", [
        ("Matrix[[]]", "-1", "Vector[]"),
        ("Matrix[[]]", "1", "Vector[]"),
        ("Matrix[[1.]]", "-1", "Vector[1.]"),
        ("Matrix[[1.]]", "2", "Vector[1.]"),
        ("Matrix[[1., 2., 3.]]", "-1", "Vector[1., 2., 3.]"),
        ("Matrix[[1., 2., 3.]]", "2", "Vector[1., 2., 3.]"),
        ("Matrix[[1.], [2.], [3.]]", "-1", "Vector[4.]"),
        ("Matrix[[1.], [2.], [3.]]", "4", "Vector[4.]"),
    ])
    def test_add_row_bad_idx(self, compiler_bin, matrix, idx, vector):
        prog = inspect.cleandoc(f"""
            addrow({matrix}, {idx}, {vector});
        """)
        assert run(compiler_bin, prog).startswith('EVAL ERROR')

    @pytest.mark.parametrize("matrix,idx,vector", [
        ("Matrix[[1.]]", "0", "Vector[]"),
        ("Matrix[[1.]]", "0", "Vector[1., 2.]"),
        ("Matrix[[1., 2., 3.]]", "0", "Vector[1., 2.]"),
        ("Matrix[[1., 2., 3.]]", "0", "Vector[1., 2., 3., 4.]"),
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[]"),
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[4., 5.]"),
    ])
    def test_add_row_bad_size(self, compiler_bin, matrix, idx, vector):
        prog = inspect.cleandoc(f"""
            addrow({matrix}, {idx}, {vector});
        """)
        assert run(compiler_bin, prog).startswith('EVAL ERROR')

    @pytest.mark.parametrize("matrix,idx,vector", [
        ("Matrix[[]]", "-1", "Vector[]"),
        ("Matrix[[]]", "1", "Vector[]"),
        ("Matrix[[1.]]", "-1", "Vector[1.]"),
        ("Matrix[[1.]]", "2", "Vector[]"),
        ("Matrix[[1.], [2.], [3.]]", "-1", "Vector[1., 2., 3.]"),
        ("Matrix[[1.], [2.], [3.]]", "2", "Vector[1., 2., 3.]"),
        ("Matrix[[1., 2., 3.]]", "-1", "Vector[4.]"),
        ("Matrix[[1., 2., 3.]]", "4", "Vector[4.]"),
    ])
    def test_add_col_bad_idx(self, compiler_bin, matrix, idx, vector):
        prog = inspect.cleandoc(f"""
            addcol({matrix}, {idx}, {vector});
        """)
        assert run(compiler_bin, prog).startswith('EVAL ERROR')

    @pytest.mark.parametrize("matrix,idx,vector", [
        ("Matrix[[1.]]", "0", "Vector[]"),
        ("Matrix[[1.]]", "0", "Vector[1., 2.]"),
        ("Matrix[[1., 2., 3.]]", "0", "Vector[]"),
        ("Matrix[[1., 2., 3.]]", "0", "Vector[4., 5.]"),
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[1., 2.]"),
        ("Matrix[[1.], [2.], [3.]]", "0", "Vector[1., 2., 3., 4.]"),
    ])
    def test_add_col_bad_size(self, compiler_bin, matrix, idx, vector):
        prog = inspect.cleandoc(f"""
            addcol({matrix}, {idx}, {vector});
        """)
        assert run(compiler_bin, prog).startswith('EVAL ERROR')
