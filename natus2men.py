# Nathan Holmes-King
# 2023-12-19

import sys
import math
import numpy as np

"""
WORK IN PROGRESS.

Command-line arguments:
1. input file
2. output file
3. MEN version (int or letter)

PEP-8 compliant.
"""


mv = {'A': 1,
      'B': 2}


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


def comBits(inp):
    rl = []
    while len(rl) < len(inp) / 8:
        rl.append(0)
    for i in range(len(inp)):
        rl[int(i/8)] += inp[i] * 2 ** (i % 8)
    return rl


def natus2men(inname, outname, menv):
    try:
        menv = int(menv)
    except ValueError:
        try:
            menv = mv[menv]
        except KeyError:
            print('ERROR: invalid MEN version.')
            return
    infile = open(inname, 'rb')
    natus = infile.read()
    infile.close()
    men = open(outname, 'wb')
    men.write(natus[:16])  # File GUID
    schema = int.from_bytes(natus[16:18], byteorder='little')
    men.write(b'\x00')  # File version
    men.write(menv.to_bytes(1, 'little'))  # MEN type
    men.write(natus[20:24] + b'\x00' * 4)  # Creation time, 64-bit
    men.write(natus[24:32])
    for i in [32, 112, 192, 272]:
        j = i
        while natus[j] != 0:
            j += 1
        men.write((j-i).to_bytes(1, 'little'))
        men.write(natus[i:j])
    men.write(natus[352:360])
    men.write(natus[360:362])  # Number of channels
    nc = int.from_bytes(natus[360:362], byteorder='little')
    if schema == 9:
        for i in range(nc):
            men.write(natus[368+i*4:370+i*4])
        nh = 0
        for i in range(4):
            if (int.from_bytes(natus[4464+i*4:4464+i*4+4],
                               byteorder='little') != 0):
                nh += 1
        men.write(bytes([nh]))
        for i in range(nh):  # Headbox type
            men.write(natus[4464+i*4:4464+i*4+4])
        for i in range(nh):  # Headbox SN
            men.write(natus[4480+i*4:4480+i*4+4])
        for i in range(nh):  # Headbox SW version
            men.write(natus[4496+i*10:4496+i*10+10])
        men.write(natus[4536:4557])
        shrt = []  # To write to MEN file
        while len(shrt) < nc / 8:
            shrt.append(0)
        shorted = []  # To keep track of for rest of Python program
        for i in range(nc):
            if natus[4560+i*2] == 1:
                shrt[math.floor(i/8)] += 2 ** (i % 8)
            shorted.append(natus[4560+i*2])
        men.write(bytes(shrt))  # Shorted
        men.write(natus[6608:6608+nc*2])  # Frequency factor
        fqb = False
        for i in range(1024):
            if (int.from_bytes(natus[6608+i*2:6608+i*2+2],
                               byteorder='little') != 32767):
                fqb = True
        j = 8656
    else:
        print('ERROR: unsupported file schema.')
        return
    if menv == 1:
        while j < len(natus):
            men.write(natus[j:j+1])  # Event byte
            j += 1
            if fqb:
                men.write(natus[j:j+1])  # Frequency byte
                j += 1
            deltaMask = []
            for i in range(int(nc / 8 + 0.5)):
                bits = []
                nn = natus[j+i]
                for k in range(8):
                    if nn >= 2 ** (7-k):
                        bits.insert(0, 1)
                        nn -= 2 ** (7-k)
                    else:
                        bits.insert(0, 0)
                for a in bits:
                    deltaMask.append(a)
            j += int(nc / 8 + 0.5)
            numBytes = []
            outp = []
            for i in range(len(shorted)):
                if shorted[i] == 0:
                    if deltaMask[i] == 0:
                        numBytes.append(0)
                        outp.append(natus[j:j+1])
                        j += 1
                    elif deltaMask[i] == 1:
                        if natus[j] == 255 and natus[j+1] == 255:
                            numBytes.append(3)
                        else:
                            numBytes.append(1)
                        outp.append(natus[j:j+2])
                        j += 2
            for i in range(len(numBytes)):
                if numBytes[i] == 3:
                    if natus[j+3] == 0:
                        numBytes[i] = 2
                        outp[i] = natus[j:j+3]
                    else:
                        outp[i] = natus[j:j+4]
                    j += 4
            while len(numBytes) % 4 != 0:
                numBytes.append(0)
            bt = 0
            for i in range(len(numBytes)):
                bt += numBytes[i] * 2 ** ((i % 4) * 2)
                if i % 4 == 3:
                    men.write(bt.to_bytes(1, 'little'))
                    bt = 0
            for a in outp:
                for b in a:
                    men.write(b.to_bytes(1, 'little'))
    elif menv == 2:
        while j < len(natus):
            men.write(natus[j:j+1])  # Event byte
            j += 1
            if fqb:
                men.write(natus[j:j+1])  # Frequency byte
                j += 1
            deltaMask = []
            for i in range(int(nc / 8 + 0.5)):
                bits = []
                nn = natus[j+i]
                for k in range(8):
                    if nn >= 2 ** (7-k):
                        bits.insert(0, 1)
                        nn -= 2 ** (7-k)
                    else:
                        bits.insert(0, 0)
                for a in bits:
                    deltaMask.append(a)
            j += int(nc / 8 + 0.5)
            bits = []
            for i in range(len(shorted)):
                if shorted[i] == 0:
                    if deltaMask[i] == 0:
                        sb = sepBits(natus[j:j+1])
                        k = 6
                        while k >= 0 and sb[k] == 0:
                            k -= 1
                        bits.append([sb[7]] + sb[:k+1])
                        j += 1
                    elif deltaMask[i] == 1:
                        if natus[j] == 255 and natus[j+1] == 255:
                            bits.append([])
                        else:
                            sb = sepBits(natus[j:j+2])
                            k = 14
                            while k >= 0 and sb[k] == 0:
                                k -= 1
                            bits.append([sb[15]] + sb[:k+1])
                        j += 2
            for i in range(len(bits)):
                if len(bits[i]) == 0:
                    sb = sepBits(natus[j:j+4])
                    k = 30
                    while k >= 0 and sb[k] == 0:
                        k -= 1
                    bits[i] = [sb[31]] + sb[:k+1]
                    j += 4
            outp = []
            for a in bits:
                for b in sepBits([len(a)-1])[:5]:
                    outp.append(b)
                for b in a[:len(a)-1]:
                    outp.append(b)
            men.write(bytes(comBits(outp)))
    men.close()


if __name__ == '__main__':
    natus2men(sys.argv[1], sys.argv[2], sys.argv[3])
