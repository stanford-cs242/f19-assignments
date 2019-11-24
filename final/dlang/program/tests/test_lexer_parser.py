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

    @pytest.mark.parametrize("binop", ["+", "*", "/", "-"])
    def test_binops(self, compiler_bin, binop):
        prog = inspect.cleandoc(f'3 {binop} -3;')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("flt,binop", itertools.product(
        ['3.', '3.1', '3.1231'],
        ["+", "*", "/", "-"]
    ))
    def test_binops_with_floats(self, compiler_bin, flt, binop):
        prog = inspect.cleandoc(f'{flt} {binop} -{flt};')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    @pytest.mark.parametrize("n1,n2", [
        ('3.12', '3'),
        ('3', '3.12')
    ])
    def test_binops_mixed_num_types(self, compiler_bin, n1, n2):
        prog = inspect.cleandoc(f'{n1} + {n2};')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_variables(self, compiler_bin):
        prog = inspect.cleandoc("""
            x = 4;
            y = 10;
            func(x, y);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_funcs(self, compiler_bin):
        prog = inspect.cleandoc("""
            def func1(a: int, b: int, c: int) {
              a + b + c;
            }

            def func2(a: int, b: int, c: int) {
              b * 2;
              a + b + c;
            }

            func2(10, 5, 1);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_builtins(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            numrows(Vector[1, 2, 3, 4]);
            numcols(Vector[1, 2, 3, 4]);
            addrow(Vector[1, 2, 3, 4], 0, 0);
            addcol(Vector[1, 2, 3, 4], 0, 0);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors(self, compiler_bin):
        prog = inspect.cleandoc('Vector[15, 10, 23, 1];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors_mixed_num_types(self, compiler_bin):
        prog = inspect.cleandoc('Vector[15, 10., 23.0, 1.1234];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_vectors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc('Vector[5 + 5, 5 - 5, 5 * 5, 5 / 5];')
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1, 2, 3, 4][3,];
            Vector[1, 2, 3, 4][,2];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Vector[1, 2, 3, 4][1 + 1,];
            Vector[1, 2, 3, 4][,1 + 1];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")


class TestMatrixLexerParserSuccess:
    def test_builtins(self, compiler_bin):
        prog = inspect.cleandoc(f"""
            numrows(Matrix[[1, 2], [3, 4]]);
            numcols(Matrix[[1, 2], [3, 4]]);
            addrow(Matrix[[1, 2], [3, 4]], 0, Vector[-1, 0]);
            addcol(Matrix[[1, 2], [3, 4]], 0, Vector[2, 4]);
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[15, 10, 23], [15, 10, 23]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices_mixed_num_types(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[15.0, 10, 23.], [15, 10.1234, 23]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_matrices_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[5 / 5, 1 + 1], [4 - 1, 2 * 2]];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_accessors(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1, 2, 3], [4, 5, 6]][1,];
            Matrix[[1, 2, 3], [4, 5, 6]][,1];
            Matrix[[1, 2, 3], [4, 5, 6]][1, 1];
        """)
        assert run(compiler_bin, prog).startswith("SUCCESS")

    def test_accessors_with_exprs(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[[1, 2, 3], [4, 5, 6]][1 / 1,];
            Matrix[[1, 2, 3], [4, 5, 6]][, 1 / 1];
            Matrix[[1, 2, 3], [4, 5, 6]][1 / 1, 4 - 2];
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

    def test_trailing_binop(self, compiler_bin):
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

    def test_builtin_shadowing_override(self, compiler_bin):
        prog = inspect.cleandoc("""
            def numrows(t: Vector) {
                t[0,];
            }

            numrows(Vector[1, 2, 3, 4]) + 2;
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")


class TestMatrixLexerParserError:
    def test_one_dim_matrix(self, compiler_bin):
        prog = inspect.cleandoc("""
            Matrix[1, 2, 3]
        """)
        assert run(compiler_bin, prog).startswith("PARSE ERROR")
