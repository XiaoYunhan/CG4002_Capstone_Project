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

ACTIONS = ['zigzag', 'rocket', 'hair']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']
LOG_DIR = os.path.join(os.path.dirname(__file__), 'evaluation_logs')
NUM_MOVE_PER_ACTION = 4
N_TRANSITIONS = 6
MESSAGE_SIZE = 3 # position, 1 action, sync 


class Server(threading.Thread):
    def __init__(self, ip_addr, port_num, group_id, n_moves=len(ACTIONS) * NUM_MOVE_PER_ACTION):
        super(Server, self).__init__()
        self.id = port_num % 10
        self.pos = self.id
        # setup moves
        self.ip_addr = ip_addr
        self.port_num = port_num
        self.actions = ACTIONS
        self.position = POSITIONS 
        self.n_moves = int(n_moves)

        # the moves should be a random distribution
        self.move_idxs = list(range(self.n_moves)) * NUM_MOVE_PER_ACTION
        assert self.n_moves == len(self.actions) * NUM_MOVE_PER_ACTION
        self.action = None
        self.action_set_time = None
        self.t2 = 0
        self.t3 = 0
        self.raw_data = ""
        self.RTT = 0
        self.offset = 0

        self.idx = 0
        self.timeout = 60
        self.has_no_response = False
        self.connection = None
        self.timer = None
        self.logout = False

        self.dancer_positions = ['1', '2', '3']

        # Create a TCP/IP socket and bind to port
        self.shutdown = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)

        print('starting up on %s port %s' % server_address, file=sys.stderr)
        self.socket.bind(server_address)

        # Listen for incoming connections
        self.socket.listen(1)
        self.client_address, self.secret_key = self.setup_connection() 

    def decrypt_message(self, cipher_text):
        decoded_message = base64.b64decode(cipher_text)
        iv = decoded_message[:16]
        secret_key = bytes(str(self.secret_key), encoding="utf8") 

        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        decrypted_message = cipher.decrypt(decoded_message[16:]).strip()
        decrypted_message = decrypted_message.decode('utf8')

        decrypted_message = decrypted_message[decrypted_message.find('#'):]
        decrypted_message = bytes(decrypted_message[1:], 'utf8').decode('utf8')

        return decrypted_message

    def run(self):
        while not self.shutdown.is_set():
            data = self.connection.recv(1024)
            self.t2 = time.time()
            if data:
                try:
                    msg = data.decode("utf8")
                    decrypted_message = self.decrypt_message(msg)
                    self.has_no_response = False
                    # print(decrypted_message) 
                    self.raw_data = decrypted_message.split("|")[0]
                    self.RTT = decrypted_message.split("|")[1]
                    self.offset = decrypted_message.split("|")[2]
                    #print("port: " + str(self.port_num), flush=True)
                    #print("raw data: " + self.raw_data, flush=True)
                    #print("RTT(ms): " + self.RTT)
                    #print("offset(ms): " + self.offset)
                    self.send_timestamp() # sendd_timestamp
                    self.set_next_action()  # Get new action
                except Exception as e:
                    print(e)
            else:
                print('no more data from', self.client_address, file=sys.stderr)
                self.stop()

    def send_timestamp(self):
        self.t3 = time.time()
        return_value = str(self.t2) + "|" + str(self.t3)
        self.connection.sendall(str(return_value).encode())

    def setup_connection(self):
        random.shuffle(self.move_idxs)
        print("No actions for 60 seconds to give time to connect")
        self.timer = threading.Timer(self.timeout, self.set_next_action)
        self.timer.start()

        # Wait for a connection
        print('waiting for a connection', file=sys.stderr)
        self.connection, client_address = self.socket.accept()

        # print("Enter the secret key: ")
        # secret_key = sys.stdin.readline().strip()
        secret_key = "passwordpassword"

        print('connection from', client_address, file=sys.stderr)
        if len(secret_key) == 16 or len(secret_key) == 24 or len(secret_key) == 32:
            pass
        else:
            print("AES key must be either 16, 24, or 32 bytes long")
            self.stop()
        
        return client_address, secret_key # forgot to return the secret key

    def stop(self):
        self.connection.close()
        self.shutdown.set()
        self.timer.cancel()

    def set_next_action(self):
        self.timer.cancel()
        if self.has_no_response:  # If no response was sent
            print("ACTION TIMEOUT")
            self.send_timestamp() # send dancer positions even at timeout

        if self.idx < self.n_moves:
            index = self.move_idxs[self.idx]
        else:
            index = self.n_moves - 1
        self.action = self.actions[int(index/NUM_MOVE_PER_ACTION)] # produces indexing error if unchanged
        position = random.randrange(0, len(POSITIONS))
        self.dancer_positions = POSITIONS[position]
        self.idx += 1
        self.action_set_time = time.time()

        self.timer = threading.Timer(self.timeout, self.set_next_action)
        self.has_no_response = True
        self.timer.start()

def main():
    if len(sys.argv) != 3:
        print('Invalid number of arguments')
        print('python server.py [IP address] [groupID]')
        sys.exit()

    # ip_addr = sys.argv[1]
    # port_num = int(sys.argv[2])
    # group_id = sys.argv[3]

    ip_addr = sys.argv[1]
    port_num1 = 8081
    port_num2 = 8082
    port_num3 = 8083
    group_id = sys.argv[2]

    my_server1 = Server(ip_addr, port_num1, group_id)
    my_server2 = Server(ip_addr, port_num2, group_id)
    my_server3 = Server(ip_addr, port_num3, group_id)
    my_server1.start()
    my_server2.start()
    my_server3.start()


if __name__ == '__main__':
    main()

