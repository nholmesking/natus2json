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
        wrt.writerow(['Reviewer', 'File', 'Channel', 'Start time', 'End time',
                      'Spikes'])
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
        data, times = raw.get_data(return_times=True)
        i = 0
        while i < len(raw.ch_names):
            j = 0
            while j < len(times):
                tr = (times[j], times[int(min(j+1e5, len(times)-1))])
                print(f, raw.ch_names[i], tr[0], tr[1])  # TEMP
                s = input('Spikes? ([T]rue / [F]alse / [B]ad data) ')
                if len(s) > 0 and s[0].lower() == 't':  # Spikes
                    wrt.writerow([rn, f, raw.ch_names[i], tr[0], tr[1], True])
                elif len(s) > 0 and s[0].lower() == 'f':  # No spikes
                    wrt.writerow([rn, f, raw.ch_names[i], tr[0], tr[1], False])
                elif len(s) > 0 and s[0].lower() == 'b':  # Bad data
                    wrt.writerow([rn, f, raw.ch_names[i], tr[0], tr[1], None])
                else:
                    print('ERROR! Invalid response.')
                    j -= 1e5
                j += 1e5
                j = int(j)
            i += 1
    infile.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
