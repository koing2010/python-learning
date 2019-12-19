import serial
import serial.tools.list_ports
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

PassWordSalt = '42D9BE8481B8DA5F21B24FD2859C08A8'.encode(encoding='utf-8')#'F9120481520D8202FA0A02DFDB575BA7'.encode(encoding='utf-8')
RandNumberSalt='95060092B8596746D6AABC2E8294036F'.encode(encoding='utf-8')#'A0FB8A2FD2352AF6432C481FCDD45CB2'.encode(encoding='utf-8')
PublicKey =  'F8370B9DB9D687C4'.encode(encoding='utf-8')# (b'\x38\x45\x42\x37\x30\x30\x39\x39\x30\x46\x45\x44\x30\x36\x31\x44')
# define every command of
Send_Lenth = 0x0001
Send_SN = 1
TyHeader = 0xB8
ProtocolType= 0x01
#IEEE64 = bytes.fromhex("08 72 82 BB 0D 00 4B 12 00")#(b'\x08\x7D\x7B\xB76B\x0D\x00\x4B\x12\x00')
IEEE64 = bytes.fromhex("0E D6 B5 0A 00 4B 12 00")

#save the device list authenticated00 12 4B 00 0A B5 D2 41"B2 42 D3 12 00 4B 12 00",00 12 4B 00 0D BB 96 50
DevListAuth =["72 D2 B5 0A 00 4B 12 00","89 84 BB 0D 00 4B 12 00","0E D6 B5 0A 00 4B 12 00"]

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
        elif self.threadID is 4:
            AutoSendThread(self.name, self.q)
        else:
            print("Thread Start ERRO!")
        print("Exiting " + self.name)

#define
def AutoSendThread(threadName, MsgQue):
        print(threadName + "start")
        while True:
            time.sleep(10)
            MsgQue.put("OPEN DOOR123456")
            #time.sleep(2.5)
            #userInputQueue.put("LOCK")
#user input
def inputTxThread(threadName,MsgQue):
    print(threadName + "start3")
    while True:
        while not AutoOpenQueue.empty():
            time.sleep(0.1)
            pass

        data = input('Please input CMD\n')#AutoOpenQueue.get()#input('Please input CMD')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        if (data[0:9] == "OPEN DOOR") or (data[0:9] == "CLOS DOOR") or (data[0:9] == "CHEK DOOR"):#OPEN DOOR123456
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
                            elif(data[0:9] == "CHEK DOOR"):
                                CMD = 2
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
                            setWord = setWord + struct.pack('>BIBII', 0x18,0x00000000, 0x7F, 0x55191000,0x55191500 )  # local pass word format :Cbitmsps + DateEnd + WeekBitMaps + DayTimeStart + DayTimeEnd
                            #setWord = setWord + struct.pack('>BIBII', 0x00, 0x20171129, 0x00, 0x00000000,0x00000000)  # local pass word format :Cbitmsps + DateEnd + WeekBq1itMaps + DayTimeStart + DayTimeEnd
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
        elif data[0:3] == "PMT":#permite join
            sendQueue.put( ModleMgmt.PackSendDataToModle( bytes.fromhex(data[3:]),0x0036, 0x01, 0x00 ) ) #
        elif data[0:2] == "DD":#Delete Device
            if len(bytes.fromhex(data[2:])) is 8:
                sendQueue.put(ModleMgmt.PackSendDataToModle(bytes.fromhex(data[2:]), 0x0034, 0x01, 0x00))
            else:
                print("DeleteDev: lenth of MAC erro\n")
        elif data[0:3] == "DIS":#Delete Device
            if len(bytes.fromhex(data[3:])) is 10:
                sendQueue.put(ModleMgmt.PackSendDataToModle(bytes.fromhex(data[3:]), 0x0042, 0x01, 0x00))
            else:
                print("DeleteDev: lenth of CMD erro\n")
        elif data[0:3] == "GDN":#get device
             sendQueue.put(ModleMgmt.PackSendDataToModle(bytes.fromhex("00"), 0x0040, 0x01, 0x00))
        elif data[0:3] == "GDL":#get device list allnumber
            for i in range( bytes.fromhex(data[3:5])[0]):
                sendQueue.put(ModleMgmt.PackSendDataToModle(struct.pack("B",i), 0x0041, 0x01, 0x00))
        elif data[0:2] == "RD":#Read
            if len(bytes.fromhex(data[2:])) is 4:
                msg = PackSendData(bytes.fromhex(data[6:]), 0x01, struct.unpack("H",bytes.fromhex(data[2:6]))[0], 0, 0)
                #HexShow("ReadCMd",msg)
                sendQueue.put(msg)
            else:
                print("Input Attr lent erro")
                print("e.g. read cluster 0x0000,attr0x0005.  Input:RD00000500")
        elif data[0:2] == "WR":#writte
            if len(bytes.fromhex(data[2:])) > 4:
                msg = PackSendData(bytes.fromhex(data[6:]), 0x01, struct.unpack("H",bytes.fromhex(data[2:6]))[0], 0x00, 2)
                #HexShow("ReadCMd",msg)
                sendQueue.put(msg)
            else:
                print("Input Attr lent erro")
        elif data[0:2] == "RL":#Setpoint Raise/Lower Command #

            # SendMsg, endpoint, cluster, headControl, Cmd
            msg = PackSendData(bytes.fromhex(data[2:]), 0x01,0x0201, 1, 0)
            sendQueue.put(msg)
        elif data[0:2] == "UP":#
            SendMsg = "00"
            msg = PackSendData(bytes.fromhex(SendMsg), 0x01, 0x0102, 1, 0)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)
        elif data[0:4] == "DOWN":
            SendMsg = "00"
            msg = PackSendData(bytes.fromhex(SendMsg), 0x01, 0x0102, 1, 1)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)
        elif data[0:4] == "STOP":
            SendMsg = "00"
            msg = PackSendData(bytes.fromhex(SendMsg), 0x01, 0x0102, 1, 2)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)
        elif data[0:2] == "ON":#
            SendMsg = ""
            msg = PackSendData(bytes.fromhex(SendMsg), 0x01, 0x0006, 1, 1)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)
        elif data[0:3] == "OFF":  #
            SendMsg = ""
            msg = PackSendData(bytes.fromhex(SendMsg), 0x01, 0x0006, 1, 0)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)
        elif data[0:4] == "MOVT":  #MOV to Color temperature 2bytes ColorTemperature +2bytes TransitionTime
            msg = PackSendData(bytes.fromhex(data[4:]), 0x01, 0x0300, 1, 0x0a)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)

        elif data[0:4] == "MOVL":  #move to level  : 1byte LEVEL + 2bytes TransitionTime
            msg = PackSendData(bytes.fromhex(data[4:]), 0x01, 0x0008, 1, 0x04)#( SendMsg, endpoint, cluster, headControl, Cmd)
            # HexShow("ReadCMd",msg)
            sendQueue.put(msg)
        elif data[0:3] == "PDL": # push device list
            # total size and crc16
            MbusCrc16 = 0xFFFF
            devlistSize = len(DevListAuth)
            for i in range(devlistSize):
                buf = bytes.fromhex(DevListAuth[i])
                MbusCrc16 = crclib.cal_file_crc16(buf, len(buf), MbusCrc16)
            print("ListSize= %d" % devlistSize, "CRC16= 0x%04X" % MbusCrc16)
            sendQueue.put(ModleMgmt.PackSendDataToModle(struct.pack("<BH", devlistSize, MbusCrc16), 0x0042, 0x01, 0x0A))
        else:
            print("format erro")
# usart tx data
def txdata(threadName, q):
	print(threadName + "start")
	while (1):
		while not sendQueue.empty():
			txda = sendQueue.get()
			s.write(txda)
			HexShow("txthread:",txda)
			time.sleep(0.05)
#usart rx data
def process_data(threadName, q):
    print(threadName + "start")
    RxStatus = START_L_STATE
    LenToken = 0
    LenTemp = 0
    while True:
        while s.inWaiting() == 0:
            time.sleep(0.1)
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
	SendMsg = struct.pack('<BBBB', Send_SN, TyHeader, ProtocolType,len(IEEE64)) + IEEE64 + struct.pack('<BHBB', endpoint, cluster, headControl, Cmd )+SendMsg
	Send_Lenth = len(SendMsg) + 6 # 6 = start_2bytes + lenth_2bytes + crc16_2bytes
	SendMsg =  struct.pack('<H',0xB55B) + struct.pack('<H',Send_Lenth) + SendMsg #add start lenth
	SendMsg = SendMsg + struct.pack('<H', crclib.cal_crc16(SendMsg, len(SendMsg))) # add crc
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
#port_list = list(serial.tools.list_ports.comports())
#for port in port_list:
#    print(port[0])
#    Comnumb = port[0]
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial("com17",115200)
   # s.open()
    #print('Port must be configured before it can be used.')


string = ''

queueLock = threading.Lock()
workQueue = queue.Queue(maxsize = 10)
sendQueue = queue.Queue(maxsize = 10)
userInputQueue = queue.Queue(maxsize = 10)
AutoOpenQueue = queue.Queue(maxsize = 10)

Rxthrd = myThread(1,'uartRxThread',workQueue)
Rxthrd.start()# start threading
Txthrd = myThread(2,'uartTxThread',sendQueue)
Txthrd.start()# start threading
Inthrd =  myThread(3,'inputTxThread',userInputQueue)
Inthrd.start()
#Sendthrd = myThread(4,'AutoSendThread',AutoOpenQueue)s
#Sendthrd.start()
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

    HexShow( "UartRxMsg",rx_string[2:] )
    if (len(rx_string) >= 14) and ((rx_string[len(rx_string)-1]*256 + rx_string[len(rx_string)-2]) == crclib.cal_crc16(rx_string,len(rx_string)-2)):# 2 = (SN + W_CMD + SIZE -CRC16)
        print("CHECK MSG SUCCESS !")
        #IEEE64 = rx_string[7:16]
        if rx_string[5] is 0x20:
            print("ModelMsg In")
            cluster = struct.unpack('<H', rx_string[8:10])[0]
            if cluster == 0x0040:
                for i in range(rx_string[12]):#get every device 64bits addr
                    sendQueue.put(ModleMgmt.PackSendDataToModle(struct.pack("B", i), 0x0041, 0x01, 0x00))
            elif cluster == 0x0041:
                print("GetDevice[%d]"%rx_string[12])
                HexShow('\r',rx_string[13:21])
            continue
        if rx_string[5] is 0x30:# need response
            print("ModelMsg In and Need Rsp")
            cluster = struct.unpack('<H', rx_string[8:10])[0]
            if cluster == 0x0042:
                # total size and crc16
                MbusCrc16 = 0xFFFF
                devlistSize = len(DevListAuth)
                for i in range(devlistSize):
                    buf = bytes.fromhex(DevListAuth[i])
                    MbusCrc16 = crclib.cal_file_crc16(buf, len(buf), MbusCrc16)
                print("ListSize= %d"%devlistSize,"CRC16= 0x%04X"%MbusCrc16)
                sendQueue.put(ModleMgmt.PackSendDataToModle(struct.pack("<BH", devlistSize,MbusCrc16), 0x0042, 0x01, 0x01))
            if cluster == 0x0043:
                DevIndex = rx_string[12]
                msg = struct.pack("B", DevIndex) +  bytes.fromhex(DevListAuth[DevIndex])
                sendQueue.put( ModleMgmt.PackSendDataToModle( msg , 0x0043, 0x01, 0x01))
                print("Syc")


        else:
            cluster = struct.unpack('<H',rx_string[17:19])[0]
            fc_type = struct.unpack('<B',rx_string[19:20])[0]
            Inputcmd = struct.unpack('<B',rx_string[20:21])[0]
            atrrCmd = struct.unpack('<H',rx_string[21:23])[0]# atrrCmd is tuple

            if (fc_type & 0x03) is 0x00:
                print("EndPoint:%02X" % rx_string[16])
                print("fc_type:%02X" % fc_type)
                print("cluster:%04X" % cluster)
                if cluster == 0x0101:
                    if Inputcmd == 0x01:  # read responce
                        print("Inputcmd:%02X" % Inputcmd)
                        if atrrCmd is 0x0040:
                            print("atrrCmd:%04X" % atrrCmd)
                            userInputQueue.put(rx_string[23:])
                            HexShow("Send Msg to UserInput Threading", rx_string[23:])
                    if Inputcmd == 0x0B:  # Secific cmd rsp

                        print("SecificCMD: ", hex(rx_string[21]), " RSP Status %02X" % rx_string[22])
                        if rx_string[22] == StatusSuccess:
                            print("\rSUCCESS<<<------")
                        else:
                            print("\rFAILURE<<<------")
                elif cluster == 0x0000:  # basic cluster
                    if Inputcmd == 0x01 and rx_string[23] == 0x00:  # read responce
                        print("Inputcmd:%02X" % Inputcmd)
                        print("%d" % rx_string[24])
                        print(rx_string[25:25 + rx_string[24]])
                        print("%d" % rx_string[25 + 3 + rx_string[24]])
                        print(rx_string[25 + 4 + rx_string[24]:])
                elif cluster == 0x000A:  # time cluster
                    if Inputcmd == 0x00 and atrrCmd == 0x0000:
                        print("TimeSychronize");
                        msg = struct.pack("<HBBI", 0x0000, 0x00, 0xE2,
                                          int(time.time()))  # Formate of ReadRsp: Att + status + valueType + Payload
                        msg = PackSendData(msg, 0x01, 0x000A, 0x00, 1)
                        # HexShow("ReadCMd",msg)
                        sendQueue.put(msg)

                elif cluster == 0x0B04:
                    if Inputcmd == 0x01 and rx_string[23] == 0x00:  # read responce and status
                        print("ReadRspcmd:%02X" % Inputcmd)
                        print("AttrID:%04X" % atrrCmd)
                        if atrrCmd == 0x0505:
                            print("RMSVoltage = %d V" % struct.unpack('<H', rx_string[25:27])[0])
                        if atrrCmd == 0x0508:
                            print("RMSCurrent = %.3f A" % (struct.unpack('<H', rx_string[25:27])[0] / 1000))
                        if atrrCmd == 0x050B:
                            print("ActivePower = %d W" % struct.unpack('<H', rx_string[25:27])[0])
                        if atrrCmd == 0x0510:
                            print("PowerFactor = %.2f " % (struct.unpack('B', rx_string[25:26])[0] / 100))
                elif cluster == 0x0201:  # Thermostat
                    if Inputcmd == 0x01:  # Read Rsp
                        if atrrCmd == 0x0000:
                            print("LoacalTemperatureAttr: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))
                        if atrrCmd == 0x0003:
                            print("AbsMinHeatSetpointLimit: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))
                        if atrrCmd == 0x0004:
                            print("AbsMaxHeatSetpointLimit: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))
                        if atrrCmd == 0x0005:
                            print("AbsMinCoolSetpointLimit: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))
                        if atrrCmd == 0x0006:
                            print("AbsMaxCoolSetpointLimit: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))
                        if atrrCmd == 0x0007:
                            print("PICoolingDemand: %" % (struct.unpack('B', rx_string[25:26])[0]))
                        if atrrCmd == 0x0010:
                            print("LocalTemperature Calibration: %d" % (struct.unpack('B', rx_string[25:26])[0]))
                        if atrrCmd == 0x0011:
                            print("OccupiedCoolingSetpoint: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))
                        if atrrCmd == 0x0012:
                            print("OccupiedHeatingSetPoint: %.2f ℃" % (struct.unpack('H', rx_string[25:27])[0] / 100))

                    elif Inputcmd == 0x0A:  # Report
                        if atrrCmd == 0x0000:
                            print("Report LoacalTemperatureAttr: %.2f ℃" % (
                            struct.unpack('H', rx_string[24:26])[0] / 100))
                elif cluster == 0x0202:  # Thermostat
                    print(" FanControlCluster", end='')
                    if atrrCmd == 0x0000:
                        if Inputcmd == 0x0A:
                            print("Reoprt FanMode: %d" % rx_string[24])
                elif cluster == 0x0300:
                    print(" ColorTemperatureCluster", end='')
                    if Inputcmd == 0x0A:
                        if atrrCmd == 0x0007:
                            print("Value : %d" % (rx_string[24] + rx_string[25] * 255))
                elif cluster == 0x0008:
                    print(" LEVELCluster", end='')
                    if Inputcmd == 0x0A:
                        if atrrCmd == 0x0000:
                            print("Value : %d" % rx_string[24])
                elif cluster == 0x0702:
                    print("ReadRspcmd:%02X" % Inputcmd)
                    print("AttrID:%04X" % atrrCmd)
                    if atrrCmd == 0x0000:
                        print("CurrentSumDelivered = %.3f KWh" % (struct.unpack('<L', rx_string[25:29])[0] / 1000))
                else:
                    print("Unkown Cluster")

                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        #print(atrrCmd)
    else:
        print("handshake FAILED	 ! ack_numb = %d"%len(rx_string))
        HexShow("erro",rx_string)
        s.flushInput()
        continue


# else:


print('\nLoading success and jump to application...')
print('bin file has been closed !')
#s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
s.close
input('Press Enter Key Exit~')
Rxthrd.join()
Txthrd.join()
Inthrd.join()