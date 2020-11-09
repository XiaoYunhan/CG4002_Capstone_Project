import numpy as np
import statsmodels.api as sm
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
    frame = []
    for i in range(6):
        frame.append(np.mean(input[i]))
    for i in range(6):
        frame.append(np.std(input[i]))
    for i in range(6):
        frame.append(np.min(input[i]))
    for i in range(6):
        frame.append(np.max(input[i]))
    for i in range(9):
        frame.append(get_angle(input[0][i:i+2], input[1][i:i+2], input[2][i:i+2]))
    for i in range(9):
        frame.append(get_angle(input[3][i:i+2], input[4][i:i+2], input[5][i:i+2]))
    for i in range(6):
        ARcoeff, sigma = sm.regression.yule_walker(input[i], order=4, method="mle")
        for j in ARcoeff:
            frame.append(j)
        frame.append(sigma)

    return frame