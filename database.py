# Nathan Holmes-King
# 2024-04-11

import csv
import mne
import os
import sys

"""
WORK IN PROGRESS.

Command-line arguments:
1. CSV file to write data to
2. folder with EDF files
3. name of reviewer

PEP-8 compliant.
"""


def main(fname, folder, rn):
    try:
        infile = open(fname, 'r')
        infile.close()
        infile = open(fname, 'a')
        wrt = csv.writer(infile)
    except FileNotFoundError:
        infile = open(fname, 'w')
        wrt = csv.writer(infile)
        wrt.writerow(['Reviewer', 'File', 'Channel', 'Spikes'])
    for f in os.listdir(folder):
        try:
            raw = mne.io.read_raw_edf(folder + '/' + f, preload=True,
                                      verbose='ERROR')
        except TypeError:
            continue
        except NotImplementedError:
            continue
        except ValueError:
            continue
        i = 0
        while i < len(raw.ch_names):
            print(f, raw.ch_names[i])  # TEMP
            s = input('Spikes? ')
            if len(s) > 0 and s[0].lower() in ['t', 'y']:
                wrt.writerow([rn, f, raw.ch_names[i], True])
            elif len(s) > 0 and s[0].lower() in ['f', 'n']:
                wrt.writerow([rn, f, raw.ch_names[i], False])
            else:
                print('ERROR! Invalid response.')
                i -= 1
            i += 1
    infile.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
