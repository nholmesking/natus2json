# Nathan Holmes-King
# 2023-12-16

import sys
from pydicom import dcmread
import time
from json2edf import rightpad

"""
WORK IN PROGRESS.

Command-line arguments:
1. Input file name.
2. Output file name.

PEP-8 compliant.
"""


months = {1: 'JAN',
          2: 'FEB',
          3: 'MAR',
          4: 'APR',
          5: 'MAY',
          6: 'JUN',
          7: 'JUL',
          8: 'AUG',
          9: 'SEP',
          10: 'OCT',
          11: 'NOV',
          12: 'DEC'}


def dicom2edf(dicomname, edfname):
    """
    Main function.
    """
    # Read DICOM file
    ds = dcmread(dicomname, force=True)
    # Open EDF file
    outfile = open(edfname, 'wb')
    # Write header
    outfile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    lpid = (ds.PatientID + ' ' + ds.PatientSex + ' ' +
            ds.PatientBirthDate[6:8] + '-' +
            months[int(ds.PatientBirthDate[4:6])] + '-' +
            ds.PatientBirthDate[:4] + ' ')
    try:
        for a in ds.PatientName:
            if a == '^':
                lpid += '_'
            else:
                lpid += a
    except AttributeError:  # Patient name not listed
        pass
    outfile.write(rightpad(lpid, 80))
    outfile.write(bytes(' ' * 80, 'ascii'))  # PLACEHOLDER
    adt = ds.AcquisitionDateTime
    outfile.write(bytes(adt[6:8] + '.' + adt[4:6] + '.' + adt[2:4] +
                        adt[8:10] + '.' + adt[10:12] + '.' +
                        adt[12:14], 'ascii'))
    outfile.write(rightpad(str(256 * ds.WaveformSequence[0].
                               NumberOfWaveformChannels + 256), 8))
    outfile.write(bytes(' ' * 44, 'ascii'))
    outfile.write(rightpad(str(len(ds.WaveformSequence)), 8))
    outfile.write(rightpad('1', 8))  # VERIFY
    outfile.write(rightpad(str(ds.WaveformSequence[0].
                               NumberOfWaveformChannels), 4))
    # Label
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(rightpad(a.ChannelLabel, 16))
    # Transducer type
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(bytes(' ' * 80, 'ascii'))  # PLACEHOLDER
    # Units
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(rightpad(a.ChannelSensitivityUnitsSequence[0].CodeValue,
                               8))
    # Physical min
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    # Physical max
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    # Digital min
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(rightpad(str(-2 ** (ds.WaveformSequence[0].
                                          WaveformBitsAllocated //
                                          ds.WaveformSequence[0].
                                          NumberOfWaveformChannels - 1)), 8))
    # Digital max
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(rightpad(str(2 ** (ds.WaveformSequence[0].
                                         WaveformBitsAllocated //
                                         ds.WaveformSequence[0].
                                         NumberOfWaveformChannels - 1) - 1),
                               8))
    # Prefiltering
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(bytes(' ' * 80, 'ascii'))  # PLACEHOLDER
    # Samples per record
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(rightpad(str(ds.WaveformSequence[0].
                                   NumberOfWaveformSamples), 8))
    # Reserved
    for a in ds.WaveformSequence[0].ChannelDefinitionSequence:
        outfile.write(bytes(' ' * 32, 'ascii'))  # PLACEHOLDER
    # Data records
    k = (ds.WaveformSequence[0].WaveformBitsAllocated //
         ds.WaveformSequence[0].NumberOfWaveformChannels) // 8
    for a in ds.WaveformSequence:
        for i in range(a.NumberOfWaveformChannels):
            for j in range(a.NumberOfWaveformSamples):
                outfile.write(a.WaveformData[j*a.WaveformBitsAllocated//8+i*k:
                                             j*a.WaveformBitsAllocated//8+i*k +
                                             k])
    outfile.close()


if __name__ == '__main__':
    t = time.time()
    dicom2edf(sys.argv[1], sys.argv[2])
    print('DONE', round(time.time() - t, 2), 's')
