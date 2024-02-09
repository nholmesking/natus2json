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
    global mode
    factor += 1
    drawChart(tk, c, mode, factor, chart)


def scrollUp(event):
    global tk
    global c
    global factor
    global chart
    global mode
    if factor > 0:
        factor -= 1
    drawChart(tk, c, mode, factor, chart)


def scrollRight(event):
    global tk
    global c
    global factor
    global chart
    global mode
    chart += 1
    drawChart(tk, c, mode, factor, chart)


def scrollLeft(event):
    global tk
    global c
    global factor
    global chart
    global mode
    if chart > 0:
        chart -= 1
    drawChart(tk, c, mode, factor, chart)


def keyD(event):
    global tk
    global c
    global factor
    global chart
    global mode
    mode = (mode + 1) % 2
    drawChart(tk, c, mode, factor, chart)


def drawChart(tk, c, mode, factor, chart):
    """
    In this function, "factor" is the position within all_indices.
    """
    global width
    global height
    global all_indices
    global axes
    c.delete('all')
    c.create_text(width/2, 50, anchor='s', font=('Helvetica', 24),
                  text='[D]imensions')
    if mode == 0 and chart in [0, 1, 2]:
        x = V[chart][:, all_indices[factor]]
        if chart == 0:
            xlabels = axes['Feature']
        elif chart == 1:
            xlabels = axes['Channel']
        elif chart == 2:
            if len(x) == 7:
                xlabels = ['d-', 'd+', 'th', 'al', 'be', 'g', 'g+']
            else:
                xlabels = ['d', 'th', 'al', 'be', 'g', 'g+']
    elif mode == 1 and chart in [0, 1, 2]:
        x = V[chart][factor, :]
        xlabels = []
        for a in all_indices:
            xlabels.append('Factor ' + str(a))
    if mode == 0:
        c.create_text(width/4, 50, anchor='s', font=('Helvetica', 24),
                      text='\u2191 Factor ' + str(all_indices[factor]) +
                      ' \u2193')
    elif mode == 1:
        if chart == 0:
            c.create_text(width/4, 50, anchor='s', font=('Helvetica', 24),
                          text='\u2191 ' + axes['Feature'][factor] + ' \u2193')
        elif chart == 1:
            c.create_text(width/4, 50, anchor='s', font=('Helvetica', 24),
                          text='\u2191 ' + axes['Channel'][factor] + ' \u2193')
        elif chart == 2:
            if V[2].shape[0] == 7:
                topl = ['d-', 'd+', 'th', 'al', 'be', 'g', 'g+']
            else:
                topl = ['d', 'th', 'al', 'be', 'g', 'g+']
            c.create_text(width/4, 50, anchor='s', font=('Helvetica', 24),
                          text='\u2191 ' + topl[factor] + ' \u2193')
    if chart == 0:
        lab = 'Features'
    elif chart == 1:
        lab = 'Channels'
    elif chart == 2:
        lab = 'Frequency'
    c.create_text(3*width/4, 50, anchor='s', font=('Helvetica', 24),
                  text='\u2190 ' + lab + ' \u2192')
    c.create_line(width/2, 100, width/2, height)  # Center vertical line
    c.create_line(0, 100, width, 100)  # Top horizontal line
    xscale = (width * 0.4) / max(max(x), abs(min(x)))
    # Bars
    for i in range(len(x)):
        c.create_rectangle(width/2, i * 40 + 120, width/2 + x[i] * xscale,
                            i * 40 + 140, fill='#000')
        if x[i] < 0:
            c.create_text(width/2 + 5, i * 40 + 130,
                          text=xlabels[i], anchor='w')
        else:
            c.create_text(width/2 - 5, i * 40 + 130,
                          text=xlabels[i], anchor='e')
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
    height = int(sys.argv[3])
    c = Canvas(width=width, height=height)
    c.pack()
    c.bind_all('<KeyPress-Up>', scrollUp)
    c.bind_all('<KeyPress-Down>', scrollDown)
    c.bind_all('<KeyPress-Left>', scrollLeft)
    c.bind_all('<KeyPress-Right>', scrollRight)
    c.bind_all('<KeyPress-d>', keyD)
    c.bind_all('<KeyPress-D>', keyD)
    k = rank_indices[rank-1]
    factor = 0
    chart = 0
    mode = 0
    for i in range(len(V)):
        for j in range(len(V[i])):
            V[i][j, k] = np.mean(V[i][j, 0:])
    all_indices = np.zeros(rank, dtype=int)
    all_indices[0] = k
    for i in range(1, rank):
        all_indices[i] = rank_indices[i-1]
    drawChart(tk, c, mode, factor, chart)
    input()
