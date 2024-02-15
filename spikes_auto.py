# Nathan Holmes-King
# 2024-02-14

import quickspikes as qs
import sys
import os

"""
WORK IN PROGRESS.

Command-line arguments:
1. Directory

PEP-8 compliant.
"""


def main(indir):
    for f in os.listdir(indir):
        edf = open(f, 'r')
        det = qs.detector(1000, 30)  # VERIFY numbers
        samples = []  # TEMP
        times = det.send(samples)
        print(f, times)


if __name__ == '__main__':
    main(sys.argv[1])
