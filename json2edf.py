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
    edffile.write('0' + ' ' * 7)
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
    edffile.write(s[:80])
    edffile.write(' ' * 80)  # PLACEHOLDER, local recording identification
    edffile.write(' ' * 8)  # PLACEHOLDER, startdate
    edffile.write(' ' * 8)  # PLACEHOLDER, starttime
    edffile.write(rightpad(str(256 + jinp['m_num_channels'] * 256), 8))
    edffile.write(' ' * 44)  # PLACEHOLDER, reserved
    edffile.write(' ' * 8)  # PLACEHOLDER, number of data records
    edffile.write(' ' * 8)  # PLACEHOLDER, duration of a data record
    edffile.write(rightpad(str(jinp['m_num_channels']), 8))
    # MORE CODE HERE
    edffile.close()


if __name__ == '__main__':
    json2edf(sys.argv[1], sys.argv[2])
