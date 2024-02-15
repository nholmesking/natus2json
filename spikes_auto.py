# Nathan Holmes-King
# 2024-02-14

import quickspikes as qs
import sys
import os
from pydicom import dcmread

"""
WORK IN PROGRESS.

Command-line arguments:
1. Directory

PEP-8 compliant.
"""


def main(indir):
    for f in os.listdir(indir):
        if f[len(f)-4:] != '.dcm':
            continue
        ds = dcmread(indir + '/' + f, force=True)
        samples = []
        for n in range(len(ds.WaveformSequence)):
            a = ds.WaveformSequence[n]
            k = (a.WaveformBitsAllocated // a.NumberOfWaveformChannels) // 8
            for i in range(a.NumberOfWaveformChannels):
                for j in range(a.NumberOfWaveformSamples):
                    samples.append(a.WaveformData[j*a.WaveformBitsAllocated //
                                                  8+i*k:j *
                                                  a.WaveformBitsAllocated//8 +
                                                  i*k+k])
                det = qs.detector(1000, 30)  # VERIFY numbers
                times = det.send(samples)
                print(f, n, a.ChannelDefinitionSequence[i].ChannelLabel,
                      times)


if __name__ == '__main__':
    main(sys.argv[1])
