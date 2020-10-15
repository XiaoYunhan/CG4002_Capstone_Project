import torch
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
import torch.nn as nn
from src.mlp import *

def load_model(PATH):
    model = ffnn()
    model.load_state_dict(torch.load(PATH + "ffnn.pt"))
    return model


def eval_model(model, frame):
        Y_test_pred = model(frame)
        Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
        _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
        return Y_pred_tags.cpu().numpy()

if __name__ == "__main__":

    model = load_model(os.getcwd() + "/models/")
    model.eval()
    frame = [[
    60.6947, 235.2977, 237.9237, 1.9999, -0.7329, 0.4500,
    70.4962, 250.1298, 250.1298, 1.2341, -0.2485, -0.0332,
    207.3969, 239.5802, 10.0305, -0.5767, 0.0693, -0.6931,
    144.9466, 46.0382, -163.2595, -1.7654, 1.6404, -0.9280,
    21.7328, 36.6870, -34.1145, 1.9999, -2.0000, 1.9999,
    -92.5802, 76.4886, 127.6489, -2.0000, 0.7646, -0.1921,
    -38.1985, -250.1374, -250.1374, 1.5981, -0.4275, 0.5403,
    20.7405, 83.8015, 169.3435, -0.0171, 0.1560, 0.0586,
    2.5802, -250.1374, 59.1756, -0.2974, 0.1436, 0.4463,
    38.4427, -250.1374, 81.0382, 0.3513, -0.1440, 1.0947]]
    scaler = MinMaxScaler()
    frame = torch.from_numpy(np.array(scaler.fit_transform(frame))).float()
    #output
    print(eval_model(model, frame))