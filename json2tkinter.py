# Nathan Holmes-King
# 2023-12-04

from tkinter import *
import json
import sys

"""
WORK IN PROGRESS.

Command-line arguments:
1. JSON file name.

Keyboard usage:
- Left & right arrow keys to scroll time range.
- Up & down arrow keys to scroll between sensors.
- "I" to zoom in, "O" to zoom out.

PEP-8 compliant.
"""


jinp = {}
tk = 0
c = 0
xoff = 0
yoff = 0
xscale = 10
buttons = []


def scrollRight():
    global jinp
    global tk
    global c
    global xoff
    global yoff
    global xscale
    global buttons
    xoff += xscale
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    buttons[1].config(command=scrollRight)


def scrollLeft():
    global jinp
    global tk
    global c
    global xoff
    global yoff
    global xscale
    global buttons
    if xoff >= xscale:
        xoff -= xscale
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    buttons[0].config(command=scrollLeft)


def scrollDown():
    global jinp
    global tk
    global c
    global xoff
    global yoff
    global xscale
    global buttons
    if yoff < len(jinp['data'][0]['delta_information']) - 1:
        yoff += 1
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    buttons[3].config(command=scrollDown)


def scrollUp():
    global jinp
    global tk
    global c
    global xoff
    global yoff
    global xscale
    global buttons
    if yoff >= 1:
        yoff -= 1
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    buttons[2].config(command=scrollUp)


def zoomOut():
    global jinp
    global tk
    global c
    global xoff
    global yoff
    global xscale
    global buttons
    xscale *= 2
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    buttons[5].config(command=zoomOut)


def zoomIn():
    global jinp
    global tk
    global c
    global xoff
    global yoff
    global xscale
    global buttons
    if xscale >= 2:
        xscale //= 2
    c.delete('all')
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    buttons[4].config(command=zoomIn)


def keyRight(event):
    scrollRight()


def keyLeft(event):
    scrollLeft()


def keyUp(event):
    scrollUp()


def keyDown(event):
    scrollDown()


def keyI(event):
    zoomIn()


def keyO(event):
    zoomOut()


def draw(tk, c, data, xoff, yoff, xscale):
    """
    Draws everything on canvas.
    """
    c.create_line(100, 100, 1500, 100)  # Top line
    c.create_line(100, 100, 100, 900)  # Left line
    for i in range(0, 15):
        c.create_line(100*(i+1), 80, 100*(i+1), 100)
        c.create_text(100*(i+1), 75, text=str(xscale*i+xoff),
                      font=('Helvetica', 32), anchor='s')
    sensors = []
    for a in data[0]['delta_information']:
        sensors.append(a)
    for i in range(len(sensors)-yoff):
        c.create_line(80, 200*(i+1), 100, 200*(i+1))
        c.create_text(80, 200*(i+1), text=sensors[i+yoff],
                      font=('Helvetica', 32), anchor='e')
        for j in range(0, 14*xscale):
            c.create_line(j*100/xscale+100,
                          (200*(i+1) -
                           data[xoff +
                                j]['delta_information'][sensors[i+yoff]] /
                           50), j*100/xscale+100+100/xscale,
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
    global xscale
    global buttons
    infile = open(jsonname, 'r')
    jinp = json.loads(infile.read())
    infile.close()
    tk = Tk()
    tk.title('Natus visualization')
    c = Canvas(height=900, width=1500)
    c.pack()
    bc = Canvas(height=100, width=100)
    bc.pack()
    buttons.append(Button(bc, text='Left', width=5, height=2,
                          command=scrollLeft))
    buttons.append(Button(bc, text='Right', width=5, height=2,
                          command=scrollRight))
    buttons.append(Button(bc, text='Up', width=5, height=2, command=scrollUp))
    buttons.append(Button(bc, text='Down', width=5, height=2,
                          command=scrollDown))
    buttons.append(Button(bc, text='Zoom in', width=5, height=2,
                          command=zoomIn))
    buttons.append(Button(bc, text='Zoom out', width=5, height=2,
                          command=zoomOut))
    for i in range(6):
        buttons[i].grid(row=1, column=i)
    c.bind_all('<KeyPress-Right>', keyRight)
    c.bind_all('<KeyPress-Left>', keyLeft)
    c.bind_all('<KeyPress-Down>', keyDown)
    c.bind_all('<KeyPress-Up>', keyUp)
    c.bind_all('<KeyPress-i>', keyI)
    c.bind_all('<KeyPress-o>', keyO)
    draw(tk, c, jinp['data'], xoff, yoff, xscale)
    inp = ''
    while inp != 'y':
        inp = input('Exit? (y/[n])')


if __name__ == '__main__':
    json2tkinter(sys.argv[1])
