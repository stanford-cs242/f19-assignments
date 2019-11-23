import pandas as pd
import argparse

GRADE_RANGE = [(.75, 1.), (.50, .8), (.30, .6), (.20, .4)]


def main(studentsol, refsol):
    student_df = pd.read_csv(studentsol)
    ref_df = pd.read_csv(refsol)

    total = 0
    count = 0
    for num_threads in range(1, 9):
        for write_frac in [0.02, 0.2, 0.4]:
            student_throughput = student_df[
                (student_df.num_threads == num_threads)
                & (student_df.write_frac == write_frac)].throughput
            ref_throughput = ref_df[(ref_df.num_threads == num_threads)
                                    & (ref_df.write_frac == write_frac)].throughput
            frac = student_throughput / ref_throughput
            grade = 0.
            for (min_frac, cur_grade) in GRADE_RANGE:
                if frac.iloc[0] > min_frac:
                    grade = cur_grade
                    break
            total += grade
            count += 1

    print('Your performance grade: {}'.format(int(total / count * 100)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute final grade')
    parser.add_argument('studentsol', help='CSV for student solution benchmark')
    parser.add_argument('refsol', help='CSV for reference solution benchmark')
    args = parser.parse_args()
    main(args.studentsol, args.refsol)
