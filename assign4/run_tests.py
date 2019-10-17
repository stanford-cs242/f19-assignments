#!/usr/bin/env python

import argparse
import os
import subprocess
from collections import namedtuple

BASE_DIR = os.path.dirname(__file__)
SEPARATOR = '=' * 30

TestResult = namedtuple('TestResult', ['test_name', 'outcome', 'student_out', 'reference_out'])

def stringify_test_result(result):
    output = '' if result.outcome != 'failure' else \
        '\nYour output:\n{}\nReference output:\n{}'.format(
            '\t' + '\n\t'.join(result.student_out.split('\n')),
            '\t' + '\n\t'.join(result.reference_out.split('\n')),
        )
    return 'Test `{}`: {}.{}'.format(result.test_name, result.outcome.upper(), output)

def run_interpreter(interpreter, test_file):
    return subprocess.check_output([interpreter, test_file, '-v', '-t']) \
                .decode('UTF-8').strip().replace('\n\n', '\n')

def run_tests(student_bin, reference_bin, test_files, outfile=None):
    results = []
    succeeded = 0
    for test_file in test_files:
        test_name = os.path.basename(test_file)
        try:
            student_out = run_interpreter(student_bin, test_file)
            reference_out = run_interpreter(reference_bin, test_file) + ''
            if student_out == reference_out:
                results.append(TestResult(test_name, 'success', '', ''))
                succeeded += 1
            else:
                results.append(TestResult(test_name, 'failure', student_out, reference_out))
        except Exception as e:
            results.append(TestResult(test_name, 'error', '', ''))
        if outfile is None:
            print('{}\n{}'.format(SEPARATOR, stringify_test_result(results[-1])))

    if outfile is not None:
        with open(outfile, 'w') as f:
            for res in results:
                f.write(SEPARATOR + '\n' + stringify_test_result(res))

    print(SEPARATOR)
    if succeeded == len(results):
        print('ALL TESTS PASSED!')
    else:
        print('SOME TESTS FAILED. {}/{} PASSED.'.format(succeeded, len(results)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs test cases on your interpreter and compares with the reference interpreter.')
    parser.add_argument('--test_dir', default=os.path.join(BASE_DIR, 'tests'),
        type=os.path.abspath, help='Directory containing test files (should be .lam files)')
    parser.add_argument('--interpreter', default=os.path.join(BASE_DIR, 'main.native'),
        type=os.path.abspath, help='Location of your interpreter')
    parser.add_argument('--ref_interpreter', default=os.path.join(BASE_DIR, 'reference.sh'),
        type=os.path.abspath, help='Location of reference interpreter')
    parser.add_argument('--outfile', default=None, type=os.path.abspath,
        help='File to print test results to. If None (default), prints to stdout.')
    args = parser.parse_args()

    if not os.path.exists(args.interpreter):
        raise ValueError('Path to your interpreter ({}) not found. Please double check.'.format(args.interpreter))

    if not os.path.exists(args.ref_interpreter):
        raise ValueError('Path to reference interpreter ({}) not found. Please double check.'.format(args.ref_interpreter))

    if args.outfile is not None and not os.path.exists(os.path.dirname(args.outfile)):
        raise ValueError('Directory for outfile ({}) not found. Please double check.'.format(os.path.dirname(args.outfile)))

    if not os.path.exists(args.test_dir):
        raise ValueError('Directory for tests ({}) not found. Please double check.'.format(args.test_dir))

    tests = os.listdir(args.test_dir)
    tests = [os.path.join(args.test_dir, test_name) for test_name in tests \
        if os.path.splitext(test_name)[1] == '.lam']

    run_tests(args.interpreter, args.ref_interpreter, tests, args.outfile)
