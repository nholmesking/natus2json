# -----------------------------------------
#   Project: EEG Tensor Analysis Project
#
#   File: eeg_tensor.py
#
#   author: Willam Bosl (primary), Nathan Holmes-King
#
#   Software provided under the MIT license: MIT.license.txt
#
# -----------------------------------------

# Standard or public libraries
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import tensorly as tl
from scipy import stats
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
import seaborn as sns
from sklearn.metrics import brier_score_loss
from sklearn import metrics
#import matlab.engine
import SupParafacEM as pySupCP
import pickle

# Global parameters
version = "python"  # python matlab
plotfilename = "plt_file.png"
data_text = ""
target = "sleep"
SLEEPSTAGE = 2


# -----------------------------------------
# This function parses command line arguments.
#
# Input argument(s): sys.argv
# Return:
# -----------------------------------------
def parse_commandline(argv):
    global plotfilename, version, target, SLEEPSTAGE
    argc = len(argv)
    usage_and_exit = False

    # Essential arguments are set to NULL so that we can check if they're set
    infile = None
    clinical_filename = None
    rank = 20

    # Usage instructions (for command line)
    if argc < 4:
        usage_and_exit = True
        infile = "Data/bects_sleep_mod.csv"
        clinical_filename = "Data/bects_demographics.csv"

    else:
        for i in range(1, argc, 2):
            indicator = argv[i]
            argument = argv[i + 1]
            if indicator == "-i":
                infile = argument
            elif indicator == "-c":
                clinical_filename = argument
            elif indicator == "-r":
                rank = int(argument)
            elif indicator == "-s":
                target = argument
            elif indicator == "-v":
                version = argument
            elif indicator == "-sleep":
               SLEEPSTAGE = int(argument)
            elif indicator == "-m":
                version = argument # Should be either 'matlab' or 'python'
                if version == "matlab" or version == "python":
                    continue
                else:
                    print("-m argument must be either matlab or python. Exiting.")
                    exit()

    if (infile is None):
        usage_and_exit = True
    if (clinical_filename is None):
        usage_and_exit = True

    if usage_and_exit:
        print("Usage: python test_supCP.py -i infile -c clinical_filename")
        sys.exit()

    return infile, clinical_filename, rank


#------------------------------------------
# Compute AUC
#------------------------------------------
def get_auc(y, score, labels):

    lab1 = labels[1]
    auc = metrics.roc_auc_score(y, score) #, labels=labels)
    fpr, tpr, thresholds = metrics.roc_curve(y, score, pos_label=lab1)
    #pr_pairs = metrics.precision_recall_curve(y, score, pos_label=lab1) # 
    avg_prec = metrics.average_precision_score(y, score, pos_label=lab1) # avg precision recall
    #auc = metrics.auc(fpr, tpr)
    sens_array = tpr # 1.0 - fnr
    spec_array = 1.0 - fpr

    ss = (sens_array+spec_array).tolist()
    max_value = max(ss)
    i = ss.index(max_value)
    sens = sens_array[i]
    spec = spec_array[i]

    return auc, sens, spec, avg_prec
    

# -----------------------------------------
# Impute missing or nan data using group averages
# -----------------------------------------
def impute_missing(df):
    # df.loc[df['Value'].isnull(), 'value_is_NaN'] = 'Yes'
    # df.loc[df['Value'].notnull(), 'value_is_NaN'] = 'No'
    headers = df.columns

    # Get the rows with a NaN
    # df_not_na = df[df['value_is_NaN']=='No']
    mean_value = df['Value'].mean()
    df['Value'].fillna(value=mean_value, inplace=True)
    return df

    # df_nan = df.isna()
    print("Start")
    df_nan = df.isnull()
    print("len of nans: %d of %d" % (len(df_nan), len(df)))

    # Loop over the rows with bad data
    if 'Sleep' in headers:
        for index, row in df_nan.iterrows():
            g = row['Label']
            s = row['Sleep']
            f = row['Feature']
            c = row['Channel']
            new_value = np.mean(
                df[(df['Label'] == g) & (df['Sleep'] == s) & (df['Feature'] == f) & (df['Channel'] == c)].Value)
            df.loc[index, 'Value'] = new_value
    else:
        for index, row in df_nan.iterrows():
            g = row['Label']
            f = row['Feature']
            c = row['Channel']
            new_value = np.mean(df[(df['Label'] == g) & (df['Feature'] == f) & (df['Channel'] == c)].Value)
            df.loc[index, 'Value'] = new_value
    return df


# -----------------------------------------
# Normalize data
# -----------------------------------------
def normalize(df):
    # Normalize by measure
    features = df.Feature.unique()

    for f in features:
        df_f = df[df['Feature'] == f]
        mx = np.max(df_f['Value'])
        mn = np.min(df_f['Value'])
        absmx = max(mx, mn)
        df.loc[df['Feature'] == f, 'Value'] = df_f['Value'] / absmx

    return df


# -----------------------------------------
#
# Read a long format .csv file and pull into
# a tensor structure
#
# Input: infilename
# Return: dataframe with all data for analysis
# -----------------------------------------
def read_file(infilename, df_clinical):
    global sup_title, plotfilename, RANK

    # Let's make sure white space at the end of NaN's won't confuse the reader
    additional_nans = ['NaN ', 'nan ', 'na ', 'inf', 'inf ']

    # Assume that indir is the full pathname for the directory where data lies.
    # Inside indir there will be one or more zip files whose name is the ID.
    df = pd.read_csv(infilename, skipinitialspace=True, na_values=additional_nans)
    df = normalize(df)

    # Add the clinical data
    headers = list(df.columns.values)
    if "Visit_year" in headers:
        df2 = pd.merge(df, df_clinical, on=['ID', 'Visit_year'])
    else:
        df2 = pd.merge(df, df_clinical, on=['ID'])
    df = df2  
    
    print ("Fraction good channels: ", df.Value.count() / len(df.Value))
    df = impute_missing(df)
    good_channels = df.Value.count() / len(df.Value)
    print ("Fraction after imputation: ", good_channels)
    if good_channels < 1.0:
        df.dropna(inplace=True)  # Dropping all the rows with nan values
    if len(df.Value) == 0.0:
        good_channels = 0.0
        print ("Fraction after dropping bad channels: ", good_channels)
        exit()

    return df

# -----------------------------------------
# Process the data
# -----------------------------------------
def extract_data(df):
    global sup_title, plotfilename, RANK, target

    # Create the labels column

    if 'Age' in df.columns:
        df['Age_Axis'] = df['Age']
        df.loc[([1 == 1 for x in df.Age_Axis]), 'Age_Axis'] = 0
        ages = df.Age_Axis.unique()

    sup_title = "Test pySupCP"
    
    # Let's use a reduced montage
    #channel_set = ['Fp1','Fp2','T7','T8']
    #channel_set = ['O1','O2','P7','P8']
    channel_set = ['T7','C3','Cz','C4','T8','Fz','Pz','P3','P4']
    df = df[[x in channel_set for x in df.Channel]]  # Controls only


    # Get Sleep stage data or BECTS
    if target == "sleep":
        df = df[[((x == 0) or (x == 2)) for x in df.Sleep]]  # Sleep stage 0 or 2
#        df = df[[x.startswith('C') for x in df.ID]]  # Controls only
        df = df[ (df["Age"] > 2) & (df["Age"] < 19)] # limit the age range
        df = df[[(not x.startswith('s_')) for x in df.Feature]] # no sync features
        #df = df[[( x.startswith('s_')) for x in df.Feature]] # only sync features
        list_of_labels = df.Sleep.tolist()
        df['Label'] = list_of_labels
        print("Labels: ", df.Label.unique())
        
        print("IDs in df = ", len(df.ID.unique()))
        print("IDs in df_clinical = ", len(df_clinical.ID.unique()))
        
        df_clinical['DX'] = df_clinical['DX'].astype('int')
        
        #df['DX'] = df_clinical['DX'].copy

        #df.loc[([x.startswith('C') for x in df_clinical.ID]), 'DX'] = 0
        #df.loc[([x.startswith('B') for x in df_clinical.ID]), 'DX'] = 1

    elif target == "bects":
        df = df[df["Sleep"] == SLEEPSTAGE]  # awake (0) or sleep stage 2 or 3
#        df = df[ (df["Age"] > 4.9) & (df["Age"] < 13.1)]
        df = df[[(not x.startswith('s_')) for x in df.Feature]]
        list_of_labels = df.ID.tolist().copy()
        
        df = df.assign(Label=list_of_labels)
        df.loc[([x.startswith('C') for x in df.ID]), 'Label'] = 0
        df.loc[([x.startswith('B') for x in df.ID]), 'Label'] = 1
        df['DX'] = df_clinical['ID'].copy
        df.loc[([x.startswith('C') for x in df_clinical.ID]), 'DX'] = 0
        df.loc[([x.startswith('B') for x in df_clinical.ID]), 'DX'] = 1



    # Read the data into structures appropriate for tensorization
    # Axes: Feature (nonlinear measure), Channel, Freq
    axes = {}
    IDs = df.ID.unique()
    features = df.Feature.unique()
    channels = df.Channel.unique()
    stages = df.Label.unique()
    ages = df.Age_Axis.unique()

    axes['ID'] = IDs
    axes['Label'] = stages
    axes['Feature'] = features
    axes['Channel'] = channels
    axes['Freq'] = []  # to be filled below with new frequencies, x_new
    axes['Age'] = ages

    # Create multiscale curves and interpolate to a standard set of frequencies
    # Use the minimum sampling rate to determine the range of new frequencies
    # delta: 0-4, theta: 4-7, alpha: 7-13, beta: 13-30, gamma: 30-60, gamma+: 60 and above
    # Only use details, wavelets that start with D
    details = ['D1', 'D2', 'D3', 'D4', 'D5']
    df = df[df["Wavelet"].isin(details)]
    x_new = np.array([64., 32., 16., 8., 4.])
#    x_new = np.array([32., 16., 8., 4., 2.])
    # x_new = np.array([1.6, 3.1, 6.2, 12.5, 25., 50., 100.])
    axes['Freq'] = x_new

    # Create the numpy array that will hold the new tensor structures
    # data_np((ID,Feature,Channel,Freq))
    # n1 = len(IDs)
    # n2 = len(stages)
    n3 = len(features)
    n4 = len(channels)
    n5 = len(x_new)
    data_np2 = []

    id_stage = []
    index = 0
    for i1, id in enumerate(IDs):
        df_id = df[(df["ID"] == id)]
        labels = df_id.Label.unique()
        #labels = df_id.Visit_year.unique()

        for i2, label in enumerate(labels):
            index += 1
            values = np.full((n3, n4, n5), np.nan)
            id_stage.append([id, label])
            df_id_s = df_id[(df_id["Label"] == label)]

            # Get the sampling rate, then compute wavelet frequencies
            # srate = df_id_s.Rate.unique()[0] # Get the sampling rate for this patient

            x = x_new

            for i3, feature in enumerate(features):
                df_id_feature = df_id_s[df_id_s["Feature"] == feature]

                for i4, ch in enumerate(channels):
                    df_id_feature_ch = df_id_feature[df_id_feature['Channel'] == ch]

                    y = np.array(df_id_feature_ch["Value"])
                    func = interp1d(x, y, "linear")
                    y_new = func(x_new)
                    values[i3, i4, 0:] = y_new[0:]

            data_np2.append(values)

    return axes, np.array(data_np2), id_stage, channels


# -----------------------------------------
# Create a tensor object
# -----------------------------------------
def create_tensor(axes, data_np, id_stage, df, channels, r, rank_acc):
    global sup_title, data_text, plotfilename, RANK, SLEEPSTAGE
    rank = r
    threshold = 0.4
    
    # Let's ignore age and put all the data together, then
    # see if we can separate out groups by age.
    # data_np['ID_age'] = data_np[['ID','Age']].astype(str).apply(''.join,1)
    print("--->>>  shape of EEG data = ", data_np.shape)
    
    # Create a tensor object and scale
    X = tl.tensor(data_np)

    # tolerance
    tol = 1.0e-3
    #        print("%8.3f  %8.3f" %(rank, err_ls) )

    # Some initializations
    nID = len(X)  # number of subjects
    label_list = []
    for i in range(nID):
        label_list.append(id_stage[i][1])
    unique_labels = list(set(label_list))
    num_labels = []
    for i, lab in enumerate(unique_labels):
        num_labels.append(i)
        
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    pr = {}
    for lab in unique_labels:
        pr[lab] = []

    lab0 = unique_labels[0]
    lab1 = unique_labels[1]
    y_truth = []
    y_score = []
    y_prob = []

    Y = []
    Y_para = []
    ages = {}
    age_list = []
    dx_list = {}
    Meds = {}
    headers = list(df.columns.values)
    
    for i in range(nID):
        label = id_stage[i][1]
        id = id_stage[i][0]
        sub_df = df.loc[df['ID'] == id]
        dx = sub_df.iloc[0]['DX']
        dx_list[id] = dx
        age = float(sub_df.iloc[0]['Age'])
        ages[id] = age
        age_list.append(age)

        meds = 'u'
        if "Meds" in headers:
            meds = sub_df.iloc[0]['Meds']
        Meds[id] = meds

        if "Sex" in headers:
            sex = sub_df.iloc[0]['Sex']
        if "Gender" in headers:
            sex = sub_df.iloc[0]['Gender']
      
        Y.append([label,sex,age])  # Labels for SupParafac
        covariate_list = ["dx_sex_age"]

    Y = np.array(Y)
    labels = np.zeros(len(Y))  # make a copy
    labels[0:] = Y[0:, 0]
    
    lab_total = {}
    lab_acc = {}
    lab_total_B = {}
    lab_acc_B = {}
    for lab in labels:
        lab_total[lab] = 0
        lab_acc[lab] = {}
        lab_total_B[lab] = 0
        lab_acc_B[lab] = {}
        for lab2 in labels:
            lab_acc[lab][lab2] = 0
            lab_acc_B[lab][lab2] = 0


    # For testing, shuffle the labels
    # We only want to randomize the first column, the outcome labels
    #np.random.shuffle(labels)
    #Y[0:, 0] = labels[0:]

    # Y_para is the same as Y, but with different structure
    for i in range(len(Y)):
        Y_para.append(Y[i][0])
    Y_para = np.array(Y_para)

    kwargs = {'AnnealIters': 100, 'ParafacStart': 0, 'max_niter': 5000, 'convg_thres': tol, 'Sf_diag': 1}


    #-----------------------------------------------
    # Cross validation loop
    #-----------------------------------------------
    #eng = matlab.engine.start_matlab()
    kfolds = 5
    # Create the stratified splits
    skf = StratifiedKFold(kfolds)
    for train_index, test_index in skf.split(X, Y_para):
        X_train = X[train_index]
        Y_train = Y[train_index]
        
        # ---------  Training step --------- #
    
        # Matlab version
        if version == "matlab":
            print("Call matlab SupCP")
#            Ymat = matlab.double(Y_train.tolist())
#            Xmat = matlab.double(X_train.tolist())
#            result = eng.SupParafacEM(Ymat, Xmat, rank, nargout=6)
        else:
            # Python version
            result = pySupCP.SupParafacEM(Y_train, X_train, rank, kwargs)
    
        (B, V, U, se2, Sf, rec) = result
        B = np.array(B)
        Sf = np.array(Sf)
        rec = np.array(rec)
        U = np.array(U)
        for i in range(len(V)):
            V[i] = np.array(V[i])
        result = (B, V, U, se2, Sf, rec)
        factors = [U] + V    
        
        # ---------  Test step --------- #
        for i in test_index:
            id = id_stage[i][0]    
            Xi = X[i]
            Yi = Y[i]
            truth = labels[i]
            prob = pySupCP.predict(result, Xi, Yi, unique_labels)

            y_truth.append(truth)
            y_score.append(prob)
            if prob < 0.5:
                yp = lab0
            else:
                yp = lab1
            y_prob.append(yp)
            lab_max_prob = yp
            
            if yp != truth:
                age = ages[id]
                dx = dx_list[id]
                print("--> id, age, dx, truth, prob: ", id, age, dx, truth, prob)
       
            lab_total[truth] += 1
            for lab in unique_labels:
                lab_acc[truth][lab_max_prob] += 1
        
            pr[truth].append(prob)
            if len(unique_labels) == 2:
    
                if prob > threshold and truth == lab1:
                    TP += 1
                elif prob > threshold and truth == lab0:
                    FP += 1
#                    print("FP, probability of %s (age=%5.2f), %7.4f, truth: %d, meds=%s: " %(id, ages[id], prob, truth, Meds[id]))
                elif prob < threshold and truth == lab0:
                    TN += 1
                elif prob < threshold and truth == lab1:
                    FN += 1
#                    print("FN, probability of %s (age=%d):  %7.4f, truth: %d, meds=%s: " %(id, ages[id], prob, truth, Meds[id]))
    #-----------------------------------------------
    #   End of cross validation loop
    
    
    #-----------------------------------------------
    # Compute factors using the entire dataset, for plotting
    if version == "matlab":
        print("Call matlab SupCP")
#        Ymat = matlab.double(Y.tolist())
#        Xmat = matlab.double(X.tolist())
#        result = eng.SupParafacEM(Ymat, Xmat, rank, nargout=6)
    else:
        # Python version
        result = pySupCP.SupParafacEM(Y, X, rank, kwargs)

    (B, V, U, se2, Sf, rec) = result
    B = np.array(B)
    Sf = np.array(Sf)
    rec = np.array(rec)
    U = np.array(U)
    for i in range(len(V)):
        V[i] = np.array(V[i])
    result = (B, V, U, se2, Sf, rec)
    factors = [U] + V     
    
    # Rank the factors
    # Let's rank the factors based on simple p-values for the factor weights
    pv = np.zeros(rank)
    n = len(U)
    for r in range(rank):
        a = []
        s = []
        for i in range(n):
            v = U[i, r]
            if labels[i] == unique_labels[0]:
                a.append(v)
            else:
                s.append(v)
        a = np.array(a)
        s = np.array(s)
        t, p = stats.ttest_ind(a, s)
        pv[r] = p
    rank_indices = np.argsort(pv)
    


    # Set the threshold
    t, p = stats.ttest_ind(pr[lab0], pr[lab1])
    m0 = np.mean(pr[lab0])
    m1 = np.mean(pr[lab1])
    threshold = (m1+m0)/2.0
    print("Resetting threshold to ", threshold,"; m0, m1 = ", m0,m1)

    group_values = " "
    if 1==0:
        # Normalize totals
        print("\n")
        n_labels = len(unique_labels)
        for lab in unique_labels:
            sys.stdout.write("Label=%4s (n=%4d), predictions: " % (lab, (list(labels)).count(lab)))
            for lab2 in unique_labels:
                if lab_total[lab] > 0: lab_acc[lab][lab2] /= (n_labels * lab_total[lab])
                a = lab_acc[lab]
                sys.stdout.write("%5.2f, " % (a[lab2]))
            sys.stdout.write("\n")
        sys.stdout.write("\n")

        total = TP + TN + FP + FN
        acc = (TP + TN) / total
        sens = 0
        spec = 0
        prec = 0
        F1 = 0
        if (TP + FN > 0): sens = TP / (TP + FN)
        if (TN + FP > 0): spec = TN / (TN + FP)
        if (TP + FP > 0): prec = TP / (TP + FP)
        if (sens + prec > 0): F1 = 2 * (sens * prec) / (sens + prec)
        lab0 = unique_labels[0]
        lab1 = unique_labels[1]

    # Compute Brier score (forecast quality)
    brier = brier_score_loss(y_truth, y_score, pos_label=lab1)

    auc, sens, spec, avg_prec = get_auc(y_truth, y_score, labels)
    acc = (sens+spec)/2.0
    F1 = 1.0
    data_text = ("acc, sens, spec, AUC, Brier, Avg_prec = %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f " % (acc, sens, spec, auc, brier, avg_prec))
    print(data_text)

    # Let's look at group differences
    t, p = stats.ttest_ind(pr[lab0], pr[lab1])
    (R, p2) = stats.pearsonr(y_truth,y_score)
    total_pval = p2
    total_R = R
    print("total_pval, total_R: ", total_pval, total_R)
    save_p_value = p
    m0 = np.mean(pr[lab0])
    m1 = np.mean(pr[lab1])
    s0 = np.std(pr[lab0])
    s1 = np.std(pr[lab1])
    print("Group values: m (std): %5.2f (%5.2f), %5.2f (%5.2f);  p = %6.3e" % (m0, s0, m1, s1, p))
    group_values = ("\nGroup values: m (std): %5.2f (%5.2f), %5.2f (%5.2f);  p = %6.3e" % (m0, s0, m1, s1, p))

    rank_acc.append([rank, acc, sens, spec, F1, brier, p])

    data_text = data_text + group_values
    # data_text = data_text + "\n" + age_axis + ";  " + "labels: " + unique_labels

    # print("weights: ", weights)
    print("Len of factors: ", len(factors))
    print("Factor vectors:")
    for f in factors:
        print(f.shape)

    n = len(factors[0])

    unique_labels = list(set(labels))
    index0 = [i for i, d in enumerate(labels) if d == unique_labels[0]]
    index1 = [i for i, d in enumerate(labels) if d == unique_labels[1]]

    print("unique_labels: ", unique_labels)
    print("index0: ", len(index0))
    print("index1: ", len(index1))
    print("labels: ", len(labels))

    unique_labels = list(set(labels))
    label_index = []
    for ilab, lab in enumerate(unique_labels):
        label_index.append([i for i, d in enumerate(labels) if d == unique_labels[ilab]])

    pv = np.arange(rank)

    # Create feature vectors and labels for each instance
    df.set_index('ID')
    X = []
    for i in range(n):
        id = id_stage[i][0]
        sub_df = df.loc[df['ID'] == id]
        row = U[i]
        X.append(row)
    X = np.array(X)

    # Let's try k-fold cross-validation
    #cv.classify(X, Y_para)

    sig_factors = []
    PVAL = True

    for r in range(rank):
        if PVAL:
            a = []
            s = []
            for i in range(n):
                v = U[i, r]

                if labels[i] == unique_labels[0]:
                    a.append(v)
                else:
                    s.append(v)

            a = np.array(a)
            s = np.array(s)

            t, p = stats.ttest_ind(a, s)
            pv[r] = p
            if p < 0.001: sig_factors.append(r)
    #-------------------------------------------
    # Write to Pickle
    #-------------------------------------------
    with open('output.pkl', 'wb') as f:
        pickle.dump(V, f)
        pickle.dump(rank_indices, f)
        pickle.dump(rank, f)
        pickle.dump(U, f)
        pickle.dump(age_list, f)
        pickle.dump(Y_para, f)
        pickle.dump(total_R, f)
    #-------------------------------------------
    # Plotting
    #-------------------------------------------
    nranks = 4
    nrows = nranks + 2
    ncols = len(V) + 2
    iplot = 1 + ncols
    fig = plt.figure(figsize=(12, 8))
    
    print ("rank_indices: ", rank_indices)

    # Seaborn colors
    colors = sns.color_palette()

    print("for plotting, shape of V: ", V[0].shape, V[1].shape, V[2].shape)

    # Get average value of V weights and place in V[:][:,0]
    k = rank_indices[rank-1]
    for i in range(len(V)):
        for j in range(len(V[i])):
            V[i][j,k] = np.mean(V[i][j, 0:])
    all_indices = np.zeros(rank, dtype=int)
    all_indices[0] = k
    for i in range(1,rank):
        all_indices[i] = rank_indices[i-1]
    

    # Let the x-axis be the age of the subject
    #id_stage.append([id, label])
    xx = age_list

    #for r in range(rank):
    for count, r in enumerate(all_indices[0:nranks+1]):

        # Box 0: text information
        ax = fig.add_subplot(nrows, ncols, iplot)
        # sns.lineplot('Day', 'x', data=df)

        # Compute the correlation value for the latent factor derived from U[i]
        print("r, shape of U: ", r, U.shape)
        (R, p) = stats.pearsonr(U[0:,r], Y_para)
        pval = ("\nR = %4.2f \np=%5.2e" % (abs(R), p))
        mytext = "\nFactor " + str(r + 1) + pval
        
        if count == 0:
            pval = ("\nR = %4.2f \np=%5.2e" % (abs(total_R), total_pval))
            mytext = "\nFactor " + str("All") + pval


        #pval = ("\np = %5.2e" % (pv[r]))

        #ax.set_title(mytext)
        ax.text(0.3, 0.5, mytext, fontsize=8)
        ax.axis('off')
        fig.tight_layout()
        iplot += 1

        # factor 1: features
        y = V[0][:, r]
        x = range(len(y))
        ax = fig.add_subplot(nrows, ncols, iplot)
        ax.bar(x, y, color=colors[0])
        # Add some text for labels, title and custom x-axis tick labels, etc.
        if r == 0:
            ax.set_title('Nonlinear Features', fontsize=12)
        xlabels = axes['Feature']
        # ax.set_ylabel(ytext, rotation=0, fontsize=10, labelpad=40)
        ax.yaxis.set_visible(False)
        iplot += 1

        # factor 2: channels
        y = V[1][:, r]
        x = range(len(y))
        ax = fig.add_subplot(nrows, ncols, iplot)
        ax.bar(x, y, color=colors[1])
        if r == 0: ax.set_title('Channels', fontsize=12)
        xlabels = axes['Channel']
        ax.yaxis.set_visible(False)
        iplot += 1

        # factor 3: frequency
        ax = fig.add_subplot(nrows, ncols, iplot)
        y = V[2][:, r]
        # x = freqs
        x = range(len(y))
        # ax.semilogx(basex=10)
        xlabels = ['d-', 'd+', 'th', 'al', 'be', 'g', 'g+']
        xlabels = ['d', 'th', 'al', 'be', 'g', 'g+']
        x = xlabels[0:len(y)]
        ax.bar(x, y, color=colors[2])  # , width=[1, 2, 3, 4, 5, 6, 7])
        if r == 0: ax.set_title('Freq', fontsize=12)
        #        ax.set_xticklabels(xlabels)
        ax.yaxis.set_visible(False)
        iplot += 1

        # Dot plots showing all groups
        y = U[:, r]
        x = range(len(y))
        x = xx
        
        ax = fig.add_subplot(nrows, ncols, iplot)
        ax.yaxis.set_visible(False)

#        m = 0
        # Dot plot
        if count == 0:
            for k in range(len(unique_labels)):
                xp = [x[i] for i in label_index[k]]
                yp = [y_score[i] for i in label_index[k]]
                ax.plot(xp, yp, '.', label=unique_labels[k])

        else:
            for k in range(len(unique_labels)):
                xp = [x[i] for i in label_index[k]]
                yp = [y[i] for i in label_index[k]]
                ax.plot(xp, yp, '.', label=unique_labels[k])
#            m = m + np.mean(yp)
#
#        m = m / 2.0
#        ax.axhline(y=m, linestyle='-', color='k')
        ax.legend(bbox_to_anchor=(1.05, 1), fontsize=10)  # Add the legend at the end

        # Line plot for regression, with confidence interval
        if 1==0:
            #sns.regplot(x=Y_para, y=U[0:, r], ax=ax, scatter_kws={'s':10, 'facecolor':colors[1]})
            sns.regplot(x=Y_para, y=U[0:, r], ax=ax, x_estimator=np.mean)

        iplot += 1


    print("Features: ", axes['Feature'])
    print("Channels: ", axes['Channel'])

    sup_title = data_text + "\n" + sup_title
    #summary = [m0, s0, m1, s1, save_p_value]
    plt.suptitle(sup_title, fontsize=10)
    
    if SLEEPSTAGE == 0:
        ss = "awake"
    elif SLEEPSTAGE == 2:
        ss = "N2"
    elif SLEEPSTAGE == 3:
        ss = "N3"

    #plotfilename = ("bects_%s_age_3to14_%s_%2d.png" %(ss,covariate_list,rank))
    plotfilename = ("bects_O1O2P7P8_%s_age_3to14_%s_%2d.png" %(ss,covariate_list,rank))
    print("Writing plot to file: ", plotfilename)
    plt.savefig(plotfilename)
    
    print("Covariate list: ", covariate_list)
    return auc, m0,s0,m1,s1,save_p_value, brier


# -----------------------------------------
#
# -----------------------------------------
if __name__ == "__main__":

    # Get command line input, if any
    infilename, clinical_filename, rank = parse_commandline(sys.argv)

    # Read the relevant Clinical/Demographic data
    df_clinical = pd.read_csv(clinical_filename, skipinitialspace=True)

    # Read and process the EEG data
    rank_acc = []
    # Append the associated clinical data
    df = read_file(infilename, df_clinical)

    # For testing all ages and all ranks, separately
    result_list = []
    axes, data_np, id_stage, channels = extract_data(df)

    # Process the tensor
    auc, m0,s0,m1,s1,pval,brier = create_tensor(axes, data_np, id_stage, df, channels, rank, rank_acc)                
    print("\nResults:")
    print("%5.2f; %5.2f (%5.2f) %5.2f (%5.2f) %5.2e %5.2f" %(auc, m0,s0,m1,s1,pval,brier))

 
    print("All done.")
