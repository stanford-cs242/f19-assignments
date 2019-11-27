import inspect
import itertools
import os

import pytest

from test_utils import run_typechecker as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestDLangBaseTypecheckerSuccess:
    @pytest.mark.parametrize("num", ["1", "1.", "1.0", "1.01", "1.2343"])
    def test_nums(self, compiler_bin, num):
        prog = inspect.cleandoc(f'{num};')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("binop", ["+", "*", "/", "-"])
    def test_binops_scalar(self, compiler_bin, binop):
        prog = inspect.cleandoc(f'3 {binop} 3;')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_binops_floats(self, compiler_bin):
        prog = inspect.cleandoc('3.1 + 3.1;')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_binops_mixed_num_types(self, compiler_bin):
        prog = inspect.cleandoc('3 + 3.1;')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("expr", ["10", "5 + 5", "Vector[10.][0]"])
    def test_var(self, compiler_bin, expr):
        prog = inspect.cleandoc(f"""
            x = {expr};
            x + 2;
        """)

    @pytest.mark.parametrize("expr", ["10", "5 + 5", "Vector[10.][0,]"])
    def test_var_chaining(self, compiler_bin, expr):
        prog = inspect.cleandoc(f"""
            x = {expr};
            y = x;
            z = y;
            z + y + x + 2;
        """)

    def test_no_arg_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
                5;
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_single_arg_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int) {
                a;
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_multiple_arg_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: Vector, c: Vector) {
                a + b[,0] + c[0,];
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_no_arg_func_with_call(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
                5;
            }

            f() + 10;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_single_arg_func_with_call(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int) {
                a;
            }

            f(8) + 10;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_multiple_arg_func_with_call(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: Vector, c: Vector, d: float) {
                a + b[,0] + c[0,] + d;
            }

            f(5 + 5, Vector[10., 20.], Vector[10., 20.], 1.0) + 10;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_multiple_funcs(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float, b: Vector, c: Vector) {
                a + b[,0] + c[0,];
            }

            def g(a: float) {
                a * 2;
            }

            f(5 + 5.0, Vector[10., 20.], Vector[10., 20.]) + g(10.0);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_nested_func_calls(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: float) {
                a * 2;
            }

            def g(a: float, b: Vector, c: Vector) {
                f(a) + b[,0] + c[0,];
            }

            f(g(5 + 5.0, Vector[10., 20.], Vector[10., 20.])) + f(10.0);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_closure(self, compiler_bin):
        prog = inspect.cleandoc("""
            c = 10;

            def f(a: int, b: int) {
                a + b + c;
            }

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS')

    def test_shared_symbol_for_var_and_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def a(a: int) {
                a;
            }

            a = 10;
            a(a);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors(self, compiler_bin):
        prog = inspect.cleandoc('Vector[15., 10., 23.];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors_all_ints(self, compiler_bin):
        prog = inspect.cleandoc('Vector[15, 10, 23];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc('Vector[5. + 5.123, 5. * 2.0, 30 - 7, 10. / 10];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("binop", ["+", "*", "/", "-"])
    def test_binops_vectors(self, compiler_bin, binop):
        prog = inspect.cleandoc(f'Vector[15., 10.] {binop} Vector[15., 10.];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_col_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[15., 10.][,1] + 2;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_col_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[15., 10.][,1 / 1] + 2;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_row_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[15., 10.][1,] + 2;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_row_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[15., 10.][1 / 1,] + 2;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("builtin", ["numrows", "numcols", "sum"])
    def test_single_arg_builtins(self, compiler_bin, builtin):
        prog = inspect.cleandoc(f"""
            {builtin}(Vector[1, 2]);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("builtin", ["addrow", "addcol"])
    def test_triple_args_builtins(self, compiler_bin, builtin):
        prog = inspect.cleandoc(f"""
            {builtin}(Vector[0, 0], 0, 0);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_num_rows_num_cols_return(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f (a: int) {a;}

            v = Vector[1., 2., 3., 4.];
            f(numcols(v) + numrows(v));
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_sum_return(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f (a: float) {a;}

            v = Vector[1., 2., 3., 4.];
            f(sum(v));
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_add_row_add_col_return(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f (a: Vector) {a;}

            v = Vector[1., 2., 3., 4.];
            v = addrow(v, 0, 0.);
            v = addcol(v, 5, 5.);
            f(v);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_builtin_expr_args(self, compiler_bin):
        prog = inspect.cleandoc("""
            def make_vector() {
                t = Vector[];
                t = addrow(t, 0, 1);
                addrow(t, numrows(t), 2);
            }

            t = make_vector();
            addcol(t, numcols(t) + 0, 3);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")


class TestMatrixTypecheckerSuccess:
    def test_matrices(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[15., 10.1, 23.123, 1.], [15., 10., 23., 1.]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices_all_ints(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[15, 10], [15, 10]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices_mixed_num_types(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[15, 10.], [15.1, 10.1223]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5.12 / 5.12, 1. + 1.0], [4 - 1, 2. * 2]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("binop", ["+", "*", "/", "-"])
    def test_elemwise_binops_matrices(self, compiler_bin, binop):
        prog = inspect.cleandoc(f"""
            Matrix[[5., 10.], [15., 20.]] {binop} Matrix[[5., 10.], [15., 20.]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("binop", ["@"])
    def test_other_binops_matrices(self, compiler_bin, binop):
        prog = inspect.cleandoc(f"""
            Matrix[[5., 10.], [15., 20.]] {binop} Matrix[[5., 10.], [15., 20.]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_row_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5., 10.], [15., 20.]][1,] + Vector[100., 100.];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_row_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5., 10.], [15., 20.]][1 / 1,] + Vector[100., 100.];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_col_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5., 10.], [15., 20.]][,1] + Vector[100., 100.];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_col_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5., 10.], [15., 20.]][,1 / 1] + Vector[100., 100.];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_elem_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5., 10.], [15., 20.]][1,1] + 2.;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_elem_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5., 10.], [15., 20.]][0 + 1,1 / 1] + 2;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("builtin", ["numrows", "numcols", "sum"])
    def test_single_arg_builtins(self, compiler_bin, builtin):
        prog = inspect.cleandoc(f"""
            {builtin}(Matrix[[1., 2.], [3., 4.]]);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_num_rows_num_cols_return(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f (a: int) {a;}

            m = Matrix[[1., 2.], [3., 4.]];
            f(numcols(m) + numrows(m));
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_sum_return(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f (a: float) {a;}

            m = Matrix[[1., 2.], [3., 4.]];
            f(sum(m));
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_add_row_add_col_return(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f (a: Matrix) {a;}

            m = Matrix[[1., 2.], [3., 4.]];
            m = addrow(m, 0, Vector[-1., 0.]);
            m = addcol(m, 2, Vector[0.1, 2.1, 4.1]);
            f(m);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")


class TestDLangBaseTypecheckerError:
    @pytest.mark.parametrize("binop", ["+", "*", "/", "-"])
    def test_mismatched_binop(self, compiler_bin, binop):
        prog = inspect.cleandoc(f'3 {binop} Vector[3];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_missing_var(self, compiler_bin):
        prog = inspect.cleandoc("""
            y = 10;
            x + 2;
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_missing_var_in_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
                y + 2;
            }
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_bad_func_body(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: Vector, b: float) {
                a + b;
            }
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_duplicate_func_symbol(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
                10;
            }

            def f() {
                20;
            }

            f();
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_missing_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: Vector, b: Vector) {
                a + b;
            }

            g(1);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_bad_func_ordering(self, compiler_bin):
        prog = inspect.cleandoc("""
            def g(a: int) {
                f(a) + 2;
            }

            def f(a: int) {
                a;
            }

            g(10);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_binding_is_not_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            f = 10;
            f(1);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_func_wrong_arity(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            f(1);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_func_wrong_types(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b;
            }

            f(1, Vector[10.]);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_func_wrong_num_types(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: float) {
                a + b;
            }

            f(2.5, 1);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_bad_dynamic_scoping(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                c = a + b;
                c;
            }

            f(10, 5) + c;
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_late_closure(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
                a + b + c;
            }

            c = 10;

            f(5, 10);
        """)
        assert run(compiler_bin, prog).startswith('TYPE ERROR')

    def test_duplicated_arg_binding(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, a: int) {
                a + a;
            }
        """)
        assert run(compiler_bin, prog).startswith('TYPE ERROR')

    def test_vectors_bad_elems(self, compiler_bin):
        prog = inspect.cleandoc('Vector[1., 3., Vector[10.]];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("idx", ["1.0", "Vector[10.]"])
    def test_row_accessor_bad_index(self, compiler_bin, idx):
        prog = inspect.cleandoc(f'Vector[1., 3.][{idx},];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("idx", ["1.0", "Vector[10.]"])
    def test_col_accessor_bad_index(self, compiler_bin, idx):
        prog = inspect.cleandoc(f'Vector[1., 3.][,{idx}];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_col_accessor_bad_matrix(self, compiler_bin):
        prog = inspect.cleandoc('3[,2];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_row_accessor_bad_matrix(self, compiler_bin):
        prog = inspect.cleandoc('3[3,];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("builtin,args", itertools.product(
        ["numcols", "numrows", "addrow", "addcol", "sum"],
        [[], ["Vector[1, 2, 3, 4]", "10", "5", "6"]]
    ))
    def test_builtins_bad_arity(self, compiler_bin, builtin, args):
        prog = inspect.cleandoc(f"""
            {builtin}({', '.join(args)});
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_num_rows_bad_arg_type(self, compiler_bin):
        prog = inspect.cleandoc("""
            numrows(2);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_num_cols_bad_arg_type(self, compiler_bin):
        prog = inspect.cleandoc("""
            numcols(2);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    def test_sum_bad_arg_type(self, compiler_bin):
        prog = inspect.cleandoc("""
            sum(2);
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("arg2,arg3", [
        ("0.0", "0.0"),
        ("0", "Vector[10.]")
    ])
    def test_add_row_bad_arg_type(self, compiler_bin, arg2, arg3):
        prog = inspect.cleandoc(f"""
            addrow(Vector[1., 2.], {arg2}, {arg3});
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("arg2,arg3", [
        ("0.0", "0.0"),
        ("0", "Vector[10.]")
    ])
    def test_add_col_bad_arg_type(self, compiler_bin, arg2, arg3):
        prog = inspect.cleandoc(f"""
            addcol(Vector[1., 2.], {arg2}, {arg3});
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")


class TestMatrixTypecheckerError:
    @pytest.mark.parametrize("bad_elem", [
        "Matrix[[1.,1.]]",
        "Vector[10.]"
    ])
    def test_matrices_bad_elems(self, compiler_bin, bad_elem):
        prog = inspect.cleandoc(f"""
            Matrix[[1., 2.], [3., {bad_elem}]];
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("test_inputs,binop", itertools.product(
        list(itertools.permutations([
            "3", "Vector[3]", "Matrix[[10, 10], [10, 10]]"
        ], 2)),
        ["+", "*", "/", "-"]
    ))
    def test_mismatched_binop(self, compiler_bin, test_inputs, binop):
        prog = inspect.cleandoc(f'{test_inputs[0]} {binop} {test_inputs[1]};')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("row,col", [
        ("0.", "0"),
        ("Vector[10.]", "0"),
        ("Matrix[[10.]]", "0"),
        ("0", "0."),
        ("0", "Vector[10.]"),
        ("0", "Matrix[[10.]]"),
    ])
    def test_elem_accessor_bad_index(self, compiler_bin, row, col):
        prog = inspect.cleandoc(f"""
            Matrix[[1], [3]][{row}, {col}];
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("tensor", ["3", "3.0", "Vector[10, 20, 30]"])
    def test_elem_accessor_bad_matrix(self, compiler_bin, tensor):
        prog = inspect.cleandoc(f'{tensor}[3,4];')
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("args", [
        ["Vector[1, 2]", "0", "Matrix[[10]]"],
        ["Matrix[[1, 2], [3, 4]]", "0", "5"],
        ["Matrix[[1, 2], [3, 4]]", "0", "Matrix[[10]]"]
    ])
    def test_add_row_bad_arg_type(self, compiler_bin, args):
        prog = inspect.cleandoc(f"""
            addrow({', '.join(args)});
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")

    @pytest.mark.parametrize("args", [
        ["Vector[1, 2]", "0", "Matrix[[10]]"],
        ["Matrix[[1, 2], [3, 4]]", "0", "5"],
        ["Matrix[[1, 2], [3, 4]]", "0", "Matrix[[10]]"],
    ])
    def test_add_col_bad_arg_type(self, compiler_bin, args):
        prog = inspect.cleandoc(f"""
            addcol({', '.join(args)});
        """)
        assert run(compiler_bin, prog).startswith("TYPE ERROR")
