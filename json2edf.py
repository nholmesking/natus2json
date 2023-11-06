# Nathan Holmes-King
# 2023-11-06

import sys
import json

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name
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
    s += jinp['Info']['Admin']['ID'] + ' '
    if jinp['Info']['Personal']['Gender'] == 'Male':
        s += 'M'
    elif jinp['Info']['Personal']['Gender'] == 'Female':
        s += 'F'
    else:
        s += 'X'
    s += ' '
    # MORE CODE HERE
    s = rightpad(s, 80)
    edffile.write(s[:80])  # local patient ID
    edffile.write(' ' * 80)  # PLACEHOLDER, local recording identification
    edffile.write(' ' * 8)  # PLACEHOLDER, startdate
    edffile.write(' ' * 8)  # PLACEHOLDER, starttime
    edffile.write(rightpad(str(256 + jinp['m_num_channels'] * 256), 8))
    edffile.write(' ' * 44)  # PLACEHOLDER, reserved
    edffile.write(rightpad(str(jinp['packets']), 8))
    edffile.write(' ' * 8)  # PLACEHOLDER, duration of a data record
    edffile.write(rightpad(str(jinp['m_num_channels']), 4))
    channels = []
    li = jinp['packets'][0]['delta_information']
    for b in li:  # label
        edffile.write(rightpad(b, 16))
        channels.append(b)
    for b in li:
        edffile.write(' ' * 80)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 80)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 8)  # PLACEHOLDER
    for b in li:
        edffile.write(' ' * 32)  # PLACEHOLDER
    for a in jinp['packets']:  # DATA RECORDS
        for b in channels:
            edffile.write(rightpad(str(a['delta_information'][b]), 16))
    edffile.close()


if __name__ == '__main__':
    json2edf(sys.argv[1], sys.argv[2])
