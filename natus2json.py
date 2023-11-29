# Nathan Holmes-King
# 2023-10-25

import sys
from datetime import datetime
from datetime import timezone
import os
import time

"""
WORK IN PROGRESS.

Command-line arguments:
1. input directory
2. output directory

PEP-8 compliant.
"""


def toInt(lst):
    """
    Convert a list of bytes into an int, and then to a string.
    Assumes little-endian.
    """
    t = 0
    for i in range(len(lst)):
        t += lst[i] * 2 ** (i * 8)
    if lst[len(lst)-1] > 127:
        t -= (2 ** (len(lst) * 8) - 1)
    return str(t)


def toPlusInt(lst):
    """
    Convert a list of bytes into an unsigned int, and then to a string.
    Assumes little-endian.
    """
    t = 0
    for i in range(len(lst)):
        t += lst[i] * 2 ** (i * 8)
    return str(t)


def toDouble(lst):  # VERIFY signed vs. unsigned
    if toInt(lst[:4]) == '0':
        return toPlusInt(lst[4:])
    else:
        return str(int(toPlusInt(lst[:4])) * 256 + int(toPlusInt(lst[4:])))


def toFileTime(lst):
    """
    Not in use.
    """
    t = int(toInt(lst))
    s = datetime.fromtimestamp(int(t / 1e7) -
                               11644473600).replace(tzinfo=timezone.utc)
    u = t % 1e7
    return s.strftime('%Y-%m-%d %H:%M:%S') + '.' + '{:07d}'.format(u)


def encode(char):
    """
    Convert a list of bytes representing chars into a string.
    """
    s = ''
    for a in char:
        if a == 0:
            return s
        s += chr(a)
    return s


def encodeWithUTF8(char, encoding):
    """
    Convert a list of bytes representing chars into a string.
    Not in use.
    """
    s = ''
    if encoding == 'ascii':
        for a in char:
            if a == 0:
                return s
            s += chr(a)
    elif encoding == 'utf8':
        i = 0
        try:
            while i < len(char):
                k = 0
                if char[i] >= 128 + 64 + 32 + 16:
                    k += (char[i] - (128 + 64 + 32 + 16)) * 64 ** 3
                    i += 1
                    k += (char[i] - 128) * 64 ** 2
                    i += 1
                    k += (char[i] - 128) * 64
                    i += 1
                    k += char[i] - 128
                elif char[i] >= 128 + 64 + 32:
                    k += (char[i] - (128 + 64 + 32)) * 64 ** 2
                    i += 1
                    k += (char[i] - 128) * 64
                    i += 1
                    k += char[i] - 128
                elif char[i] >= 128 + 64:
                    k += (char[i] - (128 + 64)) * 64
                    i += 1
                    k += char[i] - 128
                else:
                    k += char[i]
                s += chr(k)
                i += 1
        except KeyError:
            return s
    return s


def toGUID(inp):
    s = ''
    for i in range(16):
        s += '{:02x}'.format(inp[i])
        if i in [3, 5, 7, 9]:
            s += '-'
    return s


def sepList(lstr):
    """
    Take a string of a Natus list and return a Python list.
    """
    rl = []
    paren = 0
    quote = False
    lstr = lstr[:len(lstr)-1] + ',)'
    s = ''
    for i in range(len(lstr)):
        if lstr[i] in ' \n\t' and (not quote):
            continue
        elif lstr[i] == '(' and (not quote):
            paren += 1
            if paren < 2:
                continue
        elif lstr[i] == ')' and (not quote):
            paren -= 1
            if paren < 1:
                continue
        elif lstr[i] == '"' and (i == 0 or lstr[i-1] != '\\' or
                                 (lstr[i-1] == '\\' and i > 1 and
                                  lstr[i-2] == '\\')):
            quote = not quote
            if paren < 3:
                continue
        elif lstr[i] == ',' and (not quote) and paren == 1:
            if len(s) > 1 and s[0] == '(':
                if s[1] == '.':
                    rl.append(sepKeyTree(s))
                else:
                    rl.append(sepList(s))
            else:
                try:
                    rl.append(int(s))
                except ValueError:
                    try:
                        rl.append(float(s))
                    except ValueError:
                        rl.append(s)
                s = ''
            continue
        s += lstr[i]
    return rl


dt_fields = ['HBCalDate']
bool_fields = ['PatientStatus.Normal',
               'PatientStatus.MentallyChallenged',
               'PatientStatus.Awake',
               'PatientStatus.Drowsy',
               'PatientStatus.Asleep',
               'PatientStatus.Uncooperative',
               'PatientStatus.Tense',
               'PatientStatus.Confused',
               'PatientStatus.BehaviorDifficulty',
               'PatientStatus.Aphasic',
               'PatientStatus.SemiComa',
               'PatientStatus.Coma',
               'PatientStatus.StatusEpilepticus',
               'HBIsCalibrated',
               'ShowWaveforms',
               'ReadOnly',
               'Deleted',
               'IsDoneScanning',
               'UseCreator']


def sepKeyTree(lstr):
    """
    Take a string of a Natus key tree and return a Python dict.
    """
    rd = {}
    paren = 0
    quote = False
    k = 0
    lstr = lstr[:len(lstr)-1] + ',)'
    s = ''
    t = ''
    for i in range(len(lstr)):
        if lstr[i] in ' \n\t' and (not quote):
            continue
        elif lstr[i] == '(' and (not quote):
            paren += 1
            if paren < 3:
                continue
        elif lstr[i] == ')' and (not quote):
            paren -= 1
            if paren < 2:
                continue
        elif lstr[i] == '"' and (i == 0 or lstr[i-1] != '\\' or
                                 (lstr[i-1] == '\\' and i > 1 and
                                  lstr[i-2] == '\\')):
            quote = not quote
            if paren < 3:
                continue
        elif lstr[i] == ',' and (not quote):
            if paren == 1:
                if k % 2 == 1:
                    if len(t) > 1 and t[0] == '(':
                        if t[1] == '.':
                            rd[s] = sepKeyTree(t)
                        else:
                            rd[s] = sepList(t)
                    else:
                        try:
                            rd[s] = int(t)
                            if s in dt_fields:
                                rd[s] = datetime.\
                                    strftime(datetime.
                                             fromtimestamp(rd[s],
                                                           tz=timezone.utc),
                                             '%Y-%m-%dT%H:%M:%SZ')
                            elif s in bool_fields:
                                if t == 0:
                                    rd[s] = False
                                else:
                                    rd[s] = True
                        except ValueError:
                            try:
                                rd[s] = float(t)
                            except ValueError:
                                rd[s] = t
                    s = ''
                    t = ''
                k = 0
                continue
            elif paren == 2:
                k = 1
                continue
        elif lstr[i] == '.' and (not quote) and paren < 3:
            continue
        if paren > 1:
            if k == 0:
                s += lstr[i]
            elif k == 1:
                t += lstr[i]
    return sepDots(rd)


def sepDots(ind):
    """
    For key trees: split indexes with dots in the name into nested dicts.
    Supports up to 3 levels.
    """
    newind = {}
    for a in ind:
        if type(ind[a]) is dict:
            ind[a] = sepDots(ind[a])
        if '.' in a:
            sp = a.split('.')
            try:
                newind[sp[0]]
            except KeyError:
                newind[sp[0]] = {}
            if len(sp) == 2:
                newind[sp[0]][sp[1]] = ind[a]
            elif len(sp) == 3:
                try:
                    newind[sp[0]][sp[1]]
                except KeyError:
                    newind[sp[0]][sp[1]] = {}
                newind[sp[0]][sp[1]][sp[2]] = ind[a]
        else:
            newind[a] = ind[a]
    return newind


def listToString(ind, numTabs):
    """
    Return a JSON string representation of a list.
    """
    r = ''
    for a in ind:
        if type(a) is int or type(a) is float:
            r += ',\n' + '\t' * numTabs + str(a)
        elif type(a) is str:
            r += ',\n' + '\t' * numTabs + '"' + a + '"'
        elif type(a) is bool:
            r += ',\n' + '\t' * numTabs + str(a).lower()
        elif type(a) is list:
            r += ',\n' + '\t' * numTabs + '['
            r += listToString(a, numTabs + 1)
            r += '\n' + '\t' * numTabs + ']'
        elif type(a) is dict:
            r += ',\n' + '\t' * numTabs + '{'
            r += dictToString(a, numTabs + 1)
            r += '\n' + '\t' * numTabs + '}'
    if len(r) > 0 and r[0] == ',':
        return r[1:]
    else:
        return r


def dictToString(ind, numTabs):
    """
    Return a JSON string representation of a dict.
    """
    r = ''
    for a in ind:
        if type(ind[a]) is int or type(ind[a]) is float:
            r += ',\n' + '\t' * numTabs + '"' + a + '": ' + str(ind[a])
        elif type(ind[a]) is bool:
            r += ',\n' + '\t' * numTabs + '"' + a + '": ' + str(ind[a]).lower()
        elif type(ind[a]) is str:
            r += ',\n' + '\t' * numTabs + '"' + a + '": "' + ind[a] + '"'
        elif type(ind[a]) is list:
            r += ',\n' + '\t' * numTabs + '"' + a + '": ['
            r += listToString(ind[a], numTabs + 1)
            r += '\n' + '\t' * numTabs + ']'
        elif type(ind[a]) is dict:
            r += ',\n' + '\t' * numTabs + '"' + a + '": {'
            r += dictToString(ind[a], numTabs + 1)
            r += '\n' + '\t' * numTabs + '}'
    if len(r) > 0 and r[0] == ',':
        return r[1:]
    else:
        return r


chindex = {1: (['C3', 'C4', 'CZ', 'F3', 'F4', 'F7', 'F8', 'FZ', 'FP1', 'FP2',
                'FPZ', 'O1', 'O2', 'P3', 'P4', 'PZ', 'T3', 'T4', 'T5', 'T6'] +
               ['AUX' + str(i) for i in range(1, 9)] +
               ['PG1', 'PG2', 'A1', 'A2']),
           3: (['C' + str(i) for i in range(1, 129)] + ['OSAT', 'PR'] +
               ['C' + str(i) for i in range(131, 257)]),
           4: ['AC1', 'AC2', 'Ref', 'Fp1', 'F7', 'T3', 'T5', 'O1', 'F3', 'C3',
               'P3', 'Fz', 'Cz', 'Pz', 'F4', 'C4', 'P4', 'Fp2', 'F8', 'T4',
               'T6', 'O2', 'AC23', 'AC24', 'DC1', 'DC2', 'DC3', 'DC4'],
           5: ['C3', 'C4', 'O1', 'O2', 'A1', 'A2', 'LOC', 'ROC', 'CHIN1',
               'CHIN2', 'ECGL', 'ECGR', 'LAT1', 'RAT1', 'LAT2', 'RAT2', 'X1',
               'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9', 'X10', 'CHEST',
               'ABD', 'FLOW', 'SNORE', 'DIF1', 'DIF2', 'POSITION', 'PRES',
               'DC1', 'DC2', 'DC3', 'DC4', 'DC5', 'DC6', 'OSAT', 'PR'],
           6: ['AC1', 'AC2', 'Ref', 'Fp1', 'F7', 'T3', 'T5', 'O1', 'F3', 'C3',
               'P3', 'Fz', 'Cz', 'Pz', 'F4', 'C4', 'P4', 'Fp2', 'F8', 'T4',
               'T6', 'O2', 'AC23', 'AC24', 'AC25', 'AC26', 'AC27', 'AC28',
               'AC29', 'AC30', 'AC31', 'AC32', 'DC1', 'DC2', 'DC3', 'DC4'],
           8: ['Ref', 'Fp1', 'F7', 'T3', 'A1', 'T5', 'O1', 'F3', 'C3', 'P3',
               'Fpz', 'Fz', 'Cz', 'Pz', 'Fp2', 'F8', 'T4', 'A2', 'T6', 'O2',
               'F4', 'C4', 'P4', 'X1', 'X2'],
           9: (['Ref', 'Fp1', 'F7', 'T3', 'A1', 'T5', 'O1', 'F3', 'C3', 'P3',
                'Fpz', 'Fz', 'Cz', 'Pz', 'Fp2', 'F8', 'T4', 'A2', 'T6', 'O2',
                'F4', 'C4', 'P4'] + ['X' + str(i) for i in range(1, 11)]),
           14: ['C3', 'C4', 'O1', 'O2', 'A1', 'A2', 'Cz', 'F3', 'F4', 'F7',
                'F8', 'Fz', 'Fp1', 'Fp2', 'Fpz', 'P3', 'P4', 'Pz', 'T3', 'T4',
                'T5', 'T6', 'LOC', 'ROC', 'CHIN1', 'CHIN2', 'ECGL', 'ECGR',
                'LAT1', 'LAT2', 'RAT1', 'RAT2', 'CHEST', 'ABD', 'FLOW',
                'SNORE', 'DIF5', 'DIF6', 'POS', 'DC2', 'DC3', 'DC4', 'DC5',
                'DC6', 'DC7', 'DC8', 'DC9', 'DC10', 'OSAT', 'PR'],
           15: ['Fp1', 'F7', 'T3', 'A1', 'T5', 'O1', 'F3', 'C3', 'P3', 'Fpz',
                'Fz', 'Cz', 'Pz', 'Fp2', 'F8', 'T4', 'A2', 'T6', 'O2', 'F4',
                'C4', 'P4', 'X1', 'X2', 'DIF1', 'DIF2', 'DIF3', 'DIF4', 'DC1',
                'DC2', 'DC3', 'DC4', 'OSAT', 'PR'],
           17: ['Fp1', 'F7', 'T3', 'T5', 'O1', 'F3', 'C3', 'P3', 'A1', 'Fz',
                'Cz', 'Fpz', 'Pz', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7',
                'X8', 'X9', 'Fp2', 'X10', 'F8', 'X11', 'T4', 'X12', 'T6',
                'X13', 'O2', 'X14', 'F4', 'X15', 'C4', 'X16', 'P4', 'X17',
                'A2', 'X18', 'DC1', 'DC2', 'DC3', 'DC4', 'OSAT', 'PR'],
           19: ['C3', 'C4', 'CZ', 'F3', 'F4', 'F7', 'F8', 'FZ', 'FP1', 'FP2',
                'FPZ', 'O1', 'O2', 'P3', 'P4', 'PZ', 'T3', 'T4', 'T5', 'T6',
                'AUX1', 'AUX2', 'AUX3', 'AUX4', 'AUX5', 'AUX6', 'AUX7', 'AUX8',
                'PG1', 'PG2', 'A1', 'A2'],
           21: (['C' + str(i) for i in range(1, 129)] + ['PR', 'OSAT'] +
                ['C' + str(i) for i in range(131, 257)]),
           22: ['Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 'T3', 'C3', 'Cz',
                'C4', 'T4', 'T5', 'P3', 'Pz', 'P4', 'T6', 'O1', 'O2', 'A1',
                'A2', 'Pg1', 'Pg2', 'Oz', 'X1', 'X2', 'X3', 'X4', 'X5', 'X6',
                'X7', 'X8', 'DC1', 'DC2', 'DC3', 'DC4', 'DC5', 'DC6', 'DC7',
                'DC8', 'OSAT', 'PR', 'POS'],
           23: ['Pg1', 'Pg2', 'Eogl', 'Fp1', 'Fp2', 'Eogr', 'T1', 'F7', 'F3',
                'Fz', 'F4', 'F8', 'T2', 'A1', 'T3', 'C3', 'Cz', 'C4', 'T4',
                'A2', 'T5', 'P3', 'Pz', 'P4', 'T6', 'O1', 'Oz', 'O2', 'X1',
                'X2', 'X3', 'X4', 'DC1', 'DC2', 'DC3', 'DC4', 'OSAT', 'PR',
                'POS']}


def natus2json(filename, jsonname):
    """
    Main function.
    """
    fex = filename[len(filename)-3:]
    if fex == 'old':
        fex = filename[len(filename)-7:len(filename)-4]
    infile = open(filename, 'rb')
    natus = infile.read()
    infile.close()
    jsonfile = open(jsonname, 'w')
    jsonfile.write('{\n\t')
    s = []
    sn1 = natus[16]
    sn2 = natus[18]
    if fex == 'vtc':
        base_schema = -1
        file_schema = -1
    elif sn2 == 1:
        base_schema = 1
        file_schema = sn1
    else:
        base_schema = 0
        file_schema = sn2
    if fex != 'vtc':
        jsonfile.write('"m_file_guid": "')
        jsonfile.write(toGUID(natus[:16]))
        jsonfile.write('",\n\t"m_file_schema": ')
    if base_schema == 0 and fex != 'vtc':
        jsonfile.write(toInt(natus[16:20]))
        jsonfile.write(',\n\t"m_creation_time": "')
        jsonfile.write(datetime.strftime(
            datetime.fromtimestamp(int(toInt(natus[20:24])), tz=timezone.utc),
            '%Y-%m-%dT%H:%M:%SZ'))
        jsonfile.write('",\n\t"m_product_version_high": ')
        jsonfile.write(toInt(natus[24:28]))
        jsonfile.write(',\n\t"m_product_version_low": ')
    if base_schema == 1 and fex != 'vtc':
        jsonfile.write(toInt(natus[16:18]))
        jsonfile.write(',\n\t"m_base_schema": ')
        jsonfile.write(toInt(natus[18:20]))
        jsonfile.write(',\n\t"m_creation_time": "')
        jsonfile.write(datetime.strftime(
            datetime.fromtimestamp(int(toInt(natus[20:24])), tz=timezone.utc),
            '%Y-%m-%dT%H:%M:%SZ'))
        jsonfile.write('",\n\t"m_patient_id": ')
        jsonfile.write(toInt(natus[24:28]))
        jsonfile.write(',\n\t"m_study_id": ')
    if fex != 'vtc':
        jsonfile.write(toInt(natus[28:32]))
        jsonfile.write(',\n\t"m_pat_last_name": "')
        jsonfile.write(encode(natus[32:112]))
        jsonfile.write('",\n\t"m_pat_first_name": "')
        jsonfile.write(encode(natus[112:192]))
        jsonfile.write('",\n\t"m_pat_middle_name": "')
        jsonfile.write(encode(natus[192:272]))
        jsonfile.write('",\n\t"m_pat_id": "')
        jsonfile.write(encode(natus[272:352]))
        jsonfile.write('"')
    if file_schema == 3 and fex == 'eeg':
        i = 352
        while natus[i] != 0:
            i += 1
        t = sepKeyTree(encode(natus[352:i]))
        if t != {'': ''}:
            jsonfile.write(',' + dictToString(t, 1))
    if file_schema in range(5, 10) and fex == 'erd':
        jsonfile.write(',\n\t"m_sample_freq": ')
        jsonfile.write(toDouble(natus[352:360]))
        jsonfile.write(',\n\t"m_num_channels": ')
        jsonfile.write(toInt(natus[360:364]))
        num_channels = int(toInt(natus[360:364]))
        jsonfile.write(',\n\t"m_deltabits": ')
        jsonfile.write(toInt(natus[364:368]))
        jsonfile.write(',\n\t"m_phys_chan": ')
    if file_schema == 5 and fex == 'erd':
        phys_chan = []
        s = '['
        for j in range(32):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
            phys_chan.append(int(toInt(natus[368 + j * 4:368 + (j + 1) * 4])))
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
        headbox_type = int(toInt(natus[496:500]))
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[496 + j * 4:496 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sn": ')
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[512 + j * 4:512 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sw_version": ')
        s = '['
        for j in range(4):
            t = encode(natus[528 + j * 10:528 + (j + 1) * 10])
            s += '\n\t\t"' + t + '",'
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_dsp_hw_version": "')
        jsonfile.write(encode(natus[568:578]))
        jsonfile.write('",\n\t"m_dsp_sw_version": "')
        jsonfile.write(encode(natus[578:588]))
        sw = encode(natus[578:588]).split('.')
        sw1 = int(sw[0])
        if len(sw) > 1:
            sw2 = int(sw[1])
        else:
            sw2 = 0
        jsonfile.write('",\n\t"m_discardbits": ')
        jsonfile.write(toInt(natus[588:592]))
        discardbits = int(toInt(natus[588:592]))
        jsonfile.write(',\n\t"data": [')  # "data" not specified in doc
        j = 592
        if j < len(natus):
            jsonfile.write(',')
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            # Delta information
            r = []
            for i in range(num_channels):
                r.append(int(toInt(natus[j+i:j+i+1])))
            j += num_channels
            # Absolute channel values
            for i in range(len(r)):
                if r[i] == -128:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '{'
            if headbox_type == 1 or headbox_type == 3:
                for i in range(len(r)):
                    s += ('\n\t\t\t\t"' + chindex[headbox_type][phys_chan[i]] +
                          '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                            2 ** discardbits, 2)) + ',')
            elif headbox_type == 4:
                for i in range(len(r)):
                    if i in range(0, 24):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(24, 28):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] < 3 or sw[1] == 3 and sw[2] < 4):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                            (159.8 / 249.5)) * 2 **
                                    discardbits) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((1e7 / (2 ** 10 - 0.5)) /
                                                  2 ** 6)
                                    * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] > 3 or sw[1] == 3 and sw[2] > 3):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                          (159.8 / 249.5)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((2e7 / 65536) / 2 ** 6)
                                          * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 6:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 36):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 8:
                for i in range(len(r)):
                    if i in range(0, 25):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(25, 27):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 9:
                for i in range(len(r)):
                    if i in range(0, 33):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(33, 35):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            else:
                for i in range(len(r)):
                    s += ('\n\t\t\t\t"C' + str(i) +
                          '": ' + str(r[i] * (8711 / (2 ** 21 - 0.5)) * 2 **
                                      discardbits) + ',')
            s = s[:len(s)-1]
            s += '\n\t\t\t}'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 6 and fex == 'erd':
        s = '['
        for j in range(128):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
        headbox_type = int(toInt(natus[496:500]))
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[880 + j * 4:880 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sn": ')
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[896 + j * 4:896 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sw_version": ')
        s = '['
        for j in range(4):
            t = encode(natus[912 + j * 10:912 + (j + 1) * 10])
            s += '\n\t\t"' + t + '",'
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_dsp_hw_version": "')
        jsonfile.write(encode(natus[952:962]))
        jsonfile.write('",\n\t"m_dsp_sw_version": "')
        jsonfile.write(encode(natus[962:972]))
        jsonfile.write('",\n\t"m_discardbits": ')
        jsonfile.write(toInt(natus[972:976]))
        jsonfile.write(',\n\t"data": [')  # "data" not specified in doc
        j = 976
        if j < len(natus):
            jsonfile.write(',')
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            # Delta information
            r = []
            for i in range(num_channels):
                r.append(int(toInt(natus[j+i:j+i+1])))
            j += num_channels
            # Absolute channel values
            for i in range(len(r)):
                if r[i] == -128:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '{'
            if headbox_type == 1 or headbox_type == 3:
                for i in range(len(r)):
                    s += ('\n\t\t\t\t"' + chindex[headbox_type][phys_chan[i]] +
                          '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                            2 ** discardbits, 2)) + ',')
            elif headbox_type == 4:
                for i in range(len(r)):
                    if i in range(0, 24):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(24, 28):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] < 3 or sw[1] == 3 and sw[2] < 4):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                            (159.8 / 249.5)) * 2 **
                                    discardbits) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((1e7 / (2 ** 10 - 0.5)) /
                                                  2 ** 6)
                                    * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] > 3 or sw[1] == 3 and sw[2] > 3):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                          (159.8 / 249.5)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((2e7 / 65536) / 2 ** 6)
                                          * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 6:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 36):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 8:
                for i in range(len(r)):
                    if i in range(0, 25):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(25, 27):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 9:
                for i in range(len(r)):
                    if i in range(0, 33):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(33, 35):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            else:
                for i in range(len(r)):
                    s += ('\n\t\t\t\t"C' + str(i) +
                          '": ' + str(r[i] * (8711 / (2 ** 21 - 0.5)) * 2 **
                                      discardbits) + ',')
            s = s[:len(s)-1]
            s += '\n\t\t\t}'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 7 and fex == 'erd':
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
        headbox_type = int(toInt(natus[496:500]))
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[4464 + j * 4:4464 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sn": ')
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[4480 + j * 4:4480 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sw_version": ')
        s = '['
        for j in range(4):
            t = encode(natus[4496 + j * 10:4496 + (j + 1) * 10])
            s += '\n\t\t"' + t + '",'
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_dsp_hw_version": "')
        jsonfile.write(encode(natus[4536:4546]))
        jsonfile.write('",\n\t"m_dsp_sw_version": "')
        jsonfile.write(encode(natus[4546:4556]))
        jsonfile.write(',\n\t"m_discardbits": ')
        jsonfile.write(toInt(natus[4556:4560]))
        jsonfile.write(',\n\t"data": [')  # "data" not specified in doc
        j = 4560
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            # Delta information
            r = []
            for i in range(num_channels):
                r.append(int(toInt(natus[j+i:j+i+1])))
            j += num_channels
            # Absolute channel values
            for i in range(len(r)):
                if r[i] == -128:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '{'
            if headbox_type == 1 or headbox_type == 3:
                for i in range(len(r)):
                    s += ('\n\t\t\t\t"' + chindex[headbox_type][phys_chan[i]] +
                          '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                            2 ** discardbits, 2)) + ',')
            elif headbox_type == 4:
                for i in range(len(r)):
                    if i in range(0, 24):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(24, 28):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] < 3 or sw[1] == 3 and sw[2] < 4):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                            (159.8 / 249.5)) * 2 **
                                    discardbits) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((1e7 / (2 ** 10 - 0.5)) /
                                                  2 ** 6)
                                    * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] > 3 or sw[1] == 3 and sw[2] > 3):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                          (159.8 / 249.5)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((2e7 / 65536) / 2 ** 6)
                                          * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 6:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 36):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 8:
                for i in range(len(r)):
                    if i in range(0, 25):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(25, 27):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 9:
                for i in range(len(r)):
                    if i in range(0, 33):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(33, 35):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            else:
                for i in range(len(r)):
                    s += ('\n\t\t\t\t"C' + str(i) +
                          '": ' + str(r[i] * (8711 / (2 ** 21 - 0.5)) * 2 **
                                      discardbits) + ',')
            s = s[:len(s)-1]
            s += '\n\t\t\t}'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 8 and fex == 'erd':
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
        headbox_type = int(toInt(natus[4464:4468]))
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[4464 + j * 4:4464 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sn": ')
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[4480 + j * 4:4480 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sw_version": ')
        s = '['
        for j in range(4):
            t = encode(natus[4496 + j * 10:4496 + (j + 1) * 10])
            s += '\n\t\t"' + t + '",'
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_dsp_hw_version": "')
        jsonfile.write(encode(natus[4536:4546]))
        jsonfile.write('",\n\t"m_dsp_sw_version": "')
        jsonfile.write(encode(natus[4546:4556]))
        jsonfile.write('",\n\t"m_discardbits": ')
        jsonfile.write(toInt(natus[4556:4560]))
        discardbits = int(toInt(natus[4556:4560]))
        jsonfile.write(',\n\t"m_shorted": ')
        shorted = []
        num_shorted = 0
        s = '['
        for j in range(1024):
            s += '\n\t\t' + str(bool(natus[4560 + j * 2])).lower() + ','
            shorted.append(bool(natus[4560 + j * 2]))
            if bool(natus[4560 + j * 2]):
                num_shorted += 1
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_frequency_factor": ')
        freqfac = False
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[6608 + j * 2:6608 + (j + 1) * 2]) + ','
            if int(toInt(natus[6608 + j * 2:6608 + (j + 1) * 2])) != 32767:
                freqfac = True
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"data": [')  # "data" not specified in doc
        j = 8656
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            if freqfac:
                jsonfile.write(',\n\t\t\t"frequency_byte": ')
                jsonfile.write(toInt(natus[j:j+1]))
                j += 1
            delta_mask = []
            for i in range(int(num_channels / 8 + 0.5)):
                bits = []
                nn = natus[j+i]
                for k in range(8):
                    if nn >= 2 ** (7-k):
                        bits.insert(0, 1)
                        nn -= 2 ** (7-k)
                    else:
                        bits.insert(0, 0)
                for a in bits:
                    delta_mask.append(a)
            j += int(num_channels / 8 + 0.5)
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            # Delta information
            r = []
            i = 0
            k = 0
            while k < num_channels:
                if delta_mask[k] == 1:
                    if not shorted[k]:
                        r.append(int(toInt(natus[j+i:j+i+2])))
                        i += 2
                else:
                    if not shorted[k]:
                        r.append(int(toInt(natus[j+i:j+i+1])))
                        i += 1
                k += 1
            j += i
            # Absolute channel values
            for i in range(len(r)):
                if r[i] == -32768:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '{'
            c = 0
            if headbox_type == 1 or headbox_type == 3:
                for i in range(len(r)):
                    while shorted[c]:
                        c += 1
                    s += ('\n\t\t\t\t"' + chindex[headbox_type][phys_chan[c]] +
                          '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                            2 ** discardbits, 2)) + ',')
                    c += 1
            elif headbox_type == 4:
                for i in range(len(r)):
                    if i in range(0, 24):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(24, 28):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] < 3 or sw[1] == 3 and sw[2] < 4):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                            (159.8 / 249.5)) * 2 **
                                    discardbits) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((1e7 / (2 ** 10 - 0.5)) /
                                                  2 ** 6)
                                    * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] > 3 or sw[1] == 3 and sw[2] > 3):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                          (159.8 / 249.5)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((2e7 / 65536) / 2 ** 6)
                                          * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 6:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 36):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 8:
                for i in range(len(r)):
                    if i in range(0, 25):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(25, 27):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 9:
                for i in range(len(r)):
                    if i in range(0, 33):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(33, 35):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            else:
                for i in range(len(r)):
                    while shorted[c]:
                        c += 1
                    s += ('\n\t\t\t\t"C' + str(c+1) +
                          '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                            2 ** discardbits, 2)) + ',')
                    c += 1
            s = s[:len(s)-1]
            s += '\n\t\t\t}'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
    if file_schema == 9 and fex == 'erd':
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
        headbox_type = int(toInt(natus[4464:4468]))
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[4464 + j * 4:4464 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sn": ')
        s = '['
        for j in range(4):
            s += '\n\t\t' + toInt(natus[4480 + j * 4:4480 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_sw_version": ')
        s = '['
        for j in range(4):
            t = encode(natus[4496 + j * 10:4496 + (j + 1) * 10])
            s += '\n\t\t"' + t + '",'
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_dsp_hw_version": "')
        jsonfile.write(encode(natus[4536:4546]))
        jsonfile.write('",\n\t"m_dsp_sw_version": "')
        jsonfile.write(encode(natus[4546:4556]))
        jsonfile.write('",\n\t"m_discardbits": ')
        jsonfile.write(toInt(natus[4556:4560]))
        discardbits = int(toInt(natus[4556:4560]))
        jsonfile.write(',\n\t"m_shorted": ')
        shorted = []
        num_shorted = 0
        s = '['
        for j in range(1024):
            s += '\n\t\t' + str(bool(natus[4560 + j * 2])).lower() + ','
            shorted.append(bool(natus[4560 + j * 2]))
            if bool(natus[4560 + j * 2]):
                num_shorted += 1
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_frequency_factor": ')
        freqfac = False
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[6608 + j * 2:6608 + (j + 1) * 2]) + ','
            if int(toInt(natus[6608 + j * 2:6608 + (j + 1) * 2])) != 32767:
                freqfac = True
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"data": [')  # "data" not specified in doc
        j = 8656
        nsam = 0
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            if freqfac:
                jsonfile.write(',\n\t\t\t"frequency_byte": ')
                jsonfile.write(toInt(natus[j:j+1]))
                j += 1
            delta_mask = []
            for i in range(int(num_channels / 8 + 0.5)):
                bits = []
                nn = natus[j+i]
                for k in range(8):
                    if nn >= 2 ** (7-k):
                        bits.insert(0, 1)
                        nn -= 2 ** (7-k)
                    else:
                        bits.insert(0, 0)
                for a in bits:
                    delta_mask.append(a)
            j += int(num_channels / 8 + 0.5)
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            # Delta information
            r = []
            i = 0
            k = 0
            while k < num_channels:
                if delta_mask[k] == 1:
                    if not shorted[k]:
                        r.append(int(toInt(natus[j+i:j+i+2])))
                        i += 2
                else:
                    if not shorted[k]:
                        r.append(int(toInt(natus[j+i:j+i+1])))
                        i += 1
                k += 1
            j += i
            # Absolute channel values
            for i in range(len(r)):
                if r[i] == -32768:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '{'
            c = 0
            if headbox_type in [1, 3, 19]:
                for i in range(len(r)):
                    while shorted[c]:
                        c += 1
                    s += ('\n\t\t\t\t"' + chindex[headbox_type][phys_chan[c]]
                          + '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                              2 ** discardbits, 2)) + ',')
                    c += 1
            elif headbox_type == 4:
                for i in range(len(r)):
                    if i in range(0, 24):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(24, 28):
                        s += ('\n\t\t\t\t"' + chindex[4][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] < 3 or sw[1] == 3 and sw[2] < 4):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                            (159.8 / 249.5)) * 2 **
                                    discardbits) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((1e7 / (2 ** 10 - 0.5)) /
                                                  2 ** 6)
                                    * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 5 and (sw[1] > 3 or sw[1] == 3 and sw[2] > 3):
                for i in range(len(r)):
                    if i in range(0, 26):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(26, 32):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((8711 / (2 ** 21 - 0.5)) /
                                          (159.8 / 249.5)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(32, 40):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * ((2e7 / 65536) / 2 ** 6)
                                          * 2 ** discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[5][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 6:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 36):
                        s += ('\n\t\t\t\t"' + chindex[6][phys_chan[i]] + '": '
                              + str(round(r[i] * (5e6 / (2 ** 10 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
            elif headbox_type == 8:
                for i in range(len(r)):
                    if i in range(0, 25):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(25, 27):
                        s += ('\n\t\t\t\t"' + chindex[8][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 9:
                for i in range(len(r)):
                    if i in range(0, 33):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(33, 35):
                        s += ('\n\t\t\t\t"' + chindex[9][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 14:
                for i in range(len(r)):
                    if i in range(0, 38):
                        s += ('\n\t\t\t\t"' + chindex[14][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(38, 48):
                        s += ('\n\t\t\t\t"' + chindex[14][phys_chan[i]] + '": '
                              + str(round(r[i] * ((10800000 / 65536) /
                                                  (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(48, 50):
                        s += ('\n\t\t\t\t"' + chindex[14][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 15:
                for i in range(len(r)):
                    if i in range(0, 28):
                        s += ('\n\t\t\t\t"' + chindex[15][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(28, 32):
                        s += ('\n\t\t\t\t"' + chindex[15][phys_chan[i]] + '": '
                              + str(round(r[i] * ((1e7 / 65536) /
                                                  (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(32, 34):
                        s += ('\n\t\t\t\t"' + chindex[15][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 17:
                for i in range(len(r)):
                    if i in range(0, 40):
                        s += ('\n\t\t\t\t"' + chindex[17][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(40, 44):
                        s += ('\n\t\t\t\t"' + chindex[17][phys_chan[i]] + '": '
                              + str(round(r[i] * ((10800000 / 65536) /
                                                  (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(44, 46):
                        s += ('\n\t\t\t\t"' + chindex[17][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 21:
                for i in range(len(r)):
                    if i in range(0, 128) or i in range(130, 256):
                        s += ('\n\t\t\t\t"' + chindex[21][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(128, 130):
                        s += ('\n\t\t\t\t"' + chindex[21][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 22:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[22][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 40) or i == 42:
                        s += ('\n\t\t\t\t"' + chindex[22][phys_chan[i]] + '": '
                              + str(round(r[i] * ((10800000 / 65536) /
                                                  (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(40, 42):
                        s += ('\n\t\t\t\t"' + chindex[22][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            elif headbox_type == 23:
                for i in range(len(r)):
                    if i in range(0, 32):
                        s += ('\n\t\t\t\t"' + chindex[23][phys_chan[i]] + '": '
                              + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                          2 ** discardbits, 2)) + ',')
                    elif i in range(32, 36) or i == 38:
                        s += ('\n\t\t\t\t"' + chindex[23][phys_chan[i]] + '": '
                              + str(round(r[i] * ((10800000 / 65536) /
                                                  (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
                    elif i in range(36, 38):
                        s += ('\n\t\t\t\t"' + chindex[23][phys_chan[i]] + '": '
                              + str(round(r[i] * (1 / (2 ** 6)) * 2 **
                                          discardbits, 2)) + ',')
            else:  # TODO: Quantum headbox
                for i in range(len(r)):
                    while shorted[c]:
                        c += 1
                    s += ('\n\t\t\t\t"C' + str(c+1) +
                          '": ' + str(round(r[i] * (8711 / (2 ** 21 - 0.5)) *
                                            2 ** discardbits, 2)) + ',')
                    c += 1
            s = s[:len(s)-1]
            s += '\n\t\t\t}'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            nsam += 1
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 3 and fex == 'ent':
        jsonfile.write('\n\t"notes": [')  # "notes" not specified in doc
        j = 352
        while j < len(natus):
            jsonfile.write('\n\t\t{\n\t\t\t"type": ')
            jsonfile.write(toInt(natus[j:j+4]))
            jsonfile.write(',\n\t\t\t"length": ')
            jsonfile.write(toInt(natus[j+4:j+8]))
            jsonfile.write(',\n\t\t\t"prev_length": ')
            jsonfile.write(toInt(natus[j+8:j+12]))
            jsonfile.write(',\n\t\t\t"id": ')
            jsonfile.write(toInt(natus[j+12:j+16]))
            i = j + 16
            while i < len(natus) and natus[i] != 0:
                i += 1
            t = sepKeyTree(encode(natus[j+16:i]))
            if t != {'': ''}:
                jsonfile.write(',' + dictToString(t, 3))
            jsonfile.write('\n\t\t}')
            j = i + 1
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 2 and (fex == 'toc' or fex == 'etc'):  # VERIFY
        jsonfile.write('\n\t"contents": [')  # "contents" not specified in doc
        j = 352
        while j < len(natus):
            jsonfile.write('\n\t\t{\n\t\t\t"offset": ')
            jsonfile.write(toInt(natus[j:j+4]))
            jsonfile.write(',\n\t\t\t"timestamp": ')
            jsonfile.write(toInt(natus[j+4:j+8]))
            jsonfile.write(',\n\t\t\t"sample_num": ')
            jsonfile.write(toInt(natus[j+8:j+12]))
            jsonfile.write(',\n\t\t\t"sample_span": ')
            jsonfile.write(toInt(natus[j+12:j+16]))
            jsonfile.write('\n\t\t}')
            j += 16
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 3 and (fex == 'toc' or fex == 'etc'):  # VERIFY
        jsonfile.write('\n\t"contents": [')  # "contents" not specified in doc
        j = 352
        while j < len(natus):
            jsonfile.write('\n\t\t{\n\t\t\t"offset": ')
            jsonfile.write(toInt(natus[j:j+4]))
            jsonfile.write(',\n\t\t\t"samplestamp": ')
            jsonfile.write(toInt(natus[j+4:j+8]))
            jsonfile.write(',\n\t\t\t"sample_num": ')
            jsonfile.write(toInt(natus[j+8:j+12]))
            jsonfile.write(',\n\t\t\t"sample_span": ')
            jsonfile.write(toInt(natus[j+12:j+16]))
            jsonfile.write('\n\t\t}')
            j += 16
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if (file_schema == 0 or file_schema == 1) and fex == 'snc':  # VERIFY
        jsonfile.write('\n\t"contents": [')  # "contents" not specified in doc
        j = 352
        while j < len(natus):
            jsonfile.write('\n\t\t{\n\t\t\t"sampleStamp": ')
            jsonfile.write(toPlusInt(natus[j:j+4]))  # VERIFY num data type
            jsonfile.write(',\n\t\t\t"sampleTime": ')
            jsonfile.write(toPlusInt(natus[j+4:j+12]))  # VERIFY num data type
            jsonfile.write('\n\t\t}')
            j += 16
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 1 and fex == 'stc':
        jsonfile.write(',\n\t"m_next_segment": ')
        jsonfile.write(toInt(natus[352:356]))
        jsonfile.write(',\n\t"m_final": ')
        jsonfile.write(toInt(natus[356:360]))
        jsonfile.write(',\n\t"m_padding": ')
        s = '['
        for j in range(12):
            s += '\n\t\t' + toInt(natus[360 + j * 4:360 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write('\n\t"contents": [')  # "contents" not specified in doc
        j = 402
        while j < len(natus):
            jsonfile.write('\n\t\t{\n\t\t\t"segment_name": "')
            jsonfile.write(encode(natus[j:j+256]))
            jsonfile.write('",\n\t\t\t"start_stamp": ')
            jsonfile.write(toPlusInt(natus[j+256:j+260]))
            jsonfile.write(',\n\t\t\t"end_stamp": ')
            jsonfile.write(toPlusInt(natus[j+260:j+264]))
            jsonfile.write(',\n\t\t\t"sample_num": ')
            jsonfile.write(toPlusInt(natus[j+264:j+268]))
            jsonfile.write(',\n\t\t\t"sample_span": ')
            jsonfile.write(toPlusInt(natus[j+268:j+272]))
            jsonfile.write('\n\t\t}')
            j += 276
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 3 and fex == 'epo':
        jsonfile.write('\n\t"Schema": {\n\t\t"Major": "')
        jsonfile.write(toInt(natus[0:4]))
        jsonfile.write('",\n\t\t"Minor": ')
        jsonfile.write(toInt(natus[4:8]))
        jsonfile.write(',\n\t\t"Revision": ')
        jsonfile.write(toInt(natus[8:12]))
        jsonfile.write(',\n\t\t"Build": ')
        jsonfile.write(toInt(natus[12:16]))
        jsonfile.write('\n\t},\n\t"StudyInfo": {\n\t\tStudyGuid": "')
        for i in range(16, 25):
            jsonfile.write('{:02x}'.format(natus[i]))
        jsonfile.write('",\n\t\t"PatientGuid": "')
        for i in range(25, 34):
            jsonfile.write('{:02x}'.format(natus[i]))
        jsonfile.write('"\n\t},\n\t"EpochInfo": {\n\t\tEpochLength": ')
        jsonfile.write(toInt(natus[34:38]))
        jsonfile.write(',\n\t\t"TotalEpochs": ')
        jsonfile.write(toInt(natus[38:42]))
        jsonfile.write(',\n\t\t"CurrentEpoch": ')
        jsonfile.write(toInt(natus[42:46]))
        jsonfile.write(',\n\t\t"StartTime": "')
        jsonfile.write(datetime.strftime(
            datetime.fromtimestamp(int(toInt(natus[46:50])), tz=timezone.utc),
            '%Y-%m-%dT%H:%M:%SZ'))
        jsonfile.write('",\n\t\t"SleepTimeBase": ')
        jsonfile.write(toInt(natus[50:54]))
        jsonfile.write(',\n\t\t"Valid": ')
        if natus[54] == 0:
            jsonfile.write('false')
        else:
            jsonfile.write('true')
        jsonfile.write(',\n\t\t"CreationTime": "')
        jsonfile.write(datetime.strftime(
            datetime.fromtimestamp(int(toInt(natus[55:59])), tz=timezone.utc),
            '%Y-%m-%dT%H:%M:%SZ'))
        jsonfile.write('",\n\t\t"CurrentStageName": "')
        j = 59
        while natus[j] != 0:
            j += 1
        jsonfile.write(encode(natus[59:j]))
        j += 1
        jsonfile.write('",\n\t\t"SegmentStartStamp": ')
        jsonfile.write(toInt(natus[j:j+4]))
        jsonfile.write(',\n\t\t"StudyStartStamp": ')
        jsonfile.write(toInt(natus[j+4:j+8]))
        jsonfile.write(',\n\t\t"EpochOffset": ')
        jsonfile.write(toInt(natus[j+8:j+12]))
        jsonfile.write(',\n\t\t"RecoverEpochOffset": ')
        jsonfile.write(toInt(natus[j+12:j+16]))
        jsonfile.write(',\n\t\t"NextFileNum": ')
        jsonfile.write(toInt(natus[j+16:j+20]))
        jsonfile.write('\n\t}')
        jsonfile.write(',\n\t"FriendlyName": "')
        j += 20
        i = j
        while natus[i] != 0:
            i += 1
        jsonfile.write(encode(natus[j:i]))
        j = i + 1
        jsonfile.write('",\n\t"ChannelType": ')
        jsonfile.write(toInt(natus[j:j+4]))
        jsonfile.write(',\n\t"StartEpoch": ')
        jsonfile.write(toInt(natus[j+4:j+8]))
        jsonfile.write(',\n\t"EndEpoch": ')
        jsonfile.write(toInt(natus[j+8:j+12]))
        jsonfile.write(',\n\t"Hidden": ')
        if natus[j+12] == 255 and natus[j+13] == 255:
            jsonfile.write('true')
        elif natus[j+12] == 0 and natus[j+13] == 0:
            jsonfile.write('false')
        else:
            jsonfile.write('null')
        jsonfile.write(',\n\t"Creator": "')
        j += 14
        i = j
        while natus[i] != 0:
            i += 1
        jsonfile.write(encode(natus[j:i]))
        jsonfile.write('",\n\t"Password": "')
        j = i + 1
        i = j
        while natus[i] != 0:
            i += 1
        jsonfile.write(encode(natus[j:i]))
        jsonfile.write('",\n\t"Description": "')
        j = i + 1
        i = j
        while natus[i] != 0:
            i += 1
        jsonfile.write(encode(natus[j:i]))
        jsonfile.write('"')
    if fex == 'vtc':
        jsonfile.write('"VTC": "')
        jsonfile.write(toGUID(natus[:16]))
        jsonfile.write('",\n\t"Schema": ')
        jsonfile.write(toInt(natus[16:20]))
        file_schema = int(toInt(natus[16:20]))
        jsonfile.write(',\n\t"Contents": [')  # "Contents" not specified in doc
    if file_schema == 1 and fex == 'vtc':
        j = 20
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"MpgFileName": ')
            jsonfile.write(encode(natus[j:j+261]))
            jsonfile.write('",\n\t\t\t"View": ')
            jsonfile.write(toInt(natus[j+261:j+265]))
            jsonfile.write(',\n\t\t\t"StartTime": ')
            jsonfile.write(toInt(natus[j+265:j+273]))
            jsonfile.write(',\n\t\t\t"EndTime": ')
            jsonfile.write(toInt(natus[j+273:j+281]))
            jsonfile.write('\n\t\t}')
            j += 281
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 4 and fex == 'vtc':
        j = 20
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"MpgFileName": "')
            jsonfile.write(encode(natus[j:j+261]))
            jsonfile.write('",\n\t\t\t"Location": "')
            jsonfile.write(toGUID(natus[j+261:j+277]))
            jsonfile.write('",\n\t\t\t"StartTime": ')
            jsonfile.write(toInt(natus[j+277:j+285]))
            jsonfile.write(',\n\t\t\t"EndTime": ')
            jsonfile.write(toInt(natus[j+285:j+293]))
            jsonfile.write('\n\t\t}')
            j += 293
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    jsonfile.write('\n}')
    jsonfile.close()


def multipleFiles(indir, outdir):
    for f in os.listdir(indir):
        if f[len(f)-3:] != 'avi':
            try:
                st = time.time()
                natus2json(os.path.join(indir, f),
                           os.path.join(outdir, f + '.json'))
                et = time.time()
                print('DONE', round(et - st, 2), 's', f)
            except IndexError:
                print('FAILED IndexError', round(et - st, 2), 's', f)


if __name__ == '__main__':
    multipleFiles(sys.argv[1], sys.argv[2])
