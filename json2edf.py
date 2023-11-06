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
    while len(s) < 80:
        s += ' '
    edffile.write(s[:80])
    edffile.write(' ' * 80)  # PLACEHOLDER, local recording identification
    # MORE CODE HERE
    edffile.close()


if __name__ == '__main__':
    json2edf(sys.argv[1], sys.argv[2])
