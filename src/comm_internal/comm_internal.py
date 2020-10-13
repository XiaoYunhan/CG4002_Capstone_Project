from bluepy import btle
from bluepy.btle import  DefaultDelegate, Peripheral, UUID, Characteristic, Scanner, BTLEInternalError, BTLEDisconnectError
import sys
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading

uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"
beetleAddr = ['F8:30:02:08:E9:59'] #, '2C:AB:33:CC:63:F1', '2C:AB:33:CC:6C:85', '2C:AB:33:CC:6C:94']
handshakeDone = [0, 0, 0, 0, 0, 0]
index = 1

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
        re_connect(addr, index)

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
                if currTime - startTime >= 10:
                    beetle.disconnect()
                    re_connect(beetle, index)
                else:
                    pass
            continue
        except:
               print("Beetle No." + str(index) + " disconnected")
               beetle.disconnect()
               break
        #re_connect(beetle, index)
    
    while(True):
        if beetle.waitForNotifications(1000):
            #print(receive)
            #processData(receive)
            continue
    #print(receive)

def re_connect(beetle, index):
    while True:
        try:
            print("Re-connecting to beetle #" + str(index) + " now...")
            set_connection(addr, index)
            print("Re-connection setup with beetle #" + str(index))
            break
        except:
            print("Failed to re-connect with beetle #" + str(index))
            continue

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
            print(receive)
            self.processData(receive)
        else:
            return

    def processData(self, rececive):
        self.message += receive
        if 'e' in receive:
            string = self.message
            string = string.replace('e', '')
            string = string.replace(' ', '|')
            #strLen = length(string)
            #if(self.calChecksum(string, strLen)):
               #print(string)
            
            print(string)

    def calChecksum(self, string, strLen):
        index = 0
        checkSum = 0
        while index < strLen - 2:
            checksum += ord(string[index])
            index += 1
        print(checksum)
        if(checksum == ord(string[Len - 2])):
            return True
        else:
            print("Error message detected...")
            return False

def init_handshake(serviceChar):
    print("Sending H to beetle...")
    serviceChar.write(bytes("H".encode("utf-8")))

if __name__ == '__main__':

    with ThreadPoolExecutor(max_workers = len(beetleAddr)) as executor:
        for beetle in beetleAddr:
            executor.submit(set_connection, beetle, index)
            index += 1

