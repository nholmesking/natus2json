# Nathan Holmes-King
# 2023-11-06

import sys
import json

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name. JSON must be from natus2json.py.
2. EDF file name

PEP-8 compliant.
"""


def rightpad(ins, n):
    out = ins
    while len(out) < n:
        out += ' '
    return out


def json2edf(jsonname, edfname):
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    edffile = open(edfname, 'w')
    edffile.write('0' + ' ' * 7)  # data format version
    s = ''
    s += jinp['m_pat_id'] + ' '
    s += '?'  # gender
    s += ' '
    s += '??-???-????'  # birthdate
    s += ' '
    s += (jinp['m_pat_last_name'] + '_' + jinp['m_pat_first_name'] + '_' +
          jinp['m_pat_middle_name'])
    s = rightpad(s, 80)
    edffile.write(s[:80])  # local patient ID
    edffile.write(' ' * 80)  # PLACEHOLDER, local recording identification
    edffile.write(' ' * 8)  # PLACEHOLDER, startdate
    edffile.write(' ' * 8)  # PLACEHOLDER, starttime
    edffile.write(rightpad(str(256 + jinp['m_num_channels'] * 256), 8))
    edffile.write(' ' * 44)  # PLACEHOLDER, reserved
    edffile.write(rightpad(str(len(jinp['data'])), 8))
    edffile.write(' ' * 8)  # PLACEHOLDER, duration of a data record
    edffile.write(rightpad(str(jinp['m_num_channels']), 4))
    channels = []
    li = jinp['data'][0]['delta_information']
    for b in li:  # label
        edffile.write(rightpad(b, 16))
        channels.append(b)
    for b in li:  # transducer type
        edffile.write(' ' * 80)  # PLACEHOLDER
    for b in li:  # physical dimension
        edffile.write('uV      ')
    for b in li:  # physical minimum
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:  # physical maximum
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:  # digital minimum
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:  # digital maximum
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:  # prefiltering
        edffile.write(' ' * 80)  # PLACEHOLDER
    for b in li:  # number of samples in each record
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:  # reserved
        edffile.write(' ' * 32)  # PLACEHOLDER
    for a in jinp['data']:  # DATA RECORDS
        for b in channels:
            edffile.write(rightpad(str(a['delta_information'][b]), 16))
    edffile.close()


if __name__ == '__main__':
    json2edf(sys.argv[1], sys.argv[2])
