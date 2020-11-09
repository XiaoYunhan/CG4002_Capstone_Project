from threading import Thread, Timer
import psycopg2
import logging
import statistics 
import random
import time
from datetime import datetime
import numpy as np
from time import sleep
from comm_external.multiple_server import ACTIONS
from comm_external.socket_client import Client

logging.basicConfig(level=logging.INFO,
                      format='[%(levelname)s] (%(threadName)-9s) %(message)s',)



class ProcessPrediction():

    def __init__(self, q_users, sync, args):
        logging.info("DB Thread has init")
        self.pos = "1 2 3"
        self.q_users = q_users
        self.is_eval = args.eval
        RDS_HOSTNAME = "localhost"
        RDS_USERNAME = "b07admin"
        RDS_PASSWORD = "password"
        RDS_DATABASE = "justdance"
        RDS_PORT = 3306
        
        if self.is_eval:   
            self.eval_client = Client("127.0.0.1", 8075, 7, "passwordpassword") 
        connection = psycopg2.connect(user = RDS_USERNAME,
                                      password = RDS_PASSWORD,
                                      host = RDS_HOSTNAME,
                                      port = RDS_PORT,
                                      database = RDS_DATABASE)
        connection.autocommit = True
        self.cursor = connection.cursor()
        logging.info ( connection.get_dsn_parameters())
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        #conn_msg = "You are connected to - " + record + "\n"
        #logging.info(conn_msg)
        #eval_client.execute("1 2 3"+ "|" + "zigzag" + "|" + "1.0")
        
        #self.timer = Timer(8, self.set_flag)
        self.run_flag = False
        self.start = False
        self.sync = sync
        self.positions = [1,2,3]


    def build_prob(self, pred):
        new_positions = self.positions
        matrix = [[0,0,0],[0,0,0],[0,0,0]]
        change = [0,0,0]
        for pos in pred:
            if pos[1] == 0:
                change[pos[2]-1] = change[pos[2]-1] - 1
            else:
                change[pos[2]-1] = change[pos[2]-1] + 1
        for i in range(3):
            if change[i] == 0:
                matrix[i][self.positions.index(i+1)] = 0.8
                if self.positions.index(i+1) == 2:
                    matrix[i][1] = 0.2
                    matrix[i][0] = 0
                elif self.positions.index(i+1) == 1:
                    matrix[i][0] = 0.1
                    matrix[i][2] = 0.1
                elif self.positions.index(i+1) == 0:
                    matrix[i][1] = 0.2
                    matrix[i][2] = 0
            elif change[i] > 0:
                matrix[i][self.positions.index(i+1)] = 0.1
                if self.positions.index(i+1) == 1:
                    matrix[i][0] = 0
                    matrix[i][2] = 0.9
                elif self.positions.index(i+1) == 0:
                    if change[i] == 1:
                        matrix[i][1] = 0.5
                        matrix[i][2] = 0.4
                    else:
                        matrix[i][1] = 0.4
                        matrix[i][2] = 0.5
                else:
                    matrix[i][2] = 0.9
                    matrix[i][1] = 0.1
                    matrix[i][0] = 0.0
                    
            else:
                matrix[i][self.positions.index(i+1)] = 0.1
                if self.positions.index(i+1) == 1:
                    matrix[i][0] = 0.9
                    matrix[i][2] = 0
                elif self.positions.index(i+1) == 2:
                    if change[i] == -1:
                        matrix[i][1] = 0.5
                        matrix[i][0] = 0.4
                    else:
                        matrix[i][1] = 0.4
                        matrix[i][0] = 0.5
                else:
                    matrix[i][0] = 0.9
                    matrix[i][1] = 0.1
                    matrix[i][2] = 0.0
                    
        max_pos = [[],[],[]]
        for i in range(3):
            for j in range(3):
                if len(max_pos[i]) == 0:
                    max_pos[i].append((matrix[j][i], j))
                else:
                    if max_pos[i][0][0] < matrix[j][i]:
                        if len(max_pos[i]) > 1:
                            max_pos[i] = [(matrix[j][i], j)]
                        else:
                            max_pos[i][0] = (matrix[j][i], j)
                    elif max_pos[i][0][0] == matrix[j][i]:
                        max_pos[i].append((matrix[j][i], j))
        done = [False, False, False]
        sort_pos = [max_pos[0][0],max_pos[1][0],max_pos[2][0]]
        sort_pos.sort(key = lambda x: x[0], reverse=True)
        for i in sort_pos:
            i = i[1]
            if len(max_pos[i]) == 1 and not done[i]:
                new_positions[i] = max_pos[i][0][1] + 1
                done[i] = True
                max_pos[i].pop(0)
        if not all(done):
            for i in range(3):
                if not done[i]:
                    choices = []
                    for j in max_pos[i]:
                        choices.append(j[1]+1)
                    new_positions[i] = random.choice(choices)
        self.positions = new_positions       
      
        
    def cmd_to_str(self, tup):
        return str(tup[0]) + " " + str(tup[1])

    def cmd_to_dict(self, cmd):
        cmd = cmd.split(" ")
        dict = {
            "CMD"      :   int(cmd[0]),
            "MOVE"     :   cmd[1],
            "POS_1"    :   str(self.positions[0]),
            "POS_2"    :   str(self.positions[1]),
            "POS_3"    :   str(self.positions[2])
        }
        return dict

    def db_connect(self):

        move_out = []
        move_recv = 1e12
        MOVE_TIME = 6
        pos_out = []
        pos_recv = 1e12
        POS_TIME = 3
        while True:
            if time.time() - move_recv > MOVE_TIME:
                if len(move_out) > 3:
                    logging.info("Processing " + str(len(move_out)) + " moves")
                    try:
                        self.execute(statistics.mode(move_out))
                    except:
                        self.execute(random.choice(move_out))
                    sleep(1)
                move_recv = 1e12
                move_out.clear()
                while not self.q_users.empty():
                    self.q_users.get()
            if time.time() - pos_recv > POS_TIME:
                logging.info("Processing " + str(len(move_out)) + " moves")
                self.build_prob(pos_out)
                self.execute("1 -1")
                pos_recv = 1e12
            try:
                cmd = self.q_users.get(block=False)
                logging.info(cmd)
                sleep(1e-9)
                if cmd[0] == 0:
                    move_out.append(self.cmd_to_str(cmd))
                    logging.info("Captured " + str(len(move_out)) + " moves")
                    if move_recv == 1e12:
                        move_recv = time.time()
                elif cmd[0] == 1:
                    move_out.clear()
                    pos_out.append(cmd)
                    logging.info("Captured " + str(len(move_out)) + " moves")
                    if pos_recv == 1e12:
                        pos_recv = time.time()
                elif cmd[0] == 2:
                    if self.start:
                        move_out.clear()
                        continue
                    self.execute(self.cmd_to_str(cmd))
                    self.start = True
                    continue
                    
                elif cmd[0] == 3:
                    if not self.start:
                        continue
                    move_out.clear()
                    self.execute(self.cmd_to_str(cmd))
                    break;
                #if new cmd arrives and timer is running add to list
                #if new cmd arrives and timer is not running, start timer, add to list
                #if not self.run_flag:
                    #logging.info("Timer Started")
                    #self.timer.start()
                    #self.run_flag = True
            except:
                continue

    def set_flag(self):
        self.run_flag = False
        logging.info("Timer Ended")
    
    def set_query(self, cmd, date, left_time, center_time, right_time, diff_in_timing, sync):
        POS = ["POS_1", "POS_2", "POS_3"]
        action = None
        
        if sync > 1:
            sync_str = "Yes"
        else:
            sync_str = "No"
            
        if cmd["CMD"] == 0:
            if cmd["MOVE"] == -1:
                return None, None
            action = ACTIONS[int(cmd["MOVE"])]
        elif cmd["CMD"] == 1:
            # if len([cmd[POS[0]],cmd[POS[1]],cmd[POS[2]]]) != len(set([cmd[POS[1]],cmd[POS[2]],cmd[POS[3]]])):
                # logging.info("Prediction discarded due to non-matching position change")
                # return None, None
            action = "None"
        elif cmd["CMD"] == 2:
            action = "Start"
        else:
            action = "End"
            
        query = "INSERT INTO dancedata VALUES (" + "'" + date + "'," +"'"+ action +"'"+ \
             "," +"'"+left_time +"'"+ "," + cmd[POS[0]] + "," +"'"+ center_time +"'"+ "," + cmd[POS[1]] + \
             "," +"'"+ right_time +"'"+ "," + cmd[POS[2]] + "," + diff_in_timing + "," + "'" + sync_str + "')"
        eval_msg = cmd[POS[0]] + " " + cmd[POS[1]] + " " + cmd[POS[2]] + "|" + action + "|" + str(sync)
        
        return query, eval_msg
    
    def execute(self, cmd):
        date = datetime.today().strftime('%Y-%m-%d')
        dance_move = "0"
        # sync = "Yes"
        left_time = "21:03:30.204"
        center_time = "21:03:45.304"
        right_time = "21:03:45.304"
        sync = self.sync[0]
        #left_time = time.strftime("%H:%M:%S", self.sync[1])
        #center_time = time.strftime("%H:%M:%S", self.sync[2])
        #right_time = time.strftime("%H:%M:%S", self.sync[3])
        diff_in_timing = str(np.diff(np.asarray(self.sync[1:]), n=2)[0])
        insertDanceDataQuery = None
        eval_msg = None
        
        cmd = self.cmd_to_dict(cmd)
        
        query, eval_msg = self.set_query(cmd, date, left_time, center_time, right_time, diff_in_timing, sync)
        
        if query is None or not query:
            return
                
        if self.is_eval and cmd["CMD"] == 0:
            self.eval_client.execute(eval_msg)
            self.positions = self.eval_client.receive_dancer_position().split(" ")
            logging.info("Positions reset to " + " ".join(self.positions))
            sleep(1e-12)
        logging.info(query)
        #logging.info(cmd)
        self.cursor.execute(query)
        

    
