# Nathan Holmes-King
# 2023-10-25

import sys
from datetime import datetime
from datetime import timezone

"""
WORK IN PROGRESS. TO-DO:
- Conversion Factor

Command-line arguments:
1. input filename
2. output filename
3. source character encoding: "ascii", "utf8"

PEP-8 compliant.
"""


def toInt(lst):
    """
    Convert a list of bytes into an int, and then to a string.
    """
    t = 0
    k = len(lst) - 1
    for i in range(len(lst)):
        t += lst[i] * 2 ** (k * 8)
        k -= 1
    if lst[0] > 127:
        t -= 2 ** (len(lst) * 8)
    return str(t)


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
    if sys.argc < 4 or sys.argv[3] == 'ascii':
        for a in char:
            s += chr(a)
    elif sys.argv[3] == 'utf8':
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


def sepList(lstr):
    """
    Take a string of a Natus list and return a Python list.
    """
    rl = []
    paren = 0
    quote = False
    k = 0
    s = ''
    for i in range(len(lstr)):
        if lstr[i] in ' \n\t' and (not quote):
            continue
        elif lstr[i] == '(' and (not quote):
            paren += 1
            continue
        elif lstr[i] == ')' and (not quote):
            paren -= 1
            continue
        elif lstr[i] == '"' and (i == 0 or lstr[i-1] != '\\' or
                                 (lstr[i-1] == '\\' and i > 1 and
                                  lstr[i-2] == '\\')):
            quote = not quote
            continue
        elif lstr[i] == ',' and (not quote) and paren == 1:
            if s[0] == '(':
                if s[1] == '.':
                    rl.append(sepKeyTree(s))
                else:
                    rl.append(sepList(s))
            else:
                try:
                    rl.append(int(s))
                except TypeError:
                    try:
                        rl.append(float(s))
                    except TypeError:
                        rl.append(s)
                s = ''
            continue
        s += lstr[i]
    rl.append(s)
    return rd


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
    paren = -1
    quote = False
    k = 0
    s = ''
    t = ''
    for i in range(len(lstr)):
        if lstr[i] in ' \n\t' and (not quote):
            continue
        elif lstr[i] == '(' and (not quote):
            paren += 1
            continue
        elif lstr[i] == ')' and (not quote):
            paren -= 1
            continue
        elif lstr[i] == '"' and (i == 0 or lstr[i-1] != '\\' or
                                 (lstr[i-1] == '\\' and i > 1 and
                                  lstr[i-2] == '\\')):
            quote = not quote
            continue
        elif lstr[i] == ',' and (not quote):
            if paren == 1:
                if k % 2 == 1:
                    if s[0] == '(':
                        if s[1] == '.':
                            rd[s] = sepKeyTree(t)
                        else:
                            rd[s] = sepList(t)
                    else:
                        try:
                            rd[s] = int(t)
                            if s in dt_fields:
                                rd[s] = datetime.\
                                        strftime(datetime.fromtimestamp
                                                 (int(toInt(natus[20:24])),
                                                  tz=timezone.utc),
                                                 '%Y-%m-%dT%H:%M:%SZ')
                            elif s in bool_fields:
                                if t == 0:
                                    rd[s] = False
                                else:
                                    rd[s] = True
                        except TypeError:
                            try:
                                rd[s] = float(t)
                            except TypeError:
                                rd[s] = t
                    s = ''
                    t = ''
                k = 0
            elif paren == 2:
                k = 1
            continue
        if k == 0:
            s += lstr[i]
        elif k == 1:
            t += lstr[i]
    rd[s] = t
    return sepDots(rd)


def sepDots(ind):
    """
    For key trees: split indexes with dots in the name into nested dicts.
    Supports up to 3 levels.
    """
    for a in ind:
        if type(ind[a]) is dict:
            ind[a] = sepDots(ind[a])
        else:
            if '.' in a:
                sp = a.split('.')
                try:
                    ind[sp[0]]
                except KeyError:
                    ind[sp[0]] = {}
                if len(sp) == 2:
                    ind[sp[0]][sp[1]] = ind[a]
                elif len(sp) == 3:
                    try:
                        ind[sp[0]][sp[1]]
                    except KeyError:
                        ind[sp[0]][sp[1]] = {}
                    ind[sp[0]][sp[1]][sp[2]] = ind[a]
                del ind[a]


def listToString(ind, numTabs):
    """
    Return a JSON string representation of a list.
    """
    r = ''
    for a in ind:
        if type(ind[a]) is int or type(ind[a]) is float:
            r += ',\n' + '\t' * numTabs + str(ind[a])
        elif type(ind[a]) is str:
            r += ',\n' + '\t' * numTabs + '"' + ind[a] + '"'
        elif type(ind[a]) is bool:
            r += ',\n' + '\t' * numTabs + str(ind[a]).lower()
        elif type(ind[a]) is list:
            r += ',\n' + '\t' * numTabs + '['
            r += listToString(ind[a], numTabs + 1)
            r += '\n' + '\t' * numTabs + ']'
        elif type(ind[a]) is dict:
            r += ',\n' + '\t' * numTabs + '{'
            r += dictToString(ind[a], numTabs + 1)
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


def natus2json(filename, jsonname):
    """
    Main function.
    """
    fex = filename[len(filename)-3:]
    infile = open(filename, 'rb')
    natus = infile.read()
    infile.close()
    jsonfile = open(jsonname, 'w')
    jsonfile.write('{\n\t')
    s = []
    sn1 = natus[17]
    sn2 = natus[19]
    if fex == 'vtc':
        base_schema = -1
        file_schema = -1
    elif sn2 == 1:
        base_schema = 1
        file_schema = sn1
    else:
        base_schema = 0
        file_schema = sn2
    if base_schema == 0 and fex != 'vtc':
        jsonfile.write('"m_file_guid": "')
        for i in range(0, 16):
            jsonfile.write('{:02x}'.format(natus[i]))
            if i in [3, 5, 7, 9]:
                jsonfile.write('-')
        jsonfile.write('",\n\t"m_file_schema": ')
        jsonfile.write(toInt(natus[16:20]))
        jsonfile.write(',\n\t"m_creation_time": "')
        jsonfile.write(datetime.strftime(
            datetime.fromtimestamp(int(toInt(natus[20:24])), tz=timezone.utc),
            '%Y-%m-%dT%H:%M:%SZ'))
        jsonfile.write('",\n\t"m_product_version_high": ')
        jsonfile.write(toInt(natus[24:28]))
        jsonfile.write(',\n\t"m_product_version_low": ')
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
    if base_schema == 1 and fex != 'vtc':
        jsonfile.write('"m_file_guid": "')
        for i in range(0, 16):
            jsonfile.write('{:02x}'.format(natus[i]))
            if i in [3, 5, 7, 9]:
                jsonfile.write('-')
        jsonfile.write('",\n\t"m_file_schema": ')
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
        jsonfile.write(',' + dictToString(t, 1))
    if file_schema == 5 and fex == 'erd':
        jsonfile.write(',\n\t"m_sample_freq": ')
        jsonfile.write(toInt(natus[352:360]))
        jsonfile.write(',\n\t"m_num_channels": ')
        jsonfile.write(toInt(natus[360:364]))
        jsonfile.write(',\n\t"m_deltabits": ')
        jsonfile.write(toInt(natus[364:368]))
        jsonfile.write(',\n\t"m_phys_chan": ')
        s = '['
        for j in range(32):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
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
        jsonfile.write('",\n\t"m_discardbits": ')
        jsonfile.write(toInt(natus[588:592]))
        jsonfile.write(',\n\t"packets": [')  # "packets" not specified in doc
        j = 592
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            r = []
            for i in range(num_channels):
                r.append(int(toInt(natus[j+i:j+i+1])))
            j += num_channels
            for i in range(len(r)):
                if r[i] == -128:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '['
            for i in range(len(r)):
                s += '\n\t\t\t\t' + str(r[i]) + ','
            s = s[:len(s)-1]
            s += '\n\t\t\t]'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 6 and fex == 'erd':
        jsonfile.write(',\n\t"m_sample_freq": ')
        jsonfile.write(toInt(natus[352:360]))
        jsonfile.write(',\n\t"m_num_channels": ')
        jsonfile.write(toInt(natus[360:364]))
        jsonfile.write(',\n\t"m_deltabits": ')
        jsonfile.write(toInt(natus[364:368]))
        jsonfile.write(',\n\t"m_phys_chan": ')
        s = '['
        for j in range(128):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
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
        jsonfile.write(',\n\t"packets": [')  # "packets" not specified in doc
        j = 976
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            r = []
            for i in range(num_channels):
                r.append(int(toInt(natus[j+i:j+i+1])))
            j += num_channels
            for i in range(len(r)):
                if r[i] == -128:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '['
            for i in range(len(r)):
                s += '\n\t\t\t\t' + str(r[i]) + ','
            s = s[:len(s)-1]
            s += '\n\t\t\t]'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 7 and fex == 'erd':
        jsonfile.write(',\n\t"m_sample_freq": ')
        jsonfile.write(toInt(natus[352:360]))
        jsonfile.write(',\n\t"m_num_channels": ')
        jsonfile.write(toInt(natus[360:364]))
        num_channels = int(toInt(natus[360:364]))
        jsonfile.write(',\n\t"m_deltabits": ')
        jsonfile.write(toInt(natus[364:368]))
        jsonfile.write(',\n\t"m_phys_chan": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
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
        jsonfile.write(',\n\t"packets": [')  # "packets" not specified in doc
        j = 4560
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"event_byte": ')
            jsonfile.write(toInt(natus[j:j+1]))
            j += 1
            jsonfile.write(',\n\t\t\t"delta_information": ')
            i = j
            r = []
            for i in range(num_channels):
                r.append(int(toInt(natus[j+i:j+i+1])))
            j += num_channels
            for i in range(len(r)):
                if r[i] == -128:
                    r[i] = int(toInt(natus[j:j+4]))
                    j += 4
            s = '['
            for i in range(len(r)):
                s += '\n\t\t\t\t' + str(r[i]) + ','
            s = s[:len(s)-1]
            s += '\n\t\t\t]'
            jsonfile.write(s)
            jsonfile.write('\n\t\t}')
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 8 and fex == 'erd':
        jsonfile.write(',\n\t"m_sample_freq": ')
        jsonfile.write(toInt(natus[352:360]))
        jsonfile.write(',\n\t"m_num_channels": ')
        jsonfile.write(toInt(natus[360:364]))
        jsonfile.write(',\n\t"m_deltabits": ')
        jsonfile.write(toInt(natus[364:368]))
        jsonfile.write(',\n\t"m_phys_chan": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
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
        jsonfile.write(',\n\t"m_shorted": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + str(bool(natus[4561 + j * 2])).lower() + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_frequency_factor": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[6608 + j * 2:6608 + (j + 1) * 2]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
    if file_schema == 9 and fex == 'erd':
        jsonfile.write(',\n\t"m_sample_freq": ')
        jsonfile.write(toInt(natus[352:360]))
        jsonfile.write(',\n\t"m_num_channels": ')
        jsonfile.write(toInt(natus[360:364]))
        jsonfile.write(',\n\t"m_deltabits": ')
        jsonfile.write(toInt(natus[364:368]))
        jsonfile.write(',\n\t"m_phys_chan": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[368 + j * 4:368 + (j + 1) * 4]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_headbox_type": ')
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
        jsonfile.write(',\n\t"m_shorted": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + str(bool(natus[4561 + j * 2])).lower() + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
        jsonfile.write(',\n\t"m_frequency_factor": ')
        s = '['
        for j in range(1024):
            s += '\n\t\t' + toInt(natus[6608 + j * 2:6608 + (j + 1) * 2]) + ','
        s = s[:len(s)-1]
        s += '\n\t]'
        jsonfile.write(s)
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
            while natus[i] != 0:
                i += 1
            t = sepKeyTree(encode(natus[j+16:i]))
            jsonfile.write(',' + dictToString(t, 3))
            jsonfile.write('\n\t\t}')
            j = i + 1
            if j < len(natus):
                jsonfile.write(',')
        jsonfile.write('\n\t]')
    if file_schema == 2 and fex == 'toc':
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
    if file_schema == 3 and fex == 'toc':
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
    if file_schema == 0 and fex == 'snc':
        jsonfile.write('\n\t"contents": [')  # "contents" not specified in doc
        j = 352
        while j < len(natus):
            jsonfile.write('\n\t\t{\n\t\t\t"sampleStamp": ')
            jsonfile.write(toInt(natus[j:j+4]))
            jsonfile.write(',\n\t\t\t"sampleTime": ')
            jsonfile.write(toInt(natus[j+4:j+12]))
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
            jsonfile.write('\n\t\t{\n\t\t\t"segment_name": ')
            jsonfile.write(encode(natus[j:j+256]))
            jsonfile.write(',\n\t\t\t"start_stamp": ')
            jsonfile.write(toInt(natus[j+256:j+260]))
            jsonfile.write(',\n\t\t\t"end_stamp": ')
            jsonfile.write(toInt(natus[j+260:j+264]))
            jsonfile.write(',\n\t\t\t"sample_num": ')
            jsonfile.write(toInt(natus[j+264:j+268]))
            jsonfile.write(',\n\t\t\t"sample_span": ')
            jsonfile.write(toInt(natus[j+268:j+272]))
            jsonfile.write('\n\t\t}')
            j += 272
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
        for i in range(0, 16):
            jsonfile.write('{:02x}'.format(natus[i]))
            if i in [3, 5, 7, 9]:
                jsonfile.write('-')
        jsonfile.write(',\n\t"Schema": ')
        jsonfile.write(toInt(natus[16:20]))
        file_schema = int(toInt(natus[16:20]))
    if file_schema == 1 and fex == 'vtc':
        jsonfile.write(',\n\t"Contents": [')  # "Contents" not specified in doc
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
        jsonfile.write(',\n\t"Contents": [')  # "Contents" not specified in doc
        j = 20
        while j < len(natus):
            jsonfile.write('\n\t\t{')
            jsonfile.write('\n\t\t\t"MpgFileName": ')
            jsonfile.write(encode(natus[j:j+261]))
            jsonfile.write('",\n\t\t\t"Location": ')
            for i in range(j+261, j+277):
                jsonfile.write('{:02x}'.format(natus[i]))
                if i in [j+264, j+266, j+268, j+270]:
                    jsonfile.write('-')
            jsonfile.write(',\n\t\t\t"StartTime": ')
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


if __name__ == '__main__':
    natus2json(sys.argv[1], sys.argv[2])
