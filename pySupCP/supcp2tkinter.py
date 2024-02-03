# Nathan Holmes-King
# 2024-01-31

import pickle
from tkinter import *
import sys
import numpy as np

"""
WORK IN PROGRESS.

Command-line arguments:
1. input file name
2. canvas width
3. canvas height

PEP-8 compliant.
"""


def scrollDown(event):
    global tk
    global c
    global factor
    global chart
    factor += 1
    drawChart(tk, c, factor, chart)


def scrollUp(event):
    global tk
    global c
    global factor
    global chart
    if factor > 0:
        factor -= 1
    drawChart(tk, c, factor, chart)


def drawChart(tk, c, factor, chart):
    """
    In this function, "factor" is the position within all_indices.
    """
    global width
    global height
    global all_indices
    global axes
    c.delete('all')
    if chart == 0:
        c.create_line(width/2, 100, width/2, height)  # Center vertical line
        c.create_line(0, 100, width, 100)  # Top horizontal line
        x = V[0][:, all_indices[factor]]
        xscale = (width * 0.4) / max(max(x), abs(min(x)))
        # Bars
        for i in range(len(x)):
            c.create_rectangle(width/2, i * 40 + 120, width/2 + x[i] * xscale,
                               i * 40 + 140, fill='#00f')
            if x[i] < 0:
                c.create_text(width/2 + 5, i * 40 + 130,
                              text=axes['Feature'][i], anchor='w')
            else:
                c.create_text(width/2 - 5, i * 40 + 130,
                              text=axes['Feature'][i], anchor='e')
        # X scale
        c.create_line(width/2, 100, width/2, 90)
        c.create_text(width/2, 85, text='0', anchor='s')
        inc = 10 ** np.ceil(np.log10(50 / xscale))
        n = 1
        while n * inc * xscale < width / 2:
            txt = n * inc
            if inc < 1:
                txt = round(txt, int(-np.ceil(np.log10(50 / xscale))))
            c.create_line(width/2 + n * inc * xscale, 100,
                          width/2 + n * inc * xscale, 90)
            c.create_text(width/2 + n * inc * xscale, 85, text=str(txt),
                          anchor='s')
            c.create_line(width/2 - n * inc * xscale, 100,
                          width/2 - n * inc * xscale, 90)
            c.create_text(width/2 - n * inc * xscale, 85,
                          text='-' + str(txt), anchor='s')
            n += 1
    return


if __name__ == '__main__':
    infile = open(sys.argv[1], 'rb')
    V = pickle.load(infile)
    rank_indices = pickle.load(infile)
    rank = pickle.load(infile)
    U = pickle.load(infile)
    age_list = pickle.load(infile)
    Y_para = pickle.load(infile)
    total_R = pickle.load(infile)
    total_pval = pickle.load(infile)
    axes = pickle.load(infile)
    unique_labels = pickle.load(infile)
    label_index = pickle.load(infile)
    y_score = pickle.load(infile)
    data_text = pickle.load(infile)
    sup_title = pickle.load(infile)
    SLEEPSTAGE = pickle.load(infile)
    covariate_list = pickle.load(infile)
    infile.close()
    tk = Tk()
    width = int(sys.argv[2])
    height = int(sys.argv[2])
    c = Canvas(width=width, height=height)
    c.pack()
    c.bind_all('<KeyPress-Up>', scrollUp)
    c.bind_all('<KeyPress-Down>', scrollDown)
    k = rank_indices[rank-1]
    factor = 0
    chart = 0
    for i in range(len(V)):
        for j in range(len(V[i])):
            V[i][j, k] = np.mean(V[i][j, 0:])
    all_indices = np.zeros(rank, dtype=int)
    all_indices[0] = k
    for i in range(1, rank):
        all_indices[i] = rank_indices[i-1]
    drawChart(tk, c, factor, chart)
    input()
