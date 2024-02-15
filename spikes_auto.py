# Nathan Holmes-King
# 2024-02-14

import quickspikes as qs
import mne
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
        print(f)
        for i in range(nch):
            tm = det.send(data[i])
            print(raw.ch_names[i], len(tm))
        print('----')


if __name__ == '__main__':
    main(sys.argv[1])
