from threading import Thread
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

import os

import numpy as np
from datetime import datetime

import torch
import torch.nn as nn

from sklearn.preprocessing import MinMaxScaler

from src.models.mlp import *
from sklearn.ensemble import RandomForestRegressor
from comm_external.multiple_server import *

IP_ADDRESS_1 = "127.0.0.1"
PORT_1 = 8080
GROUP_1 = 7

IP_ADDRESS_2 = "127.0.0.1"
PORT_2 = 8081
GROUP_2 = 7

IP_ADDRESS_2 = "127.0.0.1"
PORT_2 = 8082
GROUP_2 = 7

IDLE_FRAME = "-1/-1/-1/-1/-1/-1/-1/-1/-1/-1/-1/-1"
IGNORE_FRAME = 10


def init_server():
    my_server = Server(IP_ADDRESS, PORT, GROUP)
    my_server.start()
    print("Server Started")
    return my_server


def load_model(PATH):
    model = ffnn()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(PATH + "mlp_1510_0451.pt", map_location=device))
    print("Model Loaded")
    return model


def eval_model(model, frame):
        Y_test_pred = model(frame)
        Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
        _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
        return Y_pred_tags.cpu().numpy()

def process_data(server):  
    prev_msg = ""
    idle_count = 0
    frame = []
    while(1):
        #print(server.raw_data)
        move_data = '/'.join(server.raw.split("/")[1:7])
        if prev_msg != move_data:
            if move_data == IDLE_FRAME:
                idle_count = idle_count + 1
                if idle_count >= IGNORE_FRAME:
                    idle_count = 0
                    frame.clear()
            else:
                prev_msg = move_data
                idle_count = 0
                frame = frame + move_data.split("/")
                if len(frame) == 60:
                    df = torch.from_numpy(np.array(MinMaxScaler().fit_transform([frame]))).float()
                    out = eval_model(model, df)[0]
                    #connect(datetime.now().strftime("%d-%m-%y"), ACTIONS[out], 0, 0, 0, 0, 0, 0, 0, 0)
                    print("Predicted Dance Move: " + ACTIONS[out])
                    del frame[0:12]

model = load_model(os.getcwd() + "/models/")
model.eval()

if __name__ == "__main__":
    s_list = []
    for i in range(3):
        s_list.append(init_server())

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(process_data, s_list)