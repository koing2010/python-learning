import serial
#from serial import win32
import time
import threading
import os
import struct
import sys
import queue
import TEA
import hashlib
import crclib
import ModleMgmt
from zlib import crc32


# define the ack status
StatusSuccess = 0x00
#MD5 = hashlib.md5()

START_1_STATE = 0
START_2_STATE = 1
START_3_STATE = 2
START_4_STATE = 3
PKT_TYPE_STATE = 4
LEN_L_STATE = 5
LEN_H_STATE = 6
DATA_STATE = 7

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print("Starting " + self.name)
        if self.threadID is 1:
           process_data(self.name, self.q)
        elif self.threadID is 2:
           txdata(self.name, self.q)
        elif self.threadID is 3:
            inputTxThread(self.name, self.q)
        elif self.threadID is 4:
            AutoSendThread(self.name, self.q)
        else:
            print("Thread Start ERRO!")
        print("Exiting " + self.name)

def AutoSendThread(threadName,MsgQue):
    print(threadName + "start")
    while True:
        time.sleep(2.5)
        userInputQueue.put("OPEN")
        time.sleep(2.5)
        userInputQueue.put("LOCK")

#user input
def inputTxThread(threadName,MsgQue):
    print(threadName + "start")
    while True:
        #if not MsgQue.empty():
         #   data = MsgQue.get()
            data = input("Please Enter CMD:")
            if data == "SCAN":
                Msg = (b'')
                SendMsg = PackSendData(0x01, 0xC8, Msg)
                sendQueue.put(SendMsg)
            if data == "OPEN":
                Msg = struct.pack('>BBH', 80, 0x15, 0x0001)#
                SendMsg = PackSendData(0x01, 0xC3, Msg)
                sendQueue.put(SendMsg)
            if data == "LOCK":
                Msg = struct.pack('>BBH', 80, 0, 0x0000)
                SendMsg = PackSendData(0x01, 0xCA, Msg)
                sendQueue.put(SendMsg)


# usart tx data
def txdata(threadName, q):
	print(threadName + "start")
	while (1):
		while not sendQueue.empty():
			txda = sendQueue.get()
			s.write(txda)
			#HexShow("txthread:",txda)
			time.sleep(0.05)
#usart rx data
def process_data(threadName, q):
    print(threadName + "start")
    RxStatus = START_1_STATE
    LenToken = 0
    LenTemp = 0
    while True:
        while s.inWaiting() == 0:
            pass
        byte = s.read(1)
        if RxStatus == START_1_STATE:
            if byte[0] == 0xFF:
                RxStatus = START_2_STATE
        elif RxStatus == START_2_STATE:
            if byte[0] == 0xFF:
                RxStatus = START_3_STATE
            else:
                RxStatus = START_1_STATE
        elif RxStatus == START_3_STATE:
            if byte[0] == 0xFF:
                RxStatus = START_4_STATE
            else:
                RxStatus = START_1_STATE
        elif RxStatus == START_4_STATE:
            if byte[0] == 0xFF:
                RxStatus = PKT_TYPE_STATE
            else:
                RxStatus = START_1_STATE
        elif RxStatus == PKT_TYPE_STATE:
            if byte[0] == 0x01 or byte[0] == 0x07:
                RxStatus = LEN_H_STATE
                string = byte
            else:
                RxStatus = START_1_STATE
        elif RxStatus == LEN_H_STATE:
            if byte[0] == 0:
                RxStatus = LEN_L_STATE
                string += byte
            else:
                RxStatus = START_1_STATE
        elif RxStatus == LEN_L_STATE:
            if byte[0] != 0x00:
                LenToken = byte[0]
                LenTemp = 0
                RxStatus = DATA_STATE
                string += byte
            else:
                RxStatus = START_1_STATE
        elif RxStatus == DATA_STATE:
            string += byte
            LenTemp += 1

            n = s.inWaiting()
            if n <= (LenToken - LenTemp):
                string += s.read(n)
                LenTemp += n
            else:
                string += s.read(LenToken - LenTemp)
                LenTemp += (LenToken - LenTemp)
            if LenTemp == LenToken:
                RxStatus = START_1_STATE
                workQueue.put(string)# send the data to
        else:
            RxStatus = START_1_STATE
	#	queueLock.acquire()
	#	workQueue.put(rxdata)
    #    queueLock.release()

def PackSendData( PKT_TYPE, CMD, Msg):
    lenth = len(Msg) + 1 + 2 # 1byte CMD + 2bytes Sum16
    SendMsg = struct.pack('>BHB', PKT_TYPE, lenth, CMD) + Msg
    SendMsg = SendMsg + struct.pack('>H', crclib.CheckSum16(SendMsg)) # CheckSum16
    SendMsg = struct.pack('>HI',0xEE01, 0xFFFFFFFF) + SendMsg
    HexShow("Txdata: ",SendMsg)
    SendMsg = (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00') + SendMsg
    return SendMsg

#display hex string
def HexShow(S_name,i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print(S_name,hex_string,'	total:',hLen)

###++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++###
Comnumb = 'com13'
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
if s._port is None:
	print('Port must be configured before it can be used.')
	while True:
		pass

string = ''

queueLock = threading.Lock()
workQueue = queue.Queue(maxsize = 10)
sendQueue = queue.Queue(maxsize = 10)
userInputQueue = queue.Queue(maxsize = 10)

Rxthrd = myThread(1,'uartRxThread',workQueue)
Rxthrd.start()# start threading
Txthrd = myThread(2,'uartTxThread',sendQueue)
Txthrd.start()# start threading
#Sendthrd = myThread(4,'AutoSendThread',userInputQueue)
#Sendthrd.start()
Inthrd =  myThread(3,'inputTxThread',userInputQueue)
Inthrd.start()
#主体
#s.write(b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
time.sleep(0.2)
while (1) :

    #print(type(rx_string))
#   userInputQueue.put("OPEN")


    if not workQueue.empty():
        rx_string = workQueue.get()
        if ( len(rx_string) >= 4 )and (len(rx_string) == rx_string[2]+3):
            if rx_string[0] == 0x01 :
               if rx_string[3] == 0xC3 and rx_string[5] == 0x95:
                   Msg = struct.pack('>BBH', 80, 0x03, 0x0000)#PWR, TYPE  ,ID
                   SendMsg = PackSendData(0x01, 0xC3, Msg)
                   sendQueue.put(SendMsg)

        else:
            print("Format Lenth ERR!")
    else:
        continue
    print("\n")

    HexShow( "UartRxMsg",rx_string )

        #s.flushInput()
s.close()
input('Press Enter Key Exit~')
Rxthrd.join()
Txthrd.join()
Inthrd.join()
#Sendthrd.join()