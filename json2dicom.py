# Nathan Holmes-King
# 2023-12-06

import sys
import json
from pydicom import dataset
from pydicom import valuerep
from pydicom import filewriter
from pydicom import sequence
import time

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name. JSON must be from natus2json.py.
2. DICOM file name

PEP-8 compliant.
"""


def json2dicom(jsonname, dicomname):
    fex = jsonname[len(jsonname)-8:len(jsonname)-5]
    if fex == 'old':
        fex = jsonname[len(jsonname)-12:len(jsonname)-9]
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    ds = dataset.Dataset()
    ds.is_little_endian = True  # VERIFY
    ds.is_implicit_VR = False  # VERIFY
    lsc = sequence.Sequence([dataset.Dataset()])
    lsc[0].CodeValue = 'en'
    lsc[0].CodingSchemeDesignator = 'RFC5646'
    ds.LanguageCodeSequence = lsc
    ds.InstanceCreationDate = (valuerep.DA.
                               fromisoformat(jinp['m_creation_time'][:10]))
    ds.InstanceCreationTime = (valuerep.TM.
                               fromisoformat(jinp['m_creation_time'][11:19] +
                                             '+00:00'))
    ins = ''
    i = 0
    while i < len(jinp['m_file_guid']):
        if jinp['m_file_guid'][i] == '-':
            i += 1
            continue
        if len(ins) > 0:
            ins += '.'
        ins += str(int(jinp['m_file_guid'][i:i+2], 16))
        i += 2
    ds.SOPInstanceUID = ins  # VERIFY
    ds.PatientName = (jinp['m_pat_last_name'] + '^' +
                      jinp['m_pat_first_name'] + '^' +
                      jinp['m_pat_middle_name'])
    ds.PatientID = jinp['m_pat_id']
    ds.Modality = 'EEG'
    ds.Manufacturer = 'Natus'
    if fex == 'eeg':
        try:
            ds.PatientSex = jinp['Info']['Personal']['Gender'][0]
        except IndexError:
            ds.PatientSex = 'O'
        ds.PatientSize = jinp['Info']['Personal']['Height'] / 100
        ds.PatientWeight = jinp['Info']['Personal']['Weight']
    elif fex == 'erd':
        ds.WaveformSequence = sequence.Sequence()
        for a in jinp['data']:
            wsi = dataset.Dataset()
            wsi.SamplingFrequency = jinp['m_sample_freq']
            wsi.NumberOfWaveformChannels = len(a['delta_information'])
            wsi.ChannelDefinitionSequence = sequence.Sequence()
            for b in a['delta_information']:
                wch = dataset.Dataset()
                wch.ChannelLabel = b
                wch.ChannelSensitivity = a['delta_information'][b]
                wch.ChannelSensitivityUnitsSequence = sequence.Sequence()
                wun = dataset.Dataset()
                wun.CodingSchemeDesignator = 'UCUM'
                wun.CodeValue = 'uV'
                wch.ChannelSensitivityUnitsSequence.append(wun)
                wsi.ChannelDefinitionSequence.append(wch)
            ds.WaveformSequence.append(wsi)
            i += 1
    filewriter.dcmwrite(dicomname, ds)


if __name__ == '__main__':
    t = time.time()
    json2dicom(sys.argv[1], sys.argv[2])
    print('DONE', round(time.time() - t, 2), 's')
