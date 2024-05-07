# Nathan Holmes-King
# 2024-05-01

import mne
import numpy as np
import os
from pyrcn.echo_state_network import ESNClassifier
from reservoirpy.nodes import Reservoir, Ridge
from sklearn.model_selection import train_test_split
import sys
import time

"""
WORK IN PROGRESS.

Command-line arguments:
1. Directory
2. Python module (PyRCN, reservoirpy)

PEP-8 compliant.
"""


std_ch = ['EEG F3-M2', 'EEG F4-M1', 'EEG T3-M2', 'EEG T4-M1']
valid_mod = ['pyrcn', 'reservoirpy']


def main(indir, mod):
    t = time.time()
    if mod not in valid_mod:
        print('ERROR! Invalid module name.')
        return
    X = []
    y = []
    max_len = 0
    for f in os.listdir(indir):
        # Read data
        try:
            raw = mne.io.read_raw_edf(indir + '/' + f, preload=True,
                                      verbose='ERROR')
        except TypeError:
            continue
        except NotImplementedError:
            continue
        except ValueError:
            continue
        print('Read file', f, '|', time.time() - t, 's')
        nch = len(raw.ch_names)
        data, times = raw.get_data(return_times=True)
        # Filter out non-EEG channels
        Xtemp = []
        for a in std_ch:
            g = True
            for i in range(nch):
                if raw.ch_names[i] == a:
                    Xtemp.append(np.array(data[i]))
                    g = False
                    break
            if g:
                Xtemp.append(np.zeros(raw.n_times))
        X.append(np.array(Xtemp))
        # Spikes or not?
        if int(f.split('.')[0][4:]) > 40:
            y.append(np.array([0]))
        else:
            y.append(np.array([1]))
        # Update max_len
        if raw.n_times > max_len:
            max_len = raw.n_times
    # Final pre-processing
    print('Final pre-processing |', time.time() - t, 's')
    for i in range(len(X)):
        if X[i].shape[1] < max_len:
            X[i] = np.append(X[i], np.zeros((X[i].shape[0],
                                             max_len-X[i].shape[1])), axis=1)
    if mod == 'pyrcn':
        newX = np.empty(shape=(len(X),), dtype=object)
        newY = np.empty(shape=(len(y),), dtype=object)
        for i in range(len(X)):
            newX[i] = X[i]
            newY[i] = y[i]
        X = newX
        y = newY
    elif mod == 'reservoirpy':
        X = np.array(X)
        y = np.array(y)
    # Train model
    print('Train model |', time.time() - t, 's')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
    print(X_train.shape, y_train.shape)
    if mod == 'pyrcn':
        clf = ESNClassifier()
        clf.fit(X=X_train, y=y_train)
        y_pred = clf.predict(X=X_test)
        print(y_test, y_pred)  # TEMP
    elif mod == 'reservoirpy':
        reservoir = Reservoir(units=100, lr=0.3, sr=1.25)
        readout = Ridge(output_dim=1, ridge=1e-5)
        esn = reservoir >> readout
        esn.fit(X_train, y_train)
        y_pred = esn.run(X_test)
        print(y_test, y_pred)  # TEMP


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2].lower())
