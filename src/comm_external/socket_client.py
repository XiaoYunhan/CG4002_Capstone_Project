import os
import sys
import random
import time

import socket
import threading

import base64
import numpy as np
from tkinter import Label, Tk
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random

class Client():
    def __init__(self, ip_addr, port_num, group_id, key):
        super(Client, self).__init__()
        self.ip_addr = ip_addr
        self.port_num = port_num
        self.group_id = group_id
        self.key = key
        self.connection = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip_addr, port_num))
        self.RTT = 0
        self.offset = 0
        print("Connected")

    def encrypt_message(self, message):
        plain_text = "#" + message
        print(plain_text)
        padded_plain_text = plain_text + ' ' * (AES.block_size - (len(plain_text) % AES.block_size))
        # print(padded_plain_text)
        iv = Random.new().read(AES.block_size)
        key = bytes(str(self.key), encoding="utf8")
        # print(key)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(iv + cipher.encrypt(bytes(padded_plain_text, "utf8")))
        return encrypted_text

    def receive_timestamp(self):
        dancer_position = self.socket.recv(1024).decode("utf8")
        return dancer_position

    def execute(self, message):
        message_encrypted = self.encrypt_message(message)
        print(message_encrypted)
        self.socket.sendall(message_encrypted)

    def stop(self):
        self.connection.close()
        self.shutdown.set()
        self.timer.cancel()


def main():
    if len(sys.argv) != 5:
        print('Invalid number of arguments')
        print('python my_client.py [IP address] [Port] [groupID] [secret key]')
        sys.exit()

    ip_addr = sys.argv[1]
    port_num = int(sys.argv[2])
    group_id = sys.argv[3]
    key = sys.argv[4]

    my_client = Client(ip_addr, port_num, group_id, key)
    
    count = 0
    raw_data = "raw_data"
    sample_input = ["-1/-1/-1/-1/-1/-1/-1/-1/-1/-1/-1/-1", "1/2/3/4/5/6/7/8/9/10/11/12"]

    time.sleep(15)

    while True:
        t1 = time.time()
        # print("t1: " + str(t1))
        my_client.execute(sample_input[count//10] + "|" + str(1000*my_client.RTT) + "|" + str(1000*my_client.offset))
        timestamp = my_client.receive_timestamp()
        t4 = time.time()
        # print("total: " + str(1000*(t4-t1)))
        t2 = float(timestamp.split("|")[0])
        t3 = float(timestamp.split("|")[1])
        # print("t1: " + str(t1))
        # print("t2: " + str(t2))
        # print("t3: " + str(t3))
        # print("t4: " + str(t4))
        my_client.RTT = (t4 - t1 - (t3 - t2))
        print("RTT(ms): " + str(1000*my_client.RTT))
        my_client.offset = (t2 - t1) - my_client.RTT/2
        print("offset(ms): " + str(1000*my_client.offset))
        # if(count == 10000) :
        #     my_client.stop()
        time.sleep(2)
        count += 1
        if(count==20):
            count = 0

if __name__ == '__main__':
    main()

