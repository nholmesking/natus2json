# Nathan Holmes-King
# 2023-12-04

from tkinter import *
import json
import sys

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name.

PEP-8 compliant.
"""


def json2tkinter(jsonname):
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    tk = Tk()
    tk.title('Natus visualization')
    c = Canvas(height=900, width=1500)
    c.pack()
    c.create_line(100, 100, 1500, 100)  # Top line
    c.create_line(100, 100, 100, 900)  # Left line
    for i in range(0, 15):
        c.create_line(100*(i+1), 80, 100*(i+1), 100)
        c.create_text(100*(i+1), 75, text=str(10*i), font=('Helvetica', 32),
                      anchor='s')
    sensors = []
    for a in jinp['data'][0]['delta_information']:
        sensors.append(a)
    for i in range(len(sensors)):
        c.create_line(80, 200*(i+1), 100, 200*(i+1))
        c.create_text(80, 200*(i+1), text=sensors[i],
                      font=('Helvetica', 32), anchor='e')
        for j in range(0, 140):
            c.create_line(j*10+100,
                          (200*(i+1) -
                           jinp['data'][j]['delta_information'][sensors[i]] /
                           50), j*10+110,
                          (200*(i+1) -
                           jinp['data'][j+1]['delta_information'][sensors[i]] /
                           50), width=2)
    tk.update()
    inp = ''
    while inp != 'y':
        inp = input('Exit? (y/[n])')


if __name__ == '__main__':
    json2tkinter(sys.argv[1])
