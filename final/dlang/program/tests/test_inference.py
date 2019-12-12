import inspect
import itertools
import os

import pytest

from test_utils import run_interpreter as run


BASE_DIR = os.path.dirname(__file__)


@pytest.fixture()
def compiler_bin(pytestconfig):
    return os.path.join(BASE_DIR, "..", pytestconfig.getoption("compiler_bin"))


class TestTypeInferenceSuccess:
    @pytest.mark.parametrize("target", [
        "10",
        "10.",
        "Vector[10.]"
    ])
    def test_single_arg_inference_no_constraints(self, compiler_bin, target):
        prog = inspect.cleandoc(f"""
            def f(a) {{
                a;
            }}
            f({target});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {target}')

    @pytest.mark.parametrize("t1,t2,res", [
        ("10.", "5.", "15."),
        ("Vector[10.]", "Vector[5.]", "Vector[15.]")
    ])
    def test_single_arg_inference_with_binop_constraints(self, compiler_bin, t1, t2, res):
        prog = inspect.cleandoc(f"""
            def f(a) {{
                a + {t2};
            }}
            f({t1});
        """)
        assert run(compiler_bin, prog).startswith(f'SUCCESS: {res}')

    def test_single_arg_inference_with_row_col_accessor_constraints(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a) {
                a[0,];
            }
            f(Vector[10.]);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 10.')

    def test_single_arg_inference_with_elem_accessor_constraints(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a) {
                a[0,0];
            }
            f(Matrix[[10.]]);
        """)
        assert run(compiler_bin, prog).startswith('SUCCESS: 10.')

class TestTypeInferenceError:
    def test_func_signature_rebinding(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a) {
                a;
            }
            f(1);
            f(1.0);
        """)
        assert run(compiler_bin, prog).find("ERROR") != -1

    def test_incompatible_binop(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a, b) {
                a + b;
            }
            f(1, Vector[1.]);
        """)
        assert run(compiler_bin, prog).find("ERROR") != -1

    def test_incompatible_elem_accessor(self, compiler_bin):
        prog = inspect.cleandoc("""
            def f(a) {
                a[1, 1];
            }
            f(Vector[5]);
        """)
        assert run(compiler_bin, prog).find("ERROR") != -1
