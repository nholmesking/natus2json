# Nathan Holmes-King
# 2023-11-06

import sys
import json
from natus2json import encode
import time

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name. JSON must be from natus2json.py.
2. EDF file name
3. First record (inclusive, start at 0). Leaving blank gives all records.
4. Last record (inclusive, start at 0)

PEP-8 compliant.
"""


def rightpad(ins, n):
    out = ins
    while len(out) < n:
        out += ' '
    return bytes(out, 'ascii')


def json2edf(jsonname, edfname, first, last):
    if first != '':
        try:
            first = int(first)
        except ValueError:
            print('ERROR: "' + first + '" is not a valid integer.')
            return
    if last != '':
        try:
            last = int(last)
        except ValueError:
            print('ERROR: "' + last + '" is not a valid integer.')
            return
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    if ((type(first) is int and first < -1) or (type(first) is int and
                                                first > len(jinp['data']))):
        print('ERROR: start-of-list index out of range.')
        return
    if ((type(last) is int and last < -1) or (type(last) is int and
                                              last > len(jinp['data']))):
        print('ERROR: end-of-list index out of range.')
        return
    if type(first) is int and type(last) is int:
        jdat = jinp['data'][first:last]
    elif type(first) is int:
        jdat = jinp['data'][first:]
    else:
        jdat = jinp['data']
    edffile = open(edfname, 'wb')
    edffile.write(bytes('0' + ' ' * 7, 'ascii'))  # data format version
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
    edffile.write(bytes(' ' * 80, 'ascii'))  # PLACEHOLDER, local recording id
    edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER, startdate
    edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER, starttime
    edffile.write(rightpad(str(256 + jinp['m_num_channels'] * 256), 8))
    edffile.write(bytes(' ' * 44, 'ascii'))  # PLACEHOLDER, reserved
    edffile.write(rightpad(str(len(jdat)), 8))
    edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER, record duration
    edffile.write(rightpad(str(jinp['m_num_channels']), 4))
    channels = []
    li = jdat[0]['delta_information']
    for b in li:  # label
        edffile.write(rightpad(b, 16))
        channels.append(b)
    for b in li:  # transducer type
        edffile.write(bytes(' ' * 80, 'ascii'))  # PLACEHOLDER
    for b in li:  # physical dimension
        edffile.write(bytes('uV      ', 'ascii'))
    for b in li:  # physical minimum
        edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    for b in li:  # physical maximum
        edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    for b in li:  # digital minimum
        edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    for b in li:  # digital maximum
        edffile.write(bytes(' ' * 8, 'ascii'))  # PLACEHOLDER
    for b in li:  # prefiltering
        edffile.write(bytes(' ' * 80, 'ascii'))  # PLACEHOLDER
    for b in li:  # number of samples in each record
        edffile.write(bytes('1       ', 'ascii'))  # VERIFY
    for b in li:  # reserved
        edffile.write(bytes(' ' * 32, 'ascii'))  # PLACEHOLDER
    for a in jdat:  # DATA RECORDS
        for b in channels:
            edffile.write(bytes(a['delta_information'][b]))
    edffile.close()


if __name__ == '__main__':
    sav = sys.argv
    while len(sav) < 5:
        sav.append('')
    st = time.time()
    json2edf(sav[1], sav[2], sav[3], sav[4])
    et = time.time()
    print('DONE', round(et - st, 2), 's')
