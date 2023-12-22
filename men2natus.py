# Nathan Holmes-King
# 2023-12-20

import sys
import math

"""
WORK IN PROGRESS.

Command-line arguments:
1. input file
2. output file

PEP-8 compliant.
"""


def sepBits(byt):
    rl = []
    for i in range(len(byt)):
        bi = byt[i]
        for k in range(8):
            if bi % 2 == 1:
                rl.append(1)
            else:
                rl.append(0)
            bi = int(bi / 2)
    return rl


def men2natus(inname, outname):
    infile = open(inname, 'rb')
    men = infile.read()
    infile.close()
    natus = open(outname, 'wb')
    natus.write(men[:16])  # File GUID
    fv = men[16]
    mv = men[17]
    natus.write(bytes([9, 0, 1, 0]))  # Schema
    natus.write(men[18:22])  # Creation time
    natus.write(men[26:34])
    j = 34
    for i in range(4):  # Patient info
        ln = men[j]
        j += 1
        s = men[j:j+ln]
        while len(s) < 80:
            s += b'\x00'
        natus.write(s)
        j += ln
    natus.write(men[j:j+10])  # Sample freq & num channels
    nc = int.from_bytes(men[j+8:j+10], 'little')
    natus.write(bytes([0, 0]))
    natus.write(bytes([8, 0, 0, 0]))  # Delta bits
    j += 10
    s = b''
    for i in range(nc):
        s += men[j:j+2]
        s += b'\x00\x00'
        j += 2
    while len(s) < 4096:
        s += b'\x00' * 4
    natus.write(s)
    nh = men[j]  # Number of headboxes
    j += 1
    s = b''
    for i in range(nh):
        s += men[j:j+4]
        j += 4
    while len(s) < 16:
        s += b'\x00' * 4
    natus.write(s)
    s = b''
    for i in range(nh):
        s += men[j:j+4]
        j += 4
    while len(s) < 16:
        s += b'\x00' * 4
    natus.write(s)
    s = b''
    for i in range(nh):
        s += men[j:j+10]
        j += 10
    while len(s) < 40:
        s += b'\x00' * 10
    natus.write(s)
    natus.write(men[j:j+21])
    j += 21
    natus.write(bytes([0, 0, 0]))  # Discardbits
    sb = sepBits(men[j:j+math.ceil(nc/8)])[:nc]
    nactc = 0
    s = b''
    for a in sb:
        s += bytes([a, 0])
        if a == 0:
            nactc += 1
    while len(s) < 2048:
        s += b'\x00' * 2
    natus.write(s)
    j += math.ceil(nc/8)
    s = men[j:j+nc*2]
    while len(s) < 2048:
        s += b'\xff\x7f'
    j += nc * 2
    natus.write(s)
    while j < len(men):
        natus.write(men[j:j+1])  # Event byte
        j += 1
        nb = men[j:j+math.ceil(nactc/4)]
        numbytes = []
        for a in nb:
            bc = a
            for i in range(4):
                numbytes.append(bc % 4)
                bc //= 4
        j += math.ceil(nactc/4)
        deltamask = []
        k = 0
        for i in range(nc):
            if sb[i] == 1:
                deltamask.append(1)
            else:
                if numbytes[k] == 0:
                    deltamask.append(0)
                else:
                    deltamask.append(1)
                k += 1
        while len(deltamask) % 8 != 0:
            deltamask.append(1)
        dm = []
        while len(dm) < nc/8:
            dm.append(0)
        for i in range(len(deltamask)):
            dm[int(i/8)] += deltamask[i] * 2 ** (i % 8)
        natus.write(bytes(dm))
        acv = []
        for i in range(nactc):
            if numbytes[i] < 2:
                natus.write(men[j:j+numbytes[i]+1])
            else:
                acv.append(men[j:j+numbytes[i]+1])
                natus.write(bytes([255, 255]))
            j += numbytes[i] + 1
        for a in acv:
            natus.write(a)
            if len(a) == 3:
                natus.write(b'\x00')


if __name__ == '__main__':
    men2natus(sys.argv[1], sys.argv[2])
