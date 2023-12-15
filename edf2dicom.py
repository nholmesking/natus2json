# Nathan Holmes-King
# 2023-12-15

import sys
from natus2json import encode
from pydicom import dataset
from pydicom import valuerep
from pydicom import filewriter
from pydicom import sequence
import numpy as np
import time

"""
WORK IN PROGRESS.

Command-line arguments:
1. Input file name.
2. Output file name.

PEP-8 compliant.
"""


def edf2dicom(edfname, dicomname):
    infile = open(edfname, 'rb')
    edf = infile.read()
    infile.close()
    numrec = int(encode(edf[236:244]).strip())
    ds = dataset.Dataset()
    ds.is_little_endian = True  # VERIFY
    ds.is_implicit_VR = False  # VERIFY
    ds.Modality = 'EEG'
    numsig = int(encode(edf[252:256]).strip())
    headend = 256 * (numsig + 1)
    lenrec = int((len(edf) - headend) / numrec)  # Length of a record in bytes
    numsamp = []
    for i in range(numsig):
        numsamp.append(int(encode(edf[256+216*numsig +
                                      8*i:256+216*numsig+8*(i+1)]).strip()))
    lensamp = lenrec // np.sum(numsamp)  # Length of a sample within a record
    labels = []
    for i in range(numsig):
        labels.append(encode(edf[256+16*i:256+16*(i+1)]))
    units = []
    for i in range(numsig):
        units.append(encode(edf[256+96*numsig+8*i:256+96*numsig+8*(i+1)]))
    dws = sequence.Sequence()
    for i in range(numrec):
        for j in range(len(numsamp)):
            if labels[j][:3] != 'EEG':  # VERIFY
                continue
            for k in range(numsamp[j]):
                try:
                    dws[i*numsamp[j]+k].NumberOfWaveformChannels += 1
                except IndexError:
                    wsi = dataset.Dataset()
                    wsi.NumberOfWaveformChannels = 1
                    wsi.ChannelDefinitionSequence = sequence.Sequence()
                    dws.append(wsi)
                wch = dataset.Dataset()
                wch.ChannelLabel = labels[j]
                rc = edf[headend+lenrec*i+np.sum(numsamp)*j+lensamp*k:
                         headend+lenrec*i+np.sum(numsamp)*j+lensamp*(k+1)]
                wch.ChannelSensitivity = int.from_bytes(rc, 'little')  # VERIFY
                wch.ChannelSensitivityUnitsSequence = sequence.Sequence()
                wun = dataset.Dataset()
                wun.CodeValue = units[j]
                wch.ChannelSensitivityUnitsSequence.append(wun)
                dws[i*numsamp[j]+k].ChannelDefinitionSequence.append(wch)
    ds.WaveformSequence = dws
    filewriter.dcmwrite(dicomname, ds)


if __name__ == '__main__':
    t = time.time()
    edf2dicom(sys.argv[1], sys.argv[2])
    print('DONE', round(time.time() - t, 2), 's')
