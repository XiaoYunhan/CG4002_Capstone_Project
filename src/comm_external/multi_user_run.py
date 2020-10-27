from threading import Thread
from joblib import load
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

IP_ADDRESS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
PORT= [8080, 8081, 8082]
GROUP= [7, 7, 7]

IDLE_FRAME = "-1/-1/-1/-1/-1/-1"
IGNORE_FRAME = 10

class MultiUser():
    def __init__(self):
        self.model = load_model(os.getcwd() + "/models/")
        self.model.eval()
        self.rf = load('models/rf.joblib')
        self.lock_model = threading.Lock()
        self.lock_rf = threading.Lock()

    def init_server(self, IP_ADDR, PRT, GRP):
        my_server = Server(IP_ADDR, PRT, GRP)
        my_server.start()
        print("Server started at", IP_ADDRESS, PORT)
        return my_server


    def load_model(self, PATH):
        model = ffnn()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model.load_state_dict(torch.load(PATH + "mlp_1510_0451.pt", map_location=device))
        print("Model Loaded")
        return model


    def eval_model(self, model, frame):
            Y_test_pred = model(frame)
            Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
            _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
            return Y_pred_tags.cpu().numpy()

    def process_data(self, server):  
        prev_msg = ""
        idle_count = 0
        TIMEOUT = 0
        move_frame = []
        pos_frame = []
        while 1:
            move_data = '/'.join(server.raw.split("/")[1:7])
            pos_data = '/'.join(server.raw.split("/")[7:13])
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
                        self.lock_model.acquire()
                        try:
                            out = eval_model(self.model, df)[0]
                            #connect(datetime.now().strftime("%d-%m-%y"), ACTIONS[out], 0, 0, 0, 0, 0, 0, 0, 0)
                            print("Predicted Dance Move: " + ACTIONS[out])
                        finally:
                            self.lock_model.release()
                        del move_frame[0:12]
                
                if pos_data == IDLE_FRAME:
                    pos_frame.clear()
                else:
                    pos_frame = pos_frame + pos_data.split("/")
                    if len(pos_data) == 30:
                        self.lock_rf.acquire()
                        try:
                            pos_out = self.rf.predict(np.array(pos_frame))
                            if TIMEOUT == 0:
                                if pos_out == 0:
                                    print("Movement LEFT")
                                else:
                                    print("Movement RIGHT")
                            TIMEOUT = 10
                        finally:
                            self.lock_rf.release()                          
                            



if __name__ == "__main__":
    s_list = []
    mu = MultiUser()
    for i in range(3):
        s_list.append(mu.init_server(IP_ADDRESS[i], PORT[i], GROUP[i]))

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(mu.process_data, s_list)