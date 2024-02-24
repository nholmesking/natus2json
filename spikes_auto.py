# Nathan Holmes-King
# 2024-02-14

import quickspikes as qs
import mne
import sys
import os
import csv

"""
WORK IN PROGRESS.

Command-line arguments:
1. Directory

PEP-8 compliant.
"""


def main(indir, outf):
    outp = open(outf, 'w')
    wrt = csv.writer(outp)
    wrt.writerow(['File', 'Channel', 'Number of spikes'])
    for f in os.listdir(indir):
        try:
            raw = mne.io.read_raw_edf(indir + '/' + f, preload=True,
                                      verbose='ERROR')
        except TypeError:
            continue
        except NotImplementedError:
            continue
        except ValueError:
            continue
        channelNames = raw.ch_names
        nch = len(channelNames)
        srate = int(raw.info['sfreq'])
        data, times = raw.get_data(return_times=True)
        nch, nt = data.shape
        det = qs.detector(1000, 30)
        for i in range(nch):
            tm = det.send(data[i])
            wrt.writerow([f, raw.ch_names[i], len(tm)])
    outp.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
