# Nathan Holmes-King
# 2024-02-14

import quickspikes as qs
import mne
import sys
import os
import csv
import scipy
import numpy as np

"""
WORK IN PROGRESS.

Command-line arguments:
1. Directory

PEP-8 compliant.
"""


bad = {'IED-41.EDF': ['EEG C3-M2']}


def findSpikesQS(raw, f, wrt):
    nch = len(raw.ch_names)
    srate = int(raw.info['sfreq'])
    data, times = raw.get_data(return_times=True)
    nch, nt = data.shape
    det = qs.detector(1000, 30)  # VERIFY
    for i in range(nch):
        if len(raw.ch_names[i]) > 2 and raw.ch_names[i][:3] == 'EEG':
            tm = det.send(data[i])
            wrt.writerow([f, raw.ch_names[i], len(tm)])


def findSpikesSciPy(raw, f, wrt, height=None, thresh=None, prom=None):
    nch = len(raw.ch_names)
    srate = int(raw.info['sfreq'])
    data, times = raw.get_data(return_times=True)
    rl = []
    for i in range(nch):
        if len(raw.ch_names[i]) > 2 and raw.ch_names[i][:3] == 'EEG':
            peaks, _ = scipy.signal.find_peaks(data[i], height=height,
                                               threshold=thresh,
                                               prominence=prom)
            wrt.writerow([f, raw.ch_names[i], len(peaks)])
            if (f not in bad) or (raw.ch_names[i] not in bad[f]):
                rl.append(len(peaks))
            """
            outfile = open('spikes_' + f + '_' + raw.ch_names[i] + '.svg', 'w')
            outfile.write('<!DOCTYPE svg>\n<svg width="100000" height="2000" '
                          'xmlns="http://www.w3.org/2000/svg">')
            for j in range(len(data[i])-1):
                if j > 1e5:
                    break
                outfile.write('\n\t<line x1="' + str(j) + '" x2="' + str(j+1) +
                              '" y1="' + str(1e3 - data[i][j]*5e5) + '" y2="' +
                              str(1e3 - data[i][j+1]*5e5) +
                              '" stroke="#000"/>')
            for j in range(len(peaks)):
                if peaks[j] > 1e5:
                    break
                outfile.write('\n\t<circle cx="' + str(peaks[j]) + '" cy="' +
                              str(1e3 - data[i][peaks[j]]*5e5) +
                              '" r="5" fill="#f00" stroke="#000"/>')
            outfile.write('\n</svg>')
            outfile.close()
            """
    return rl


def main(indir, outf):
    tout = open(outf, 'w')
    rit = csv.writer(tout)
    rit.writerow(['Height', 'Threshold', 'Prominence', 'Cutoff value',
                  'Accuracy'])
    for h in [0, 1e-4, 2e-4, 5e-4, 1e-3]:
        for t in [0, 1e-4, 2e-4, 5e-4, 1e-3]:
            for p in [0, 1e-4, 2e-4, 5e-4, 1e-3]:
                if t > p:
                    continue
                dic = {True: [], False: []}
                outp = open('spikes_' + str(h) + '_' + str(t) + '_' + str(p) +
                            '.csv', 'w')
                wrt = csv.writer(outp)
                wrt.writerow(['Height', 'Channel', 'Number of spikes'])
                for f in os.listdir(indir):
                    try:
                        raw = mne.io.read_raw_edf(indir + '/' + f,
                                                  preload=True,
                                                  verbose='ERROR')
                    except TypeError:
                        continue
                    except NotImplementedError:
                        continue
                    except ValueError:
                        continue
                    rl = findSpikesSciPy(raw, f, wrt, height=h, thresh=t,
                                         prom=p)
                    print('DONE', h, t, p, f)
                    if int(f.split('.')[0].split('-')[1]) < 40:
                        dic[True].append(max(rl))
                    else:
                        dic[False].append(max(rl))
                outp.close()
                max_thresh = (0, 0)
                al = np.array(dic[True] + dic[False])
                al = np.unique(al)
                al.sort()
                dt = np.array(dic[True])
                df = np.array(dic[False])
                for v in al:
                    acc = ((len(dt[dt >= v]) + len(df[df < v])) /
                           (len(dt) + len(df)))
                    if acc > max_thresh[1]:
                        max_thresh = (v, acc)
                rit.writerow([h, t, p, max_thresh[0], max_thresh[1]])
    tout.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
