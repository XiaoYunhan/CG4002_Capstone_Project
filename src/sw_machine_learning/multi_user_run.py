from threading import Thread
from queue import Queue
from joblib import load
from concurrent.futures import ThreadPoolExecutor

import os, time
import psycopg2
import numpy as np
from datetime import datetime

#import torch
#import torch.nn as nn
from sklearn.svm import SVC

from sklearn.preprocessing import MinMaxScaler

#from src.models.mlp import *
from sklearn.ensemble import RandomForestRegressor
from comm_external.multiple_server import *

IP_ADDRESS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
PORT= [8081, 8082, 8083]
GROUP= [7, 7, 7]

IDLE_FRAME = "-1/-1/-1/-1/-1/-1"
IGNORE_FRAME = 10

class Q_Pkt():
    def __init__(self):
        #move1 pos1 move2 pos2 move3 pos3
        self.data = [(0,1),(0,2),(0,3)]

class MultiUser():
    def __init__(self, queue):
        #self.model = load_model(os.getcwd() + "/models/")
        #self.model.eval()
        self.model = load('models/rbf.joblib')
        self.rf = load('models/rf.joblib')
        self.lock_model = threading.Lock()
        self.lock_rf = threading.Lock()
        self.queue = queue
        self.q_pkt = Q_Pkt()

    def init_server(self, IP_ADDR, PRT, GRP):
        my_server = Server(IP_ADDR, PRT, GRP)
        my_server.start()
        print("Server started at", IP_ADDRESS, PORT)
        return my_server


    # def load_model(self, PATH):
    #     model = mlp()
    #     device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    #     model.load_state_dict(torch.load(PATH + "mlp_1510_0451.pt", map_location=device))
    #     print("Model Loaded")
    #     return model


    # def eval_model(self, model, frame):
    #     Y_test_pred = model(frame)
    #     Y_pred_softmax = torch.log_softmax(Y_test_pred, dim = 1)
    #     _, Y_pred_tags = torch.max(Y_pred_softmax, dim = 1)
    #     return Y_pred_tags.cpu().numpy()

    def process_data(self, server):  
        prev_msg = ""
        idle_count = 0
        MOVE_TIMEOUT = 0
        POS_TIMEOUT = 0
        move_frame = []
        pos_frame = []
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
                        #df = torch.from_numpy(np.array(MinMaxScaler().fit_transform([move_frame]))).float()
                        #self.lock_model.acquire()
                        #try:
                        #out = eval_model(self.model, df)[0]
                        out = self.model.predict([move_frame])[0]
                        #connect(datetime.now().strftime("%d-%m-%y"), ACTIONS[out], 0, 0, 0, 0, 0, 0, 0, 0)
                        print("Predicted Dance Move: " + ACTIONS[out])
                        self.q_pkt[server.id - 1] = (out, server.pos) 
                        self.queue.put()
                        self.q_pkt[server.id -1] = (-1, server.pos)
                        #finally:
                            #self.lock_model.release()
                        del move_frame[0:12]
                
                if pos_data == IDLE_FRAME or POS_TIMEOUT > 0:
                    pos_frame.clear()
                else:
                    pos_frame = pos_frame + pos_data.split("/")
                    if len(pos_data) == 30:
                        #self.lock_rf.acquire()
                        #try:
                        pos_out = np.round(np.clip(self.rf.predict([pos_frame]), 0, 1)).astype(bool)[0]
                        if pos_out:
                            print("Movement RIGHT")
                            if server.pos != 3:
                                server.pos = server.pos + 1
                        else:
                            print("Movement LEFT")
                            if server.pos != 1:
                                server.pos =  server.pos - 1
                        pos_frame.clear()
                        self.q_pkt[server.id - 1] = (-1, server.pos) 
                        self.queue.put()
                        POS_TIMEOUT = 10
                        #finally:
                            #self.lock_rf.release()                          
                            



def multi_user_run(queue):
    s_list = []
    mu = MultiUser(queue)
    for i in range(3):
        s_list.append(mu.init_server(IP_ADDRESS[i], PORT[i], GROUP[i]))
        #time.sleep(3)
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(mu.process_data, s_list)

#Db side wait for move detection output from 3 queues, if not all output, clear the queue

def db_connect(self, queue):
    RDS_HOSTNAME = "localhost"
    RDS_USERNAME = "b07admin"
    RDS_PASSWORD = "password"
    RDS_DATABASE = "justdance"
    RDS_PORT = 3306
    flag = False
    date = "2020-10-27"
    dance_move = "0"
    left_time = "21:03:30.204"
    left_dancer = "0"
    center_time = "21:03:45.304"
    center_dancer = "0"
    right_time = "21:03:45.304"
    right_dancer = "0"
    diff_in_timing = "0"
    sync = "Yes"

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

    while not queue.empty():
        cmd = queue.get()
        for i in range(3):
            if cmd[i][0] != -1:
                insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ ACTIONS[cmd[i][0]] +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
                flag = True
                break
        if not flag:
            insertDanceDataQuery = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ str(cmd[0][0]) +"'"+ "," +"'"+left_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[0][1]) + "," +"'"+ center_time +"'"+ "," + str(cmd[1][1]) + "," +"'"+ right_time +"'"+ "," + str(cmd[2][1]) + "," + diff_in_timing + "," + "'" + sync + "')"
            flag = False
        cursor.execute(insertDanceDataQuery)

if __name__ == "__main__":
    queue = Queue()
    multi_user_run(queue)
    # thread1 = Thread(target=multi_user_run, args=("MU-Thread", queue) )
    # thread2 = Thread(target=db_connect, args=("DB-Thread", queue) )
    # thread1.start()
    # thread2.start()
