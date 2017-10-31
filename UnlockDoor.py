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
from zlib import crc32

PassWordSalt = 'F9120481520D8202FA0A02DFDB575BA7'.encode(encoding='utf-8')
RandNumberSalt='A0FB8A2FD2352AF6432C481FCDD45CB2'.encode(encoding='utf-8')
PublicKey =  (b'\x38\x45\x42\x37\x30\x30\x39\x39\x30\x46\x45\x44\x30\x36\x31\x44')
# define every command of
Send_Lenth = 0x0001
Send_SN = 1
TyHeader = 0xB8
ProtocolType= 0x01
IEEE64 = bytes.fromhex("08 F7 7F BB 0D 00 4B 12 00")#(b'\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00')
print(IEEE64)
EndPoint = 0x0E
ClusterDoorLock = 0x0101
HaHeader = 0x19 #type = 01 direction = 1 no_rsp = 1


atrrCmd = 0x0001#coordinator report
# define every attribtes
SystemDescriptionAtrr = 0x01
ManufactureAtrr  = 0x02
ModelIDAtrr  = 0x03
FileSizeAtrr  = 0x0A
FileDataAtrr  = 0x0B
# define the ack status
StatusSuccess = 0x00
#MD5 = hashlib.md5()

START_L_STATE = 0
START_H_STATE = 1
LEN_L_STATE = 2
LEN_H_STATE = 3
DATA_STATE = 4

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
        else:
            print("Thread Start ERRO!")
        print("Exiting " + self.name)
#user input
def inputTxThread(threadName,MsgQue):
    print(threadName + "start3")
    while True:
        data = input('Please input CMD')
        if (data[0:9] == "OPEN DOOR") or (data[0:9] == "CLOS DOOR"):#OPEN DOOR123456
            #bytesData = bytes.fromhex(data[9:])
            msg = struct.pack('<H',0x0040)
            HexShow("msg= ",msg)
            #read the Random data
            sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 0, 0))
            delay = 0
            while True:
                if not MsgQue.empty():
                    rxdata = MsgQue.get()
                    if rxdata[0] == StatusSuccess:#status
                        print("Success")
                        if rxdata[1]== 0x08:# must be 8
                            print("lenth Success")
                            Random = TEA.decrypt(rxdata[2:10],PublicKey)
                            print("Random =",Random)
                            print("UserINputKeyWords=",data[9:])
                            MD5 = hashlib.md5()
                            MD5.update(data[9:].encode(encoding='utf-8')+ PassWordSalt)
                            Md5InputKey = str.upper((MD5.hexdigest())[0:32:4])
                            print("MD5(UserINputKeyWords+PassWordSalt)=",Md5InputKey)
                            crc = crc32(Md5InputKey.encode(encoding='utf-8')+ Random + RandNumberSalt)
                            crc_turn = str.upper((hex(crc)[2:])).encode(encoding='utf-8')
                            if len(crc_turn) != 8:
                                n = len(crc_turn)
                                print("len(crc_turn)=",n)
                                for i in range(8- n):
                                    crc_turn = "0".encode(encoding='utf-8')+crc_turn
                            print("Crc32Value=",crc_turn)
                            PassWord = TEA.encrypt(crc_turn,PublicKey)
                            HexShow("tea(crc32)=",PassWord)
                            msg = struct.pack('<BB',len(PassWord)+1,0x01)+PassWord
                            HexShow("Open Msg CMD",msg)
                            if(data[0:9] == "CLOS DOOR"):
                                CMD = 0
                            else:
                                CMD = 1
                            sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 1, CMD))#cmd 0 unlock
                        break
                    else:
                        sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 0, 0))
                        break
                elif delay < 12:#  timeout = 6s
                    time.sleep(0.5)
                    delay = delay + 1
                    print("Waiting:%d..."%delay)
                    continue
                else:
                    print("Open Door TimeOut!")
                    break
        elif data[0:8] == "SET DOOR":#SET DOOR123456
            HexShow("input =",data[8:].encode(encoding='utf-8'))
            MD5 = hashlib.md5()
            MD5.update(data[8:].encode(encoding='utf-8')+ PassWordSalt)
            md5hex = (MD5.hexdigest())[0:32:4]
            print(str.upper(md5hex))
            setWord = TEA.encrypt(str.upper(md5hex).encode(encoding='utf-8'),PublicKey)
            HexShow('SetWord=',setWord)
            msg = struct.pack('<HBBB',0x0001,0x00,0x02,len(setWord)) + setWord#userID 2bytes + userStatus 1byte + userKeyType 1byte + userKeyLenth 1byte
            sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 1, 0x05))  # cmd = 5 ,set password
        elif data[0:9] == "SET LOCAL":#SET LOCAL234567
            HexShow("input =",data[9:].encode(encoding='utf-8'))
            msg = struct.pack('<H',0x0040)
            HexShow("msg= ",msg)
            #read the Random data
            sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 0, 0))
            delay = 0
            while True:
                if not MsgQue.empty():
                    rxdata = MsgQue.get()
                    if rxdata[0] == StatusSuccess:#status
                        print("Success")
                        if rxdata[1]== 0x08:# must be 8
                            print("lenth Success")
                            Random = TEA.decrypt(rxdata[2:10],PublicKey)
                            print("Random =",Random)
                            print("UserINputKeyWords=",data[9:])
                            setWord = TEA.encrypt(data[9:].encode(encoding='utf-8')+Random[0:8:4], PublicKey)
                            setWord = setWord + struct.pack('>BIBII', 0x1C,0x20171129, 0x7F, 0x55090100,0x55183000 )  # local pass word format :Cbitmsps + DateEnd + WeekBitMaps + DayTimeStart + DayTimeEnd
                            #setWord = setWord + struct.pack('>BIBII', 0x00, 0x20171129, 0x00, 0x00000000,0x00000000)  # local pass word format :Cbitmsps + DateEnd + WeekBitMaps + DayTimeStart + DayTimeEnd
                            HexShow('SetWord=', setWord)
                            msg = struct.pack('<HBBB', 150, 0x00, 0x00, len(setWord)) + setWord  # userID 2bytes + userStatus 1byte + userKeyType 1byte + userKeyLenth 1byte
                            sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 1, 0x05))  # cmd = 5 ,set password
                        break
        elif data[0:9] == "DEL LOCAL":#DEL LOCAL1
            if len(data) > 9:
                msg = struct.pack('<H',151)
            else:
                msg = struct.pack('<H',150) # UserID
            sendQueue.put(PackSendData(msg, 0x01, ClusterDoorLock, 1, 0x07))  # cmd = 7 ,ClearPinCode
        elif data[0:4] == "TIME":
            msg = struct.pack('<HBI',0x0000, 0xE2, int(time.time()))
            sendQueue.put(PackSendData(msg, 0x01, 0x000A, 0, 0x02))  # cmd = 2 ,write
        else:
            print("format erro")
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
    RxStatus = START_L_STATE
    LenToken = 0
    LenTemp = 0
    while True:
        while s.inWaiting() == 0:
            pass
        byte = s.read(1)
        if RxStatus == START_L_STATE:
            if byte[0] == 0x5B:
                RxStatus = START_H_STATE
                string = byte
        elif RxStatus == START_H_STATE:
            if byte[0] == 0xB5:
                RxStatus = LEN_L_STATE
                string += byte
            else:
                RxStatus = START_L_STATE
        elif RxStatus == LEN_L_STATE:
            if byte[0] < 128:
                LenToken = byte[0]
                LenTemp = 0
                RxStatus = LEN_H_STATE
                string += byte
            else:
                RxStatus = START_L_STATE
        elif RxStatus == LEN_H_STATE:
            if byte[0] == 0x00:
                RxStatus = DATA_STATE
                string += byte
                LenTemp = 4
            else:
                RxStatus = START_L_STATE
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
                RxStatus = START_L_STATE
                workQueue.put(string)# send the data to
        else:
            RxStatus = START_L_STATE
	#	queueLock.acquire()
	#	workQueue.put(rxdata)
    #    queueLock.release()

def PackSendData( SendMsg, endpoint, cluster, headControl, Cmd):
	SendMsg = struct.pack('<BBB', Send_SN, TyHeader, ProtocolType) + IEEE64 + struct.pack('<BHBB', endpoint, cluster, headControl, Cmd )+SendMsg
	Send_Lenth = len(SendMsg) + 6 # 6 = start_2bytes + lenth_2bytes + crc16_2bytes
	SendMsg =  struct.pack('<H',0xB55B) + struct.pack('<H',Send_Lenth) + SendMsg #add start lenth
	SendMsg = SendMsg + struct.pack('<H', cal_crc16(SendMsg, len(SendMsg))) # add crc
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

#crc16 calculate
def cal_crc16(puchMsg,crc_count):
	xorCRC = 0xA001
	CRC = 0xFFFF
	for i in range(crc_count):
		CRC ^= puchMsg[i]
		for j in range(8):
			XORResult = CRC & 0x01
			CRC >>= 1
			if (XORResult & 0xFF):
				CRC ^= xorCRC
	return CRC
###++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++###
Comnumb = 'com12'
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
Inthrd =  myThread(3,'inputTxThread',userInputQueue)
Inthrd.start()
#主体
#s.write(b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
time.sleep(0.2)
while (1) :

    #print(type(rx_string))
    if not workQueue.empty():
        rx_string = workQueue.get()
    else:
        continue
    print("\n")

    HexShow( "UartRxMsg",rx_string )
    if (len(rx_string) >= 14) and ((rx_string[len(rx_string)-1]*256 + rx_string[len(rx_string)-2]) == cal_crc16(rx_string,len(rx_string)-2)):# 2 = (SN + W_CMD + SIZE -CRC16)
        print("CHECK MSG SUCCESS !")
        #IEEE64 = rx_string[7:16]
        cluster = struct.unpack('<H',rx_string[17:19])[0]
        fc_type = struct.unpack('<B',rx_string[19:20])[0]
        Inputcmd = struct.unpack('<B',rx_string[20:21])[0]
        atrrCmd = struct.unpack('<H',rx_string[21:23])[0]# atrrCmd is tuple
        #print(atrrCmd)
    else:
        print("handshake FAILED	 ! ack_numb = %d"%len(rx_string))
        HexShow("erro",rx_string)
        s.flushInput()
        continue
    if (fc_type&0x03) is 0x00:
        print("fc_type:%02X"%fc_type)
        print("cluster:%04X"%cluster)
        if cluster == 0x0101:
            if Inputcmd == 0x01:#read responce
                print("Inputcmd:%02X" % Inputcmd)
                if atrrCmd is 0x0040:
                    print("atrrCmd:%04X" % atrrCmd)
                    userInputQueue.put(rx_string[23:])
                    HexShow("Send Msg to UserInput Threading",rx_string[23:])
            if Inputcmd == 0x0B:# Secific cmd rsp
                print("SecificCMD: ",hex(rx_string[21])," RSP Status %02X"%rx_string[22] )
                if rx_string[22] == StatusSuccess:
                    print("\rSUCCESS<<<------")
                else:
                    print("\rFAILURE<<<------")
        else:
            print("Others Cluster")

# else:


print('\nLoading success and jump to application...')
print('bin file has been closed !')
#s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
s.close()
input('Press Enter Key Exit~')
Rxthrd.join()
Txthrd.join()
Inthrd.join()