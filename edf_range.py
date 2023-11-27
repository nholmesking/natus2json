# Nathan Holmes-King
# 2023-11-27

import sys
from natus2json import encode
from json2edf import rightpad

"""
WORK IN PROGRESS.

Command-line arguments:
1. Input file name.
2. Output file name.
3. Start of range (inclusive).
4. End of range (exclusive).

PEP-8 compliant.
"""


def edf_range(inname, outname, start, end):
    try:
        start = int(start)
    except ValueError:
        print('ERROR: "' + start + '" is not an integer.')
        return
    try:
        end = int(end)
    except ValueError:
        print('ERROR: "' + end + '" is not an integer.')
        return
    infile = open(inname, 'rb')
    edf = infile.read()
    infile.close()
    numrec = int(encode(edf[236:244]).strip())
    if start < 0 or start > numrec or end < 0 or end > numrec or start > end:
        print('ERROR: start/end values out of range.')
        return
    outfile = open(outname, 'wb')
    outfile.write(edf[:236] + bytes(rightpad(str(end-start), 8),
                                    'ascii') + edf[244:256])
    numsig = int(encode(edf[252:256]).strip())
    headend = 256 * (numsig + 1)
    outfile.write(edf[256:headend])
    lenrec = int((len(edf) - headend) / numrec)
    outfile.write(edf[headend+lenrec*start:headend+lenrec*end])
    outfile.close()
    return


if __name__ == '__main__':
    edf_range(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
