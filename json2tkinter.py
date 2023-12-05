# Nathan Holmes-King
# 2023-12-04

from tkinter import *
import json
import sys

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name.

How to use:
- Left & right arrow keys to scroll time range.

PEP-8 compliant.
"""


jinp = {}
tk = 0
c = 0
xoff = 0
yoff = 0


def scrollRight(event):
    global jinp
    global tk
    global c
    global xoff
    global yoff
    xoff += 10
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff)


def scrollLeft(event):
    global jinp
    global tk
    global c
    global xoff
    global yoff
    if xoff >= 10:
        xoff -= 10
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff)


def scrollDown(event):
    global jinp
    global tk
    global c
    global xoff
    global yoff
    if yoff < len(jinp['data'][0]['delta_information']) - 1:
        yoff += 1
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff)


def scrollUp(event):
    global jinp
    global tk
    global c
    global xoff
    global yoff
    if yoff >= 1:
        yoff -= 1
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff)


def draw(tk, c, data, xoff, yoff):
    """
    Draws everything on canvas.
    """
    c.create_line(100, 100, 1500, 100)  # Top line
    c.create_line(100, 100, 100, 900)  # Left line
    for i in range(0, 15):
        c.create_line(100*(i+1), 80, 100*(i+1), 100)
        c.create_text(100*(i+1), 75, text=str(10*(i+int(xoff/10))),
                      font=('Helvetica', 32), anchor='s')
    sensors = []
    for a in data[0]['delta_information']:
        sensors.append(a)
    for i in range(len(sensors)-yoff):
        c.create_line(80, 200*(i+1), 100, 200*(i+1))
        c.create_text(80, 200*(i+1), text=sensors[i+yoff],
                      font=('Helvetica', 32), anchor='e')
        for j in range(0, 140):
            c.create_line(j*10+100,
                          (200*(i+1) -
                           data[xoff +
                                j]['delta_information'][sensors[i+yoff]] /
                           50), j*10+110,
                          (200*(i+1) -
                           data[xoff + j +
                                1]['delta_information'][sensors[i+yoff]] /
                           50), width=2)
    tk.update()


def json2tkinter(jsonname):
    """
    Main function. Reads data, sets up Tk, and calls helpers.
    """
    global jinp
    global tk
    global c
    global xoff
    global yoff
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    tk = Tk()
    tk.title('Natus visualization')
    c = Canvas(height=900, width=1500)
    c.pack()
    c.bind_all('<KeyPress-Right>', scrollRight)
    c.bind_all('<KeyPress-Left>', scrollLeft)
    c.bind_all('<KeyPress-Down>', scrollDown)
    c.bind_all('<KeyPress-Up>', scrollUp)
    draw(tk, c, jinp['data'], 0, 0)
    inp = ''
    while inp != 'y':
        inp = input('Exit? (y/[n])')


if __name__ == '__main__':
    json2tkinter(sys.argv[1])
