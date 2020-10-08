from bluepy import btle
from bluepy.btle import  DefaultDelegate, Peripheral, UUID, Characteristic
import sys
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import numpy
import threading

beetleAddr = ['F8:30:02:08:E9:59', '2C:AB:33:CC:63:F1', '2C:AB:33:CC:6C:85', '2C:AB:33:CC:6C:94']
connectedBeetle = [0, 0, 0, 0, 0, 0] # 0 if the beetle corresponding  to the index is not connected
connectedDelegate = [0, 0, 0, 0, 0, 0]

uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"

def set_connection(addr):
    while True:
        for index in range(len(beetleAddr)):
            if beetleAddr[index] == addr:
                if connectedBeetle[index] != 0:
                    return
                else:
                    print("connecting %s now..." % (addr))
                    beetle = btle.Peripheral(addr)
                    connectedBeetle[index] = beetle
                    beetleDelegate = note_delegate(addr)
                    connectedDelegate[index] = beetleDelegate
                    beetle.withDelegate(beetleDelegate)

                    init_handshake(beetle)
                    print("Connection setup with %s!!" % (addr))
                    return

def re_connect(beetle):
    while True:
        try:
            print("re-connecting to%s now..." % (beetle.addr))
            beetle.connect(beetle.addr)
            print("Re-connection setup with %s" % (beetle.addr))
            receive_data(beetle)
            return
        except():
            print("Failed to re-connect to %s" %(beetle.addr))
            time.sleep(5)
            continue
class note_delegate(btle.DefaultDelegate):
    def __init__(self, number):
        btle.DefaultDelegate.__init__(self)

        #self.number = number
        #self.message_str = ""

    def handle_notification(self, cHandle, data):
        #receiving_timestamp = time.time() * 1000
        print("Notification:" + str(cHandle) + str(data) +"\n")


def init_handshake(beetle):

    #sending_timestamp = time.time() * 1000

    for characteristic in beetle.getCharacteristics():
        if characteristic.uuid == uuid:
             #sending_timestamp = time.time() * 1000
             print("Sending 'H' to %s" % (beetle.addr))
             characteristic.write(bytes("H".encode("utf-8")))

def receive_data(beetle):
    while True:
        try:
            if beetle.waitForNotification(20):
                print("receiving data from %s" % (beetle.addr))
        except():
            print("The connection with %s is lost..." % (beetle.addr))
            re_connect(beetle)
