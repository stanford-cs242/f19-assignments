def pytest_addoption(parser):
    parser.addoption("--compiler_bin", action="store", default="main.native")
