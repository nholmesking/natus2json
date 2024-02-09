# Nathan Holmes-King
# 2024-02-08

import pickle
import sys
import numpy as np

"""
WORK IN PROGRESS.

Command-line arguments:
1. input file name
2. SVG width
3. SVG height

PEP-8 compliant.
"""


def drawChart(svg, factor, chart):
    """
    In this function, "factor" is the position within all_indices.
    """
    global width
    global height
    global all_indices
    global axes
    if chart == 0:
        lab = 'Features'
    elif chart == 1:
        lab = 'Channels'
    elif chart == 2:
        lab = 'Frequency'
    svg.write('<!DOCTYPE svg>\n<svg width="' + str(width) + '" height="' +
              str(height) + '" xmlns="http://www.w3.org/2000/svg">')
    svg.write('\n\t<text x="' + str(width/3) +
              '" y="50" font-size="24" text-anchor="middle">Factor ' +
              str(all_indices[factor]) + '</text>')
    svg.write('\n\t<text x="' + str(2*width/3) +
              '" y="50" font-size="24" text-anchor="middle">' + lab +
              '</text>')
    svg.write('\n\t<line x1="' + str(width/2) + '" y1="100" x2="' +
              str(width/2) + '" y2="' +
              str(height) + '" stroke="#000"/>')  # Center vertical line
    svg.write('\n\t<line x1="0" y1="100" x2="' + str(width) +
              '" y2="100" stroke="#000"/>')  # Top horizontal line
    if chart in [0, 1, 2]:
        x = V[chart][:, all_indices[factor]]
    xscale = (width * 0.4) / max(max(x), abs(min(x)))
    # Bars
    if chart == 0:
        for i in range(len(x)):
            if x[i] < 0:
                svg.write('\n\t<rect x="' + str(width/2 + x[i] * xscale) +
                          '" y="' + str(i * 40 + 120) + '" width="' +
                          str(-x[i] * xscale) + '" height="20" fill="#000"/>')
                svg.write('\n\t<text x="' + str(width/2+5) + '" y="' +
                          str(i * 40 + 135) + '" text-anchor="start">' +
                          axes['Feature'][i] + '</text>')
            else:
                svg.write('\n\t<rect x="' + str(width/2) + '" y="' +
                          str(i * 40 + 120) + '" width="' +
                          str(x[i] * xscale) + '" height="20" fill="#000"/>')
                svg.write('\n\t<text x="' + str(width/2-5) + '" y="' +
                          str(i * 40 + 135) + '" text-anchor="end">' +
                          axes['Feature'][i] + '</text>')
    elif chart == 1:
        for i in range(len(x)):
            if x[i] < 0:
                svg.write('\n\t<rect x="' + str(width/2 + x[i] * xscale) +
                          '" y="' + str(i * 40 + 120) + '" width="' +
                          str(-x[i] * xscale) + '" height="20" fill="#000"/>')
                svg.write('\n\t<text x="' + str(width/2+5) + '" y="' +
                          str(i * 40 + 135) + '" text-anchor="start">' +
                          axes['Channel'][i] + '</text>')
            else:
                svg.write('\n\t<rect x="' + str(width/2) + '" y="' +
                          str(i * 40 + 120) + '" width="' +
                          str(x[i] * xscale) + '" height="20" fill="#000"/>')
                svg.write('\n\t<text x="' + str(width/2-5) + '" y="' +
                          str(i * 40 + 135) + '" text-anchor="end">' +
                          axes['Channel'][i] + '</text>')
    elif chart == 2:
        if len(x) == 7:
            xlabels = ['d-', 'd+', 'th', 'al', 'be', 'g', 'g+']
        else:
            xlabels = ['d', 'th', 'al', 'be', 'g', 'g+']
        for i in range(len(x)):
            if x[i] < 0:
                svg.write('\n\t<rect x="' + str(width/2 + x[i] * xscale) +
                          '" y="' + str(i * 40 + 120) + '" width="' +
                          str(-x[i] * xscale) + '" height="20" fill="#000"/>')
                svg.write('\n\t<text x="' + str(width/2+5) + '" y="' +
                          str(i * 40 + 135) + '" text-anchor="start">' +
                          xlabels[i] + '</text>')
            else:
                svg.write('\n\t<rect x="' + str(width/2) + '" y="' +
                          str(i * 40 + 120) + '" width="' +
                          str(x[i] * xscale) + '" height="20" fill="#000"/>')
                svg.write('\n\t<text x="' + str(width/2-5) + '" y="' +
                          str(i * 40 + 135) + '" text-anchor="end">' +
                          xlabels[i] + '</text>')
    # X scale
    svg.write('\n\t<line x1="' + str(width/2) + '" y1="100" x2="' +
              str(width/2) + '" y2="90" stroke="#000"/>')
    svg.write('\n\t<text x="' + str(width/2) +
              '" y1="85" text-anchor="middle">0</text>')
    inc = 10 ** np.ceil(np.log10(50 / xscale))
    n = 1
    while n * inc * xscale < width / 2:
        txt = n * inc
        if inc < 1:
            txt = round(txt, int(-np.ceil(np.log10(50 / xscale))))
        svg.write('\n\t<line x1="' + str(width/2 + n * inc * xscale) +
                  '" y1="100" x2="' + str(width/2 + n * inc * xscale) +
                  '" y2="90" stroke="#000"/>')
        svg.write('\n\t<text x="' + str(width/2 + n * inc * xscale) +
                  '" y="85" text-anchor="middle">' + str(txt) + '</text>')
        svg.write('\n\t<line x1="' + str(width/2 - n * inc * xscale) +
                  '" y1="100" x2="' + str(width/2 - n * inc * xscale) +
                  '" y2="90" stroke="#000"/>')
        svg.write('\n\t<text x="' + str(width/2 - n * inc * xscale) +
                  '" y="85" text-anchor="middle">-' + str(txt) + '</text>')
        n += 1
    svg.write('\n</svg>')
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
    width = int(sys.argv[2])
    height = int(sys.argv[3])
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
    cl = ['Features', 'Channels', 'Frequency']
    for factor in range(len(all_indices)):
        for chart in range(len(cl)):
            svg = open('chart_' + cl[chart] + '_F' + str(all_indices[factor]) +
                       '.svg', 'w')
            drawChart(svg, factor, chart)
            svg.close()
