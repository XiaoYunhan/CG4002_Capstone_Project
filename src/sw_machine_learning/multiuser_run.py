from threading import Thread
from queue import Queue
import argparse

from src.db_connect import db_connect
from src.multiuser import MultiUser

IP_ADDRESS = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
PORT= [8081, 8085, 8083]
GROUP= [7, 7, 7]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fpga', '-f', action='store_true', default=False,
                    dest='use_fpga',
                    help='Use FPGA for prediction')
    parser.add_argument('-u', type=int, default=3, action='store', dest='num_users',
                    help='Number of Users')
    args = parser.parse_args()

    queue = Queue()
    mu = MultiUser(queue, args.use_fpga)
    workers = []
    
    for i in range(args.num_users):
        server = mu.init_server(IP_ADDRESS[i], PORT[i], GROUP[i], i + 1)
        workers.append(Thread(name="User-" + str(i+1), target=mu.process_data, args=(server,)))
        workers[i].setDaemon(True)
    db_thread = Thread(name="DB-Thread", target=db_connect, args=(queue,) )
    db_thread.setDaemon(True)
    workers.append(db_thread)
    for i in range(args.num_users + 1):
        workers[i].start()
    for i in range(args.num_users + 1):
         workers[i].join()
    #queue.join()
