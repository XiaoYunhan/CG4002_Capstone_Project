from skbayes.rvm_ard_models import RVC
from sklearn.metrics import classification_report

import pandas, numpy

def import_data(data_path, DATA_LEN):
    cols = []
    for i in range(DATA_LEN + 1):
        cols.append(i)

    X = pd.read_csv(data_path, sep='\s+', names=cols)
    Y = pd.read_csv(data_path, sep='\s+', names=cols)
    
    print("Data Loaded from File")
    return X, Y

if __name__ == "__main__":
    clf = RVC(kernel='rbf', gamma=0.001)

    X = numpy.random.uniform(-1, 1, (240, 6))
    X = numpy.round(X, 4)
    Y = numpy.random.randint(2, size=(240, 1))

    clf.fit(X, Y)
    y_predict = clf.predict(X)
    
    print(classification_report(Y, y_predict,
                            target_names=[0, 1]))
