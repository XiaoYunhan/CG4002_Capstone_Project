from threading import Thread
#from queue import Queue
import argparse
from multiprocessing import Process, Queue

from src.db_connect import ProcessPrediction
from src.multiuser import MultiUser
#from comm_external.socket_client import Client

IP_ADDRESS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
PORT= [8081, 8085, 8083]
GROUP= [7, 7, 7]

def multi_user(queue, args):

    mu = MultiUser(queue, args.use_fpga)
    workers = []
    for i in range(args.num_users):
        server = mu.init_server(IP_ADDRESS[i], PORT[i], GROUP[i], i + 1)
        workers.append(Thread(name="User-" + str(i+1), target=mu.process_data, args=(server,)))
        workers[i].setDaemon(True)
    for i in range(args.num_users):
        workers[i].start()
    for i in range(args.num_users):
         workers[i].join()

def process_prediction(queue, eval):
    pred = ProcessPrediction(queue, eval)
    process_thread = Thread(name="Process-Thread", target=pred.db_connect, args=())
    process_thread.start()
    process_thread.join()
    
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fpga', '-f', action='store_true', default=False,
                    dest='use_fpga',
                    help='Use FPGA for prediction')
    parser.add_argument('-u', type=int, default=3, action='store', dest='num_users',
                    help='Number of Users')
    parser.add_argument('-e', action='store_true', default=False,
                    dest='eval',
                    help='Connect to evaluation server')
    args = parser.parse_args()

    queue = Queue()
    procs = []
    eval_client = Client("127.0.0.1", 8075, 7, "passwordpassword")
    
    db_thread = Thread(name="DB-Thread", target=db_connect, args=(queue,eval_client) )
    db_thread.setDaemon(True)
    procs.append(Process(target=multi_user, args=(queue, args,)))
    procs.append(Process(target=process_prediction, args=(queue, args.eval,)))
    workers.append(db_thread)
    for i in range(2):
        procs[i].start()
    for i in range(2):
        procs[i].join()
    
    queue.join()
