import os
import subprocess
import uuid


def run_lexer_parser(compiler_bin, prog):
    file_name = f'/tmp/{str(uuid.uuid4())}.dl'
    with open(file_name, 'w') as f:
        f.write(prog)
    result = subprocess.check_output([compiler_bin, file_name, "-lp"]) \
                     .decode('UTF-8').strip()
    os.remove(file_name)
    return result


def run_typechecker(compiler_bin, prog):
    file_name = f'/tmp/{str(uuid.uuid4())}.dl'
    with open(file_name, 'w') as f:
        f.write(prog)
    result = subprocess.check_output([compiler_bin, file_name, "-t"]) \
                     .decode('UTF-8').strip()
    os.remove(file_name)
    return result


def run_interpreter(compiler_bin, prog):
    file_name = f'/tmp/{str(uuid.uuid4())}.dl'
    with open(file_name, 'w') as f:
        f.write(prog)
    result = subprocess.check_output([compiler_bin, file_name]) \
                     .decode('UTF-8').strip()
    os.remove(file_name)
    return result
