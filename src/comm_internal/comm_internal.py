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
beetleHandshake = [0, 0, 0, 0, 0, 0]
entryFlag = 1
dataFlag = 0
index = 1
uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"

def set_connection(addr, index):
    global beetleHAndshake
    while True:
        #for index in range(len(beetleAddr)):
            #if beetleAddr[index] == addr:
        if connectedBeetle[index] != 0:
            return
        else:
            print("Connecting Beetle No." + str(index) + "now...")
            try:
                beetle = btle.Peripheral(addr)
                connectedBeetle[index] = beetle
                beetleDelegate = note_delegate(addr)
                connectedDelegate[index] = beetleDelegate
                beetle.withDelegate(beetleDelegate)
                beetleService = beetle.getServiceUUID("0000dfb0-0000-1000-8000-00805f9b34fb")
                serviceChara = beetleService.getCharacteristics()[0]
                break
            except:
                continue
            print("Connection setup with beetle No." + str(index))
              
            while beetleHandshake[index] == 0:
                init_handshake(serviceChara)
                if (p.waitFotNotifications(1)):
                    break
                else:
                    continue
            while (sum(beetleHandshake) != len(beetleHAndshake)):
                time.sleep(3)
              
            while True:
               try:
                   if(p.waitForNotifications(1)):
                       startTime = 0.0
                   else:
                       currTime = time.time()
                       if currTime - startTime >= 5:
                           beetle.disconnect()
                           re_connect(beetle, index)
                       else:
                           pass
                   continue
               except:
                   print("Beetle No." + str(index) + "disconnected")
                   beetle.disconnect()
                   break
               re_connect(beetle, index)

def re_connect(beetle, index):
    while True:
        try:
            print("re-connecting to%s now..." % (beetle.addr))
            set_connection(addr, index)
            print("Re-connection setup with %s" % (beetle.addr))
            break
        except():
            print("Failed to re-connect to %s" %(beetle.addr))
            #time.sleep(5)
            continue

class note_delegate(btle.DefaultDelegate):
    def __init__(self, index):
        btle.DefaultDelegate.__init__(self)
        self.index = index
        self.sensorData = list()
        self.message = ""

    def handle_notification(self, cHandle, data):
        global handshakeDone
        receive = data.decode("utf-8")
        if receive == "ACK":
            if handshakeDone[self.index] == 0:
                handshakeDone[self.index] = 1
                print("Beetle No." + str(self.index) + "received ACK!")
        elif handshakeDone[self.index] == 1:
            self.handle_data(receive)
        else:
            pass
        #receiving_timestamp = time.time() * 1000
        #print("Notification:" + str(cHandle) + str(data) +"\n")

        def handle_data(self, rececive):
            global entryFlag
            global dataFlag
            global index
            global start
        
            if(entryFlag):
                print("Receving data from beetle No." + str(self.index))
                entryFlag = 0
            receive.replace(" ", "|")
            self.message += receive 
            print(self.message)

        #def checksumCheck(self, msgString, msgLen):
            #index = 0
            #checkSum = 0
            #while index < msgLen - 2:
                #checkSum ^= ord(msgString[index])
                #index += 1
            #checksum = 
            #if(checksum == ord(msgString[msgLen - 2])):
                #return True
            #else:
                #print("Error message detected...")
                #return False

def init_handshake(beetle):

    #sending_timestamp = time.time() * 1000

    for characteristic in beetle.getCharacteristics():
        if characteristic.uuid == uuid:
             #sending_timestamp = time.time() * 1000
             print("Sending 'H' to %s" % (beetle.addr))
             characteristic.write(bytes("H".encode("utf-8")))

if __name__ == '__main__':
    #[connectedBeetleAddr.append(0) for index in range(len(beetleAddr))]
    #[connectedDelegate.append(0) for index in range(len(beetleAddr))]

    #set_connection('F8:30:02:08:E9:59', 1)
    #time.sleep(5)

    #set_connection('2C:AB:33:CC:63:F1')
    #time.sleep(5)

    #set_connection('2C:AB:33:CC:6C:85')
    #time.sleep(5)

    #set_connection('2C:AB:33:CC:6C:94')
    #time.sleep(5)

    with ThreadPoolExecutor(max_workers = len(beetleAddr)) as executor:
        for beetle in beetleAddr:
            executor.submit(set_connection, beetle, index)
            index += 1

