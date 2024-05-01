# Nathan Holmes-King
# 2024-05-01

import mne
import numpy as np
import os
from pyrcn.echo_state_network import ESNClassifier
from sklearn.model_selection import train_test_split
import sys

"""
WORK IN PROGRESS.

Command-line arguments:
1. Directory

PEP-8 compliant.
"""


def main(indir):
    X = []
    y = []
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
        nch = len(raw.ch_names)
        data, times = raw.get_data(return_times=True)
        # Filter out non-EEG channels
        Xtemp = []
        print(f)  # DEBUG
        for i in range(nch):
            if len(raw.ch_names[i]) > 2 and raw.ch_names[i][:3] == 'EEG':
                Xtemp.append(data[i])
                print(raw.ch_names[i])  # DEBUG
        X.append(np.array(Xtemp))
        # Spikes or not?
        if int(f.split('.')[0][4:]) > 40:
            y.append(np.array([False]))
        else:
            y.append(np.array([True]))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
    clf = ESNClassifier()
    clf.fit(X=X_train, y=y_train)
    y_pred_classes = clf.predict(X=X_test)
    y_pred_proba = clf.predict_proba(X=X_test)
    print(y_pred_classes.shape)  # TEMP


if __name__ == '__main__':
    main(sys.argv[1])
