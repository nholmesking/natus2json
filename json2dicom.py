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
    ds.CreationDate = valuerep.DA.fromisoformat(jinp['m_creation_time'][:10])
    ds.CreationTime = (valuerep.TM.
                       fromisoformat(jinp['m_creation_time'][11:19] +
                                     '+00:00'))
    # EXPAND
    filewriter.dcmwrite(dicomname, ds)


if __name__ == '__main__':
    json2dicom(sys.argv[1], sys.argv[2])
