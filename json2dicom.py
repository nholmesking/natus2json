# Nathan Holmes-King
# 2023-12-06

import sys
import json
import pydicom

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
    ds = pydicom.dataset.Dataset()
    # EXPAND
    pydicom.filewriter.dcmwrite(dicomname, ds)


if __name__ == '__main__':
    json2dicom(sys.argv[1], sys.argv[2])
