import os

import numpy as np
import pandas as pd
from datetime import datetime

import torch
import torch.nn as nn

from sklearn.preprocessing import MinMaxScaler

from .src.models.mlp import *
from ..comm_external.socket_server import *
from ..comm_external.DB_Client import connect

IP_ADDRESS = "127.0.0.1"
PORT = 8080
GROUP = 7
IDLE_FRAME = "-1/-1/-1/-1/-1/-1"
IGNORE_FRAME = 10

def init_server():
    my_server = Server(IP_ADDRESS, PORT, GROUP)
    my_server.run()
    return my_server


def load_model(PATH):
    model = ffnn()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(PATH + "mlp_1510_0451.pt", map_location=device))
    return model


def eval_model(model, frame):
        Y_test_pred = model(frame)
        Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
        _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
        return Y_pred_tags.cpu().numpy()

if __name__ == "__main__":
    
    model = load_model(os.getcwd() + "/models/")
    model.eval()
    server = init_server()
    prev_msg = ""
    idle_count = 0
    frame = []
    while(1):
        if prev_msg != server.raw_data:
            if server.raw_data == IDLE_FRAME:
                idle_count = idle_count + 1
                if idle_count >= IGNORE_FRAME:
                    idle_count = 0
                    frame.clear()
            else:
                prev_msg = server.raw_data
                s = server.raw_data.split("/").pop(0)
                frame = frame + s
                if frame.size() == 60:
                    df = torch.from_numpy(np.array(MinMaxScaler().fit_transform([frame]))).float()
                    out = eval_model(model, df)[0]
                    connect(datetime.now().strftime("%d-%m-%y"), ACTIONS[out], 0, 0, 0, 0, 0, 0, 0, 0)
                    del frame[0:19]
