import matplotlib.pyplot as plt
import pandas as pd
import sys


def main():
    argv = sys.argv[1:]
    nplots = len(argv) // 2

    fig, axes = plt.subplots(1, nplots, sharey=True, figsize=(nplots * 5, 5))

    for i in range(nplots):
        df = pd.read_csv(argv[i * 2])
        name = argv[i * 2 + 1]
        df = df.pivot(
            index='num_threads',
            values='throughput',
            columns='write_frac',
        )
        ax = axes[i]
        df.plot(ax=ax, legend=i == 0)
        ax.set_ylabel('Throughput')
        ax.set_xlabel('Number of threads')
        ax.set_title(name)

    plt.tight_layout()
    plt.savefig('bench.png')


if __name__ == '__main__':
    main()
