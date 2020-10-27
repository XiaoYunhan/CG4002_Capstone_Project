import os

import numpy as np
from datetime import datetime
from joblib import load

import torch
import torch.nn as nn

from sklearn.preprocessing import MinMaxScaler

from src.models.mlp import *
from comm_external.multiple_server import *
from sklearn.ensemble import RandomForestRegressor
#from ..comm_external.DB_Client import connect

IP_ADDRESS = "127.0.0.1"
PORT = 8080
GROUP = 7
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


def process_data():  
    model = load_model(os.getcwd() + "/models/")
    rf = load('models/rf.joblib')
    model.eval()
    server = init_server()
    prev_msg = ""
    idle_count = 0
    TIMEOUT = 0
    move_frame = []
    pos_frame = []
    while 1:
        move_data = '/'.join(server.raw_data.split("/")[1:7])
        pos_data = '/'.join(server.raw_data.split("/")[7:13])
        if prev_msg != move_data:
            if TIMEOUT > 0:
                TIMEOUT = TIMEOUT - 1
            if move_data == IDLE_FRAME:
                idle_count = idle_count + 1
                if idle_count >= IGNORE_FRAME:
                    idle_count = 0
                    move_frame.clear()
            else:
                prev_msg = move_data
                idle_count = 0
                move_frame = move_frame + move_data.split("/")
                if len(move_frame) == 60:
                    df = torch.from_numpy(np.array(MinMaxScaler().fit_transform([move_frame]))).float()
                    out = eval_model(model, df)[0]
                    #connect(datetime.now().strftime("%d-%m-%y"), ACTIONS[out], 0, 0, 0, 0, 0, 0, 0, 0)
                    print("Predicted Dance Move: " + ACTIONS[out])
                    del move_frame[0:12] 
            
            if pos_data == IDLE_FRAME:
                pos_frame.clear()
            else:
                pos_frame = pos_frame + pos_data.split("/")
                if len(pos_data) == 30:
                    pos_out = rf.predict(np.array(pos_frame))
                    if TIMEOUT == 0:
                        if pos_out == 0:
                            print("Movement LEFT")
                        else:
                            print("Movement RIGHT")
                        TIMEOUT = 10



if __name__ == "__main__":
    process_data()