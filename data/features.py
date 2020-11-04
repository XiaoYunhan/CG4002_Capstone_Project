import numpy as np
import pandas as pd
import statsmodels.api as sm
import multiprocessing as mp
from math import ceil

WINDOW_SIZE = 10
    

def get_angle(x, y, z):
    u = [x[0], y[0], z[0]]
    v = [x[1], y[1], z[1]]
    uu = u / np.linalg.norm(u)
    vv = v / np.linalg.norm(v)
    dp = np.dot(uu,vv)
    return np.arccos(dp)


def convert_raw(input):
    df = []
    for index, row in input.iterrows():
        acc_X = []
        acc_Y = []
        acc_Z = []
        gyro_X = []
        gyro_Y = []
        gyro_Z = []
        for i in range(WINDOW_SIZE):
            acc_X.append(row[6 * i])
            acc_Y.append(row[6 * i + 1])
            acc_Z.append(row[6 * i + 2])
            gyro_X.append(row[6 * i + 3])
            gyro_Y.append(row[6 * i + 4])
            gyro_Z.append(row[6 * i + 5])
        acc_X = np.array(acc_X)
        acc_Y = np.array(acc_Y)
        acc_Z = np.array(acc_Z)
        gyro_X = np.array(gyro_X)
        gyro_Y = np.array(gyro_Y)
        gyro_Z = np.array(gyro_Z)
        meanAX = np.mean(acc_X)
        meanAY = np.mean(acc_Y)
        meanAZ = np.mean(acc_Z)
        meanGX = np.mean(gyro_X)
        meanGY = np.mean(gyro_Y)
        meanGZ = np.mean(gyro_Z)
        stdAX = np.std(acc_X)
        stdAY = np.std(acc_Y)
        stdAZ = np.std(acc_Z)
        stdGX = np.std(gyro_X)
        stdGY = np.std(gyro_Y)
        stdGZ = np.std(gyro_Z)
        minAX = np.min(acc_X)
        minAY = np.min(acc_Y)
        minAZ = np.min(acc_Z)
        minGX = np.min(gyro_X)
        minGY = np.min(gyro_Y)
        minGZ = np.min(gyro_Z)
        maxAX = np.max(acc_X)
        maxAY = np.max(acc_Y)
        maxAZ = np.max(acc_Z)
        maxGX = np.max(gyro_X)
        maxGY = np.max(gyro_Y)
        maxGZ = np.max(gyro_Z)
        angA12 = get_angle(acc_X[0:2], acc_Y[0:2], acc_Z[0:2])
        angA23 = get_angle(acc_X[1:3], acc_Y[1:3], acc_Z[1:3])
        angA34 = get_angle(acc_X[2:4], acc_Y[2:4], acc_Z[2:4])
        angA45 = get_angle(acc_X[3:5], acc_Y[3:5], acc_Z[3:5])
        angA56 = get_angle(acc_X[4:6], acc_Y[4:6], acc_Z[4:6])
        angG12 = get_angle(gyro_X[0:2], gyro_Y[0:2], gyro_Z[0:2])
        angG23 = get_angle(gyro_X[1:3], gyro_Y[1:3], gyro_Z[1:3])
        angG34 = get_angle(gyro_X[2:4], gyro_Y[2:4], gyro_Z[2:4])
        angG45 = get_angle(gyro_X[3:5], gyro_Y[3:5], gyro_Z[3:5])
        angG56 = get_angle(gyro_X[4:6], gyro_Y[4:6], gyro_Z[4:6])
        ARcoeffAX, sigmaAX = sm.regression.yule_walker(acc_X, order=4, method="mle")
        ARcoeffAY, sigmaAY = sm.regression.yule_walker(acc_Y, order=4, method="mle")
        ARcoeffAZ, sigmaAZ = sm.regression.yule_walker(acc_Z, order=4, method="mle")
        ARcoeffGX, sigmaGX = sm.regression.yule_walker(gyro_X, order=4, method="mle")
        ARcoeffGY, sigmaGY = sm.regression.yule_walker(gyro_Y, order=4, method="mle")
        ARcoeffGZ, sigmaGZ = sm.regression.yule_walker(gyro_Z, order=4, method="mle")

        next_row = {
        "meanAX"    : meanAX,
        "meanAY"    : meanAY,
        "meanAZ "   : meanAZ,
        "meanGX"    : meanGX,
        "meanGY"    : meanGY,
        "meanGZ"    : meanGZ,
        "stdAX"     : stdAX,
        "stdAY"     : stdAY,
        "stdAZ"     : stdAZ,
        "stdGX"     : stdGX,
        "stdGY"     : stdGY,
        "stdGZ"     : stdGZ,
        "minAX"     : minAX,
        "minAY"     : minAY,
        "minAZ"     : minAZ,
        "minGX"     : minGX,
        "minGY"     : minGY,
        "minGZ"     : minGZ,
        "maxAX"     : maxAX,
        "maxAY"     : maxAY,
        "maxAZ"     : maxAZ,
        "maxGX"     : maxGX,
        "maxGY"     : maxGY,
        "maxGZ"     : maxGZ,
        "angA12"     : angA12,
        "angA23"     : angA23,
        "angA34"     : angA34,
        "angA45"     : angA45,
        "angA56"     : angA56,
        "angG12"     : angG12,
        "angG23"     : angG23,
        "angG34"     : angG34,
        "angG45"     : angG45,
        "angG56"     : angG56,
        "ARcoeff1AX" : ARcoeffAX[0],
        "ARcoeff2AX" : ARcoeffAX[1],
        "ARcoeff3AX" : ARcoeffAX[2],
        "ARcoeff4AX" : ARcoeffAX[3],
        "sigmaAX"   : sigmaAX,
        "ARcoeff1AY" : ARcoeffAY[0],
        "ARcoeff2AY" : ARcoeffAY[1],
        "ARcoeff3AY" : ARcoeffAY[2],
        "ARcoeff4AY" : ARcoeffAY[3],
        "sigmaAY"   : sigmaAY,
        "ARcoeff1AZ" : ARcoeffAZ[0],
        "ARcoeff2AZ" : ARcoeffAZ[1],
        "ARcoeff3AZ" : ARcoeffAZ[2],
        "ARcoeff4AZ" : ARcoeffAZ[3],
        "sigmaAZ"   : sigmaAZ,
        "ARcoeff1GX" : ARcoeffGX[0],
        "ARcoeff2GX" : ARcoeffGX[1],
        "ARcoeff3GX" : ARcoeffGX[2],
        "ARcoeff4GX" : ARcoeffGX[3],
        "sigmaGX"   : sigmaGX,
        "ARcoeff1GY" : ARcoeffGY[0],
        "ARcoeff2GY" : ARcoeffGY[1],
        "ARcoeff3GY" : ARcoeffGY[2],
        "ARcoeff4GY" : ARcoeffGY[3],        
        "sigmaGY"   : sigmaGY,
        "ARcoeff1GZ" : ARcoeffGZ[0],
        "ARcoeff2GZ" : ARcoeffGZ[1],
        "ARcoeff3GZ" : ARcoeffGZ[2],
        "ARcoeff4GZ" : ARcoeffGZ[3],
        "sigmaGZ"   : sigmaGZ,
        "Activity"  : row[6 * WINDOW_SIZE]
        }
        df.append(next_row)
        print(mp.current_process(), "{0:.0%}".format((index + 1 - input.index[0])/(input.shape[0])))
    return pd.DataFrame(df).astype({'Activity' : 'int64'})
    

if __name__ == "__main__":
    data = pd.read_csv('Raw Data/moves/compiled.txt', sep="\s+", header=None)
    num_processes = mp.cpu_count()
    chunksize = ceil(data.shape[0] / num_processes)
    chunks = pd.read_csv('Raw Data/moves/compiled.txt', sep="\s+", header=None, chunksize=chunksize)
    pool = mp.Pool(processes=num_processes)
    df = pd.concat(pool.map(convert_raw, chunks))
    pool.close()
    pool.join()
    df.to_csv('Raw Data/moves/features.txt', header=None, index=None, sep=' ', mode='w')