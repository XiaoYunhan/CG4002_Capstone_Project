from threading import Thread
#from queue import Queue
import argparse
import time
import numpy as np
import datetime
import multiprocessing as mp
from multiprocessing import Process, Queue, Array

from src.db_connect import ProcessPrediction
from src.multiuser import MultiUser
import warnings
warnings.filterwarnings('ignore')
#from comm_external.socket_client import Client

IP_ADDRESS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
PORT= [8081, 8082, 8084]
GROUP= [7, 7, 7]

def sync_delay(server, sync):
    STOP_PATTERN = "-1/-1/-1/-1/-1/-1/-1/-1/-1/-1/-1/-1"
    sync_stop = False
    sync_start = False
    first_timestamp = time.time()
    third_timestamp = time.time()
    sync_delay = 0
    first_index = 1
    third_index = 1
    while True:
        # print("server1: " + server[0].raw_data)
        # print("server2: " + server[1].raw_data)
        # print("server3: " + server[2].raw_data)
        if sync_stop == False and STOP_PATTERN in server[0].raw_data and STOP_PATTERN in server[1].raw_data and STOP_PATTERN in server[2].raw_data:
            sync_stop = True
            # for i in range(10):
                # print("!")
        # if server[0].raw_data != STOP_PATTERN and server[1].raw_data != STOP_PATTERN and server[2].raw_data != STOP_PATTERN:
        #     sync_stop = False
        check = [STOP_PATTERN in server[0].raw_data, STOP_PATTERN in server[1].raw_data, STOP_PATTERN in server[2].raw_data]
        if sync_stop == True and check.count(False) == 1:
            first_index = check.index(False)
            if first_index == 0:
                first_timestamp = time.time() - server[0].offset/1000.0
            elif first_index == 1:
                first_timestamp = time.time() - server[1].offset/1000.0
            else:
                first_timestamp = time.time() - server[2].offset/1000.0
        if sync_stop == True and check.count(False) == 2:
            third_index = check.index(True)
        if sync_stop == True and check.count(False) == 3:
            if third_index == 0:
                third_timestamp = time.time() - server[0].offset/1000.0
            elif third_index == 1:
                third_timestamp = time.time() - server[1].offset/1000.0
            else:
                third_timestamp = time.time() - server[2].offset/1000.0
            sync_stop = False
            sync_delay = abs(third_timestamp - first_timestamp)
        
        sync[0] = sync_delay * 1000
        #sync[0] = random.randrange(0,100)/100.0
        sync[1] = server[0].offset/1000.0
        sync[2] = server[1].offset/1000.0
        sync[3] = server[2].offset/1000.0
        time.sleep(0.01)


def multi_user(q_users, sync, args):

    mu = MultiUser(q_users, args)
    workers = []
    server = []
    for i in range(args.num_users):
        server.append(mu.init_server(IP_ADDRESS[i], PORT[i], GROUP[i], i + 1))
        workers.append(Thread(name="User-" + str(i+1), target=mu.process_data, args=(server[i],)))
        workers[i].setDaemon(True)
    if args.num_users == 3:
        workers.append(Thread(name="SyncThread", target=sync_delay, args=(server, sync)))
    for i in range(len(workers)):
        workers[i].start()
    for i in range(len(workers)):
         workers[i].join()


def process_prediction(q_users, sync, args):
    pred = ProcessPrediction(q_users, sync, args)
    pred.db_connect()
    #process_thread = Thread(name="Process-Thread", target=pred.db_connect, args=())
    #process_thread.start()
    #process_thread.join()
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fpga', '-f', action='store_true', default=False,
                    dest='use_fpga',
                    help='Use FPGA for prediction')
    parser.add_argument('--feat', action='store_true', default=True,
                    dest='use_feat',
                    help='Use FPGA for prediction')
    parser.add_argument('-u', type=int, default=3, action='store', dest='num_users',
                    help='Number of Users')
    parser.add_argument('-e', action='store_true', default=False,
                    dest='eval',
                    help='Connect to evaluation server')
    args = parser.parse_args()

    q_users = Queue()
    procs = []
    #sync = Array(c.c_double, 4)
    sync = Array('d', 4)
    #eval_client = Client("127.0.0.1", 8075, 7, "passwordpassword")
    
    #db_thread = Thread(name="DB-Thread", target=db_connect, args=(queue,eval_client) )
    #db_thread.setDaemon(True)
    #workers.append(db_thread)
    
    print("[Power Saving] Running on", mp.cpu_count, "cores.")
    #procs.append(Process(target=multi_user, args=(q_users, sync, args,)))
    procs.append(Process(target=process_prediction, args=(q_users, sync, args,)))
    
    for i in range(len(procs)):
        procs[i].start()
    multi_user(q_users, sync, args)
    for i in range(len(procs)):
        procs[i].join()
    
    #queue.join()
