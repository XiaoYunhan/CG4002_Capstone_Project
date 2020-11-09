import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.preprocessing import MinMaxScaler

input = pd.read_csv('Raw Data/moves/features.txt', header=None, delimiter=r"\s+")

X = input.iloc[:, :-1]
Y = input.iloc[:, -1]
X = np.array(X, dtype="float64")
scaler = MinMaxScaler(feature_range=(0,255))
X = scaler.fit_transform(X)
dump(scaler, os.getcwd() + '/../src/sw_machine_learning/models/feat_scaler.joblib')
exit()
#X = X.astype(np.uint8)
X = pd.DataFrame(X)
output = pd.concat([X,Y], axis=1)
print(output.head)
output.to_csv('Raw Data/moves/compiled_int.txt', header=None, index=None, sep=' ', mode='w')
