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
    model = mlp()
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
    MOVE_TIMEOUT = 0
    POS_TIMEOUT = 0
    move_frame = []
    pos_frame = []
    RDS_HOSTNAME = "localhost"
    RDS_USERNAME = "b07admin"
    RDS_PASSWORD = "password"
    RDS_DATABASE = "justdance"
    RDS_PORT = 3306
    date = ""
    dance_move = ""
    left_time = ""
    left_dancer = ""
    center_time = ""
    center_dancer = ""
    right_time = ""
    right_dancer = ""
    diff_in_timing = ""
    sync = ""

    connection = psycopg2.connect(user = RDS_USERNAME,
                                password = RDS_PASSWORD,
                                host = RDS_HOSTNAME,
                                port = RDS_PORT,
                                database = RDS_DATABASE)
    connection.autocommit = True
    cursor = connection.cursor()
    print ( connection.get_dsn_parameters(),"\n")
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    while 1:
        move_data = '/'.join(server.raw_data.split("/")[1:7])
        pos_data = '/'.join(server.raw_data.split("/")[7:13])
        if prev_msg != move_data:
            if MOVE_TIMEOUT > 0:
                MOVE_TIMEOUT = MOVE_TIMEOUT - 1
            if POS_TIMEOUT > 0:
                POS_TIMEOUT = POS_TIMEOUT - 1
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
                    insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ dance_move +"'"+ "," +"'"+left_time +"'"+ "," + left_dancer + "," +"'"+ center_time +"'"+ "," + center_dancer + "," +"'"+ right_time +"'"+ "," + right_dancer + "," + diff_in_timing + "," + "'" + sync + "')"
                    cursor.execute(insertDanceDataQuery)
                    #connect(datetime.now().strftime("%d-%m-%y"), ACTIONS[out], 0, 0, 0, 0, 0, 0, 0, 0)
                    print("Predicted Dance Move: " + ACTIONS[out])
                    del move_frame[0:12] 
            
            if pos_data == IDLE_FRAME:
                pos_frame.clear()
            else:
                pos_frame = pos_frame + pos_data.split("/")
                if len(pos_data) == 30:
                    pos_out = np.round(np.clip(rf.predict(np.array(pos_frame)), 0, 1)).astype(bool)[0]
                    if POS_TIMEOUT == 0:
                        if pos_out:
                            print("Movement RIGHT")
                        else:
                            print("Movement LEFT")
                        POS_TIMEOUT = 10



if __name__ == "__main__":
    process_data()
