import serial
#from serial import win32
import time
import threading
import os
import struct
import sys
import queue
# define local file version
LocalFileVersion = 0x17071303
LocalManufacture = 0x585A #x5A\x48\x01\xD0
LocalImageType = 0x1003

# define every command of
Send_Lenth = 0x0001
Send_SN = 1
TyHeader = 0xB8
ProtocolType= 0x01
IEEE64 = (b'\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00')
EndPoint = 0x0E
ClusterOTA = 0x0019
HaHeader = 0x19 #type = 01 direction = 1 no_rsp = 1

#define the OTA type command
CmdImageNotify = 0x00
CmdQueryNextImageReq = 0x01
CmdQueryNextImageRsp = 0x02
CmdImageBlockReq =  0x03
CmdImagePageReq = 0x04
CmdImageBlockRsp = 0x05
CmdUpgradeEndReq = 0x06
CmdUpgradeEndRsp = 0x07

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
Comnumb = 'com3'
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

Rxthrd = myThread(1,'uartRxThread',workQueue)
Rxthrd.start()# start threading
Txthrd = myThread(2,'uartTxThread',sendQueue)
Txthrd.start()# start threading

#主体
#s.write(b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
time.sleep(0.2)
path_str = os.path.abspath('.')
path_str += '/zigbeebin/585A-1003-17071303.zigbee'
file_t = open(path_str,'rb')#'rb' read bin format
bin_size = os.path.getsize(path_str);#get size of this
if bin_size > (256-20)*1024: # 256K(total flash) -20K(boot sector)
	print("Bin file size is out of size allowed! Please recheck~~")
else:
# send handshake command:
# format :          StatCode + Send_SN + OperateCmd + Attribution + PayloadLenth + PayloadData + CRC16
# frame size:       2bytes   + 2Byte   + 1byte      + 1byte       + 1byte        + nbytes      + 2Bytes
#Description:       PayloadLenth = n_bytes + 2_bytes_CRC16

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
			atrrCmd = struct.unpack('<H',rx_string[21:23])# atrrCmd is tuple
			#print(atrrCmd)
		else:
			print("handshake FAILED	 ! ack_numb = %d"%len(rx_string))
			HexShow("erro",rx_string)
			s.flushInput()
			continue
		if(atrrCmd[0] == 0x00F3):# NextBlockReq
			b_offset = 25
			Manufacture, ImageType, FileVersion, FileOffset, MaxDataSize= struct.unpack('<HHIIB',rx_string[b_offset:b_offset+13])
			#send total size of bin file
			print("Manufacture=%X"%Manufacture,"ImageType=%X"%ImageType,"FileVersion=%X"%FileVersion,"FileOffset=%X"%FileOffset, "MaxDataSize=%X"%MaxDataSize)
			file_t.seek(FileOffset, 0)
			ImageDtaBytes = file_t.read(MaxDataSize)
			status = 0
			tx_forme =   struct.pack('<BHHIIB',status,Manufacture, ImageType, FileVersion, FileOffset, len(ImageDtaBytes)) + ImageDtaBytes # H 2bytes,B 1byte,I 4bytes

			tx_string = PackSendData(tx_forme, EndPoint, ClusterOTA, HaHeader,CmdImageBlockRsp) # add startCode  lenth and crc

			HexShow("ImageBlockRsp:", tx_string)
			#time.sleep(0.1)
			#s.write(tx_string)
			sendQueue.put(tx_string)
			continue
		if(atrrCmd[0] == 0x00F1):# NextImageReq
			b_offset = 29 # data offset
			devFileVersion = struct.unpack('<I',rx_string[b_offset:b_offset+4])
			HexShow("devIEEE64 =", IEEE64)
			print("devFileVersion= %X"%devFileVersion)# Device FileVersion now

			if(devFileVersion[0] > LocalFileVersion):#judge the FileVersion
				print("there is no higher version !!!")
				sendmsg = (b'\x01') # status of NextImageRsp
			else:
				sendmsg =(b'\x00')# Mannufacture and ImageType
				sendmsg = sendmsg + struct.pack('<HHI', LocalManufacture, LocalImageType, LocalFileVersion) + struct.pack('<I', bin_size)

			sendmsg = PackSendData(sendmsg,  EndPoint, ClusterOTA, HaHeader,CmdQueryNextImageRsp)
			s.flushOutput()
			HexShow("NextImageRsp",sendmsg)
			#s.write( sendmsg)
			sendQueue.put(sendmsg)
			print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
			StartTime = time.localtime(time.time())
			StartTimeSeconds = time.time()

			continue
		if(atrrCmd[0] == 0x00F6):# UpgradeEndRsp
			if(rx_string[24] is not 0x00):
				print("UpgradeEndRep: Failed")
				continue
			NowTime = 0  #
			UpgradTime = 1 ;#about 1 minute(UpgradeTime - NowTime) after ,the device will restart and upgrade
			sendmsg = struct.pack('<HHIII',LocalManufacture, LocalImageType, LocalFileVersion, NowTime , UpgradTime)
			sendmsg = PackSendData(sendmsg, EndPoint, ClusterOTA, HaHeader, CmdUpgradeEndRsp)
			HexShow("UpgradeEndRsp:",sendmsg)
			#s.write(sendmsg)
			sendQueue.put(sendmsg)
			print("\nUpgrade Ending")
			print(time.strftime('start %Y-%m-%d %H:%M:%S',StartTime))
			print(time.strftime('end %Y-%m-%d %H:%M:%S',time.localtime()))#how long is the duration
			print("This Upgrade Duration is %.2f Seconds"%(time.time() - StartTimeSeconds))
			continue

print('\nLoading success and jump to application...')
print('bin file has been closed !')
#s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
file_t.close()# close bin file

s.close()
input('Press Enter Key Exit~')
Rxthrd.join()
Txthrd.join()