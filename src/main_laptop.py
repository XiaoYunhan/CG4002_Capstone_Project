import sys
import time
from sys import path
sys.path.append('CG4002_Capstone_Project/src/comm_internal/')
from comm_internal.comm_internal import set_connection
from comm_external.socket_client import Client
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading
beetleAddr = ['F8:30:02:08:E9:59'] #, '2C:AB:33:CC:63:F1', '2C:AB:33:CC:6C:85', '2C:AB:33:CC:6C:94']
index = 1

def main():

    """ declaration & initialization """
    # count = 0
    # raw_data = "raw_data"

    # socket_client = Client("127.0.0.1", 8080, 7, "passwordpassword")

    with ThreadPoolExecutor(max_workers = len(beetleAddr)) as executor:
        for beetle in beetleAddr:
            executor.submit(set_connection, beetle, index)
            index += 1

    # time.sleep(15)

    """ infinite loop to run services on laptop side """
    # while True:
    #     t1 = time.time()
    #     socket_client.execute(raw_data + "|" + str(1000*socket_client.RTT) + "|" + str(1000*socket_client.offset))
    #     timestamp = socket_client.receive_timestamp()
    #     t4 = time.time()
    #     t2 = float(timestamp.split("|")[0])
    #     t3 = float(timestamp.split("|")[1])
    #     socket_client.RTT = (t4 - t1 - (t3 - t2))
    #     print("RTT(ms): " + str(1000*socket_client.RTT))
    #     socket_client.offset = (t2 - t1) - socket_client.RTT/2
    #     print("offset(ms): " + str(1000*socket_client.offset))
    #     if(count == 10000) :
    #         socket_client.stop()
    #     time.sleep(2)
    #     count += 1


if __name__ == '__main__':
    main()
