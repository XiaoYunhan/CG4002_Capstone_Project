from bluepy import btle
from bluepy.btle import  DefaultDelegate, Peripheral, UUID, Characteristic, Scanner, BTLEInternalError, BTLEDisconnectError
import sys
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from queue import Queue
import os
import random
import socket
import threading
import base64
import numpy as np
from tkinter import Label, Tk
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random

uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
beetleAddr = ['2C:AB:33:CC:63:F1'] #['2C:AB:33:CC:65:D4'] #F8:30:02:08:E9:59', '2C:AB:33:CC:63:F1', '2C:AB:33:CC:6C:85', '2C:AB:33:CC:6C:94']
handshakeDone = [0, 0, 0, 0, 0, 0]
global string
receive = ""
queue = Queue()

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
        #print(plain_text)
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
        #print(message_encrypted)
        self.socket.sendall(message_encrypted)

    def stop(self):
        self.connection.close()
        self.shutdown.set()
        self.timer.cancel()


def set_connection(addr, index):
    #global handshakeDone
    #while True:
    print("Connecting beetle #" + str(index) + " now...")
    try:
        beetle = btle.Peripheral(addr)
        beetle.withDelegate(note_delegate(index))
        beetleService = beetle.getServiceByUUID(uuid)
        serviceChar = beetleService.getCharacteristics()[0]
        print("Connection setup with beetle #" + str(index) + " !")
    except:
        print("Failed to connect to beetle #" + str(index) + ".")
        #set_connection(addr, index)

    #init_handshake(serviceChar)
    
    while handshakeDone[index] == 0:
        init_handshake(serviceChar)
        if (beetle.waitForNotifications(1.0)):
            #called handleNotification() here
            break
        else:
            continue

    #while (sum(handshakeDone) != len(handshakeDone)):
        #time.sleep(3)

    while True:
        try:
            if(beetle.waitForNotifications(1)):
                startTime = 0.0
            else:
                currTime = time.time()
                if currTime - startTime >= 60:
                    #beetle.disconnect()
                    re_connect(beetle, index)
                else:
                    pass
            continue
        except:
               print("Beetle #" + str(index) + " disconnected")
               #beetle.disconnect()
               set_connection(beetle, index)
               break
    
    while(True):
        if beetle.waitForNotifications(1000):
            #print(receive)
            return getStr()
            continue

def re_connect(beetle, index):
    set_connection(addr, index)
    #while True:
        #try:
            #print("Re-connecting to beetle #" + str(index) + " now...")
            #set_connection(addr, index)
            #print("Re-connection setup with beetle #" + str(index))
            #break
        #except:
            #print("Failed to re-connect with beetle #" + str(index))
            #continue

class note_delegate(btle.DefaultDelegate):
    def __init__(self, index):
        btle.DefaultDelegate.__init__(self)
        self.index = index
        #self.sensorData = list()
        self.message = ""
    
    def handleNotification(self, cHandle, data):
        global receive
        receive = data.decode("utf-8")
        if receive == "ACK":
            if handshakeDone[self.index] == 0:
                handshakeDone[self.index] = 1
                print("Beetle #" + str(self.index) + " received ACK!")
                return
        elif handshakeDone[self.index] == 1:
            #print(receive) # mark
            #queue.put(receive)
            self.processData(receive)
        else:
            return

    def processData(self, rececive):
        #print(receive)
        self.message += receive
        if 'e' in receive:
            global string
            string = self.message
            string = string.replace(' ', '')
            string = string.replace('/e', '')
            string = string.replace('\n', '')
            self.message = ""
            #strLen = length(string)
            #if(self.calChecksum(string, strLen)):
               #print(string)
            
            print(string) 
            #print(ascii(string))
           # print("************************")
            queue.put(string)

    def calChecksum(self, string, strLen):
        pass
        #index = 0
        #checkSum = 0
        #while index < strLen - 2:
            #checksum += ord(string[index])
            #index += 1
        #print(checksum)
        #if(checksum == ord(string[Len - 2])):
            #return True
        #else:
            #print("Error message detected...")
            #return False

    #def getStr():
        #return string

def init_handshake(serviceChar):
    print("Sending H to beetle...")
    serviceChar.write(bytes("H".encode("utf-8")))

if __name__ == '__main__':
  
#    global index 
#    index = 1
    def thread_internal(threadname, queue):
        index = 1
        with ThreadPoolExecutor(max_workers = len(beetleAddr)) as executor:
            for beetle in beetleAddr:
                executor.submit(set_connection, beetle, index)
                index += 1

    def thread_external(threadname, queue):
        my_client = Client("127.0.0.1", 8080, 7, "passwordpassword")
        
        count = 0
        raw_data = "raw_data"

    	#time.sleep(15)
        while True:
            raw_data = queue.get()
            t1 = time.time()
            my_client.execute(raw_data + "|" + str(1000*my_client.RTT) + "|" + str(1000*my_client.offset))
            timestamp = my_client.receive_timestamp()
            t4 = time.time()
            t2 = float(timestamp.split("|")[0])
            t3 = float(timestamp.split("|")[1])
            my_client.RTT = (t4 - t1 - (t3 - t2))
            print("RTT(ms): " + str(1000*my_client.RTT))
            my_client.offset = (t2 - t1) - my_client.RTT/2
            print("offset(ms): " + str(1000*my_client.offset))
            if(count == 10000) :
                my_client.stop()
            #time.sleep(2)
            count += 1

        #while True:

            #print("Test: " + receive)
            #time.sleep(1)
           # a = queue.get()
            #print("received: " + a)

    thread1 = Thread(target = thread_internal, args = ("Thread-1", queue))
    thread2 = Thread(target = thread_external, args = ("Thread-2", queue))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
