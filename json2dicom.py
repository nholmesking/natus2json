# Nathan Holmes-King
# 2023-12-06

import sys
import json
from pydicom import dataset
from pydicom import valuerep
from pydicom import filewriter

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
    ds.PatientName = (jinp['m_pat_last_name'] + '^' +
                      jinp['m_pat_first_name'] + '^' +
                      jinp['m_pat_middle_name'])
    ds.PatientID = jinp['m_pat_id']
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
    ds.Modality = 'EEG'
    if fex == 'erd':
        ds.SamplingFrequency = jinp['m_sample_freq']
    # EXPAND
    filewriter.dcmwrite(dicomname, ds)


if __name__ == '__main__':
    json2dicom(sys.argv[1], sys.argv[2])
