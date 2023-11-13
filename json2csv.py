# Nathan Holmes-King
# 2023-11-13

import sys
import json
import csv

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name. JSON must be from natus2json.py.
2. CSV file name

PEP-8 compliant.
"""


def json2csv(jsonname, csvname):
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    csvfile = open(csvname, 'w')
    csvwriter = csv.writer(csvfile)
    firstrow = ['index', 'event_byte']
    for b in jinp['data'][0]['delta_information']:
        firstrow.append(b)
    csvwriter.writerow(firstrow)
    k = 0
    while k < len(jinp['data']):
        row = [k, jinp['data'][k]['event_byte']]
        for a in jinp['data'][k]['delta_information']:
            row.append(jinp['data'][k]['delta_information'][a])
        csvwriter.writerow(row)
        k += 1
    csvfile.close()


if __name__ == '__main__':
    json2csv(sys.argv[1], sys.argv[2])
