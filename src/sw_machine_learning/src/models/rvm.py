from skbayes.rvm_ard_models import RVC
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split 

import pandas as pd
import numpy as np
import os

def import_data(data_path, DATA_LEN=60):
    cols = []
    for i in range(DATA_LEN + 1):
        cols.append(i)

    df = pd.read_csv(data_path, sep='\s+', names=cols)
    X = df.loc[:, :DATA_LEN-1]
    Y = df.loc[:, DATA_LEN:]
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=69)
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    X_test, Y_test = np.array(X_test), np.array(Y_test)
    
    print("Data Loaded from File")
    return X_train, X_test, Y_train, Y_test

if __name__ == "__main__":

    clf = RVC(kernel='rbf', gamma=0.001)

    # X = numpy.random.uniform(-1, 1, (240, 6))
    # X = numpy.round(X, 4)
    # Y = numpy.random.randint(2, size=(240, 1))
    X_train, X_test, Y_train, Y_test = import_data(os.getcwd() + '/../../../../data/Raw Data/positions/compiled_pos.txt')

    clf.fit(X_train, Y_train)
    y_predict = clf.predict(X_test)
    
    print(classification_report(Y_test, y_predict,
                            target_names=[0, 1]))
