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

months = {'JAN': '01',
          'FEB': '02',
          'MAR': '03',
          'APR': '04',
          'MAY': '05',
          'JUN': '06',
          'JUL': '07',
          'AUG': '08',
          'SEP': '09',
          'OCT': '10',
          'NOV': '11',
          'DEC': '12'}


def edf2dicom(edfname, dicomname):
    ds = dataset.Dataset()
    ds.is_little_endian = True  # VERIFY
    ds.is_implicit_VR = False  # VERIFY
    ds.Modality = 'EEG'
    ds.Manufacturer = 'Natus'
    infile = open(edfname, 'rb')
    edf = infile.read()
    infile.close()
    pinfo = encode(edf[8:88]).split(' ')
    ds.PatientSex = pinfo[1]
    try:
        diso = (pinfo[2][7:11] + '-' + months[pinfo[2][3:6]] + '-' +
                pinfo[2][0:2])
        ds.PatientBirthDate = valuerep.DA.fromisoformat(diso)
    except IndexError:
        pass
    pn = pinfo[3].split('_')  # VERIFY
    try:
        ds.PatientName = pn[0] + '^' + pn[1]
    except IndexError:
        pass
    studydt = encode(edf[168:184])
    if int(studydt[6:8]) < 85:
        sdstr = '20'
    else:
        sdstr = '19'
    sdstr += (studydt[6:8] + '-' + studydt[3:5] + '-' + studydt[:2] + 'T' +
              studydt[8:10] + ':' + studydt[11:13] + ':' + studydt[14:16])
    ds.AcquisitionDateTime = valuerep.DT.fromisoformat(sdstr)
    numrec = int(encode(edf[236:244]).strip())
    recsec = int(encode(edf[244:252]).strip())
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
                    wsi.SamplingFrequency = numsamp[j] // recsec
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