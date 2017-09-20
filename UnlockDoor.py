import serial
#from serial import win32
import time
import threading
import os
import struct
import sys
import queue
#import lisencegyen


# define every command of
Send_Lenth = 0x0001
Send_SN = 1
TyHeader = 0xB8
ProtocolType= 0x01
IEEE64 = bytes.fromhex("41 82 BB 0D 00 4B 12 00")#(b'\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00')
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

def MyTxThread():
	time.sleep(20)
	print('Waiting!')

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
        else:
           txdata(self.name, self.q)
        print("Exiting " + self.name)
#user input
def inputTxThread(threadName,q):
    print(threadName + "start3")
    while True:
        data = input('Please input CMD')
        if data[0:9] is "OPEN DOOR":
            bytesData = bytes.fromhex(data[9:])
            msg = struct.pack('<H',0x0040)
            HexShow("msg= ",msg)
            #
            workQueue.put(PackSendData( msg,0x01,ClusterDoorLock,0,0))
            delay = 0
            while True:
                if not q.empty():
                    data = q.get()
                    print(data)

                elif delay > 12:#  timeout = 6s
                    time.sleep(0.5)
                    delay = delay + 1;

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
	rxdata  = (b'')
	while (1):
		#wait ack of handshake
		while s.inWaiting() == 0:#wait ack
			pass
		time.sleep(0.008)
		ack_numb = s.inWaiting()#read the numb of bytes received
		rxdata =rxdata + s.read(ack_numb)
		while (1):
			if(rxdata[0] is 0x5B) and (rxdata[1] is 0xB5):
				templen = len(rxdata)
				if templen >= 4:
					frame_lenth =  rxdata[2] + rxdata[3]*256
					if frame_lenth <= templen:
						workQueue.put(rxdata[0:frame_lenth])
						#print("more")
						rxdata = rxdata[frame_lenth:templen]
					else:
						time.sleep(0.005)
						ack_numb = s.inWaiting()  # read the numb of bytes received
						if(frame_lenth - templen) <= ack_numb:
							rxdata = rxdata + s.read(frame_lenth - templen)
							workQueue.put(rxdata)
							rxdata = (b'')
						else:#timeout
							rxdata = (b'')
					break
			else:
				for i in range(len(rxdata)):
					if rxdata[i] is 0xFE:
						rxdata = rxdata[i:len(rxdata)]
						break #break the for loop
					else:
						continue
				rxdata = (b'')
				break;#while
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
Comnumb = 'com8'
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
userInputQueue = queue.Queue(maxsize = 2)

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
        IEEE64 = rx_string[7:16]
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
        if cluster is ClusterDoorLock:
            if Inputcmd is 0x01:#read responce
                if atrrCmd is 0x0040:
                    userInputQueue.put(rx_string[23:])

# else:


print('\nLoading success and jump to application...')
print('bin file has been closed !')
#s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
s.close()
input('Press Enter Key Exit~')
Rxthrd.join()
Txthrd.join()
Inthrd.join()