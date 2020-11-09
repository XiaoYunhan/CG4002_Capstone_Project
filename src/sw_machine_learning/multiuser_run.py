from threading import Thread
#from queue import Queue
import argparse
import time
import numpy as np
from multiprocessing import Process, Queue, Array
import ctypes as c

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
        if sync_stop == False and server[0].raw_data == STOP_PATTERN and server[1].raw_data == STOP_PATTERN and server[2].raw_data == STOP_PATTERN:
            sync_stop = True
            print("!")
        # if server[0].raw_data != STOP_PATTERN and server[1].raw_data != STOP_PATTERN and server[2].raw_data != STOP_PATTERN:
        #     sync_stop = False
        check = [server[0].raw_data == STOP_PATTERN, server[1].raw_data == STOP_PATTERN, server[2].raw_data == STOP_PATTERN]
        if sync_stop == True and check.count(False) == 1:
            first_index = check.index(False)
            if first_index == 0:
                first_timestamp = time.time() - server[0].offset/1000
            elif first_index == 1:
                first_timestamp = time.time() - server[1].offset/1000
            else:
                first_timestamp = time.time() - server[2].offset/1000
        if sync_stop == True and check.count(False) == 2:
            third_index = check.index(True)
        if sync_stop == True and check.count(False) == 3:
            if third_index == 0:
                third_timestamp = time.time() - server[0].offset/1000
            elif third_index == 1:
                third_timestamp = time.time() - server[1].offset/1000
            else:
                third_timestamp = time.time() - server[2].offset/1000
            sync_stop = False
            sync_delay = third_timestamp - first_timestamp
        
        sync[0] = sync_delay
        sync[1] = time.time() #- server[0].offset/1000
        sync[2] = time.time() #- server[1].offset/1000
        sync[3] = time.time() #- server[2].offset/1000
        time.sleep(0.2)


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
    parser.add_argument('--feat', action='store_true', default=False,
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
    sync = Array(c.c_double, 4)
    #eval_client = Client("127.0.0.1", 8075, 7, "passwordpassword")
    
    #db_thread = Thread(name="DB-Thread", target=db_connect, args=(queue,eval_client) )
    #db_thread.setDaemon(True)
    #workers.append(db_thread)
    
    procs.append(Process(target=multi_user, args=(q_users, sync, args,)))
    procs.append(Process(target=process_prediction, args=(q_users, sync, args,)))
    
    for i in range(2):
        procs[i].start()
    for i in range(2):
        procs[i].join()
    
    #queue.join()
