from threading import Thread, Lock
from queue import Queue
from joblib import load
from concurrent.futures import ThreadPoolExecutor

import os, time
import psycopg2
import numpy as np
from datetime import datetime

    

class MultiUser():
    def __init__(self, queue):
        self.lock_rf = Lock()
        self.queue = queue
        self.q_pkt = [(-1,1),(-1,2),(-1,3)]

    def process_data(self, id): 
        print("Beginning data processing", flush=True)
        while True:
            self.lock_rf.acquire()
            try:
                self.q_pkt[id] = (self.q_pkt[id][0] + 1, self.q_pkt[id][1])
                self.queue.put(self.q_pkt)
            finally:
                self.lock_rf.release()                     
                            



def multi_user_run(queue):
    s_list = []
    mu = MultiUser(queue)
    for i in range(3):
        s_list.append(i)
        #time.sleep(3)
    with ThreadPoolExecutor(max_workers=3) as executor:
        while 1:
            executor.map(mu.process_data, s_list)

#Db side wait for move detection output from 3 queues, if not all output, clear the queue

def db_connect(queue):
    while 1:
        if not queue.empty():
            out = queue.get()
            print(out, flush=True)

if __name__ == "__main__":
    queue = Queue()
    mu = MultiUser(queue)
    workers = []
    for i in range(3):
         workers.append(Thread(target=mu.process_data, args=(i,)))
         workers[i].setDaemon(True)
         workers[i].start()
    thread2 = Thread(target=db_connect, args=(queue,) )
    thread2.setDaemon(True)
    thread2.start()
    thread2.join()
    for i in range(3):
         workers[i].join()
