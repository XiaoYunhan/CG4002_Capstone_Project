import sys
from sys import path
sys.path.append('CG4002_Capstone_Project/src/comm_internal/')
from comm_internal.comm_internal import set_connection
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading
beetleAddr = ['F8:30:02:08:E9:59'] #, '2C:AB:33:CC:63:F1', '2C:AB:33:CC:6C:85', '2C:AB:33:CC:6C:94']
index = 1

if __name__ == '__main__':

    with ThreadPoolExecutor(max_workers = len(beetleAddr)) as executor:
        for beetle in beetleAddr:
            executor.submit(set_connection, beetle, index)
            index += 1


