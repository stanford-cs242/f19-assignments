import inspect
import itertools
import os

import pytest

from test_utils import run_lexer_parser as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestDLangBaseLexerParserSuccess:
    def test_comments(self, compiler_bin):
        prog = inspect.cleandoc("""
            (* There's a comment here with some invalid syntax! 3.x *)
            x = 3;
            x + 3;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_multiline_comments(self, compiler_bin):
        prog = inspect.cleandoc("""
            (* There's a comment here with some invalid syntax! 3.x
                and it even goes onto another line! *)
            x = 3;
            x + 3;
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("num", ["1", "1.", "1.0", "1.01", "1.2343"])
    def test_num(self, compiler_bin, num):
        prog = inspect.cleandoc(f'{num};')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("binop", ["+", "*", "/", "-"])
    def test_binops(self, compiler_bin, binop):
        prog = inspect.cleandoc(f'3 {binop} -3;')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_binops_expr(self, compiler_bin):
        prog = inspect.cleandoc('(3 * 2) + (2 + -1.8);')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_variables(self, compiler_bin):
        prog = inspect.cleandoc("""
            x = 4;
            y = 10;
            func(x, y);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_func_def_no_args(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f() {
              2;
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_func_def_single_arg(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int) {
              a;
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_func_def_multiple_args(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int, b: int) {
              a + b;
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_func_multiple_defs(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int) {
              a;
            }

            def g(a: int, b: int, c: int) {
              b * 2;
              a + b + c;
            }
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_func_app(self, compiler_bin):
        prog = inspect.cleandoc("""
            def g(a: int, b: int, c: int) {
              b * 2;
              a + b + c;
            }

            g(1, 2, 3);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize('builtin_call', [
        'numrows(Vector[1., 2., 3., 4.])',
        'numcols(Vector[1., 2., 3., 4.])',
        'addrow(Vector[1., 2., 3., 4.], 0, 0)',
        'addcol(Vector[1., 2., 3., 4.], 0, 0)',
        'sum(Vector[1., 2., 3., 4.])'
    ])
    def test_builtins(self, compiler_bin, builtin_call):
        prog = inspect.cleandoc(f'{builtin_call};')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize('vector', [
        'Vector[]',
        'Vector[15.]',
        'Vector[15., 10., 23.]',
    ])
    def test_vectors(self, compiler_bin, vector):
        prog = inspect.cleandoc(f'{vector};')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc('Vector[5 + 5, 5. - 5., 5.0 * 5.123, 5. / 5.];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_row_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1., 2., 3., 4.][3,];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_row_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1., 2., 3., 4.][1 + 1,];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_col_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1., 2., 3., 4.][,2];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_col_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1., 2., 3., 4.][,1 + 1];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")


class TestMatrixLexerParserSuccess:
    def test_matrices(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[15., 10., 23.], [15., 10., 23.]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5 / 5, 1.07 + 1.], [4.0 - 1., 2. * 2.]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_elem_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1., 2., 3.], [4., 5., 6.]][1, 1];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_elem_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1., 2., 3.], [4., 5., 6.]][1 / 1, 4 - 2];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_other_binops(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1., 2., 3.], [4., 5., 6.]] @ Matrix[[1.], [1.], [1.]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")


class TestDLangBaseLexerParserError:
    def test_no_semicolons(self, compiler_bin):
        prog = inspect.cleandoc("""
            func(10, x)
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_no_semicolons_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def func (a: int, b: int) {
              a + b
              2 * a
            }
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_missing_paren(self, compiler_bin):
        prog = inspect.cleandoc("""
            ((2 + 3) + 4;
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_trailing_semicolon_on_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def func (a: int, b: int) {
              a + b;
              2 * a;
            };
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_trailing_elemwise_binop(self, compiler_bin):
        prog = inspect.cleandoc("""
            5 + 2 - 2 /;
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_empty_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f () {};
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_inline_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a: int) {
                def g(b: int) {
                    a + b;
                }
                g;
            }
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_chained_assignment(self, compiler_bin):
        prog = inspect.cleandoc("""
            a = b = 5;
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_no_types_func(self, compiler_bin):
        prog = inspect.cleandoc("""
            def func (a, b) {
              a + b;
              2 * a;
            }
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_overriden_builtin(self, compiler_bin):
        prog = inspect.cleandoc("""
            def numcols (a: Vector) {
              0;
            }
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_builtin_shadowing_override(self, compiler_bin):
        prog = inspect.cleandoc("""
            def numrows(t: Vector) {
                t[0,];
            }

            numrows(Vector[1., 2., 3., 4.]) + 2;
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_accessor_no_comma(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1, 2, 3, 4][2];
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")


class TestMatrixLexerParserError:
    @pytest.mark.parametrize("matrix", ["Matrix[]", "Matrix[1., 2., 3.]"])
    def test_one_dim_matrix(self, compiler_bin, matrix):
        prog = inspect.cleandoc(f'{matrix};')
        assert run(compiler_bin, prog).startswith("PARSE ERROR")

    def test_trailing_other_binop(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1.]] @;
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")
