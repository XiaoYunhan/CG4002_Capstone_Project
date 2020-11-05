from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split 
from joblib import dump, load

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
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1, stratify=Y, random_state=69)
    X_train, Y_train = np.array(X_train), np.array(Y_train)
    X_test, Y_test = np.array(X_test), np.array(Y_test)
    print(X_train.shape, Y_train.shape)    
    print("Data Loaded from File")
    return X_train, X_test, Y_train, Y_test

if __name__ == "__main__":

    rbf = SVC(kernel='rbf')

    # X = numpy.random.uniform(-1, 1, (240, 6))
    # X = numpy.round(X, 4)
    # Y = numpy.random.randint(2, size=(240, 1))
    X_train, X_test, Y_train, Y_test = import_data(os.getcwd() + '/../../../../data/Raw Data/moves/compiled.txt')

    rbf.fit(X_train, Y_train.ravel())
    y_predict = rbf.predict(X_test)
    dump(rbf, os.getcwd() + '/../../models/rbf0511.joblib')
    #rbf = load(os.getcwd() + '/../../models/rbf0511.joblib')
    y_predict = rbf.predict(X_test)
    errors = abs(y_predict - Y_test)
    mape = 100 * (errors / Y_test.size)
    # Calculate and display accuracy
    accuracy = 100 - np.mean(mape)
    print('Accuracy:', round(accuracy, 2), '%.')

    
#    print(classification_report(Y_test, y_predict,
#                            target_names=[0, 1]))
