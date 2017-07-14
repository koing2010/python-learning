import serial
import time
import threading
import struct
txmsg = ('\x5B\xB5\x19\x00\x78\xB8\x01\x08\x23\xB4\xEC\x11\x00\x4B\x12\x00\x01\x06\x00\x00')
# define every command of
Send_Lenth = 0x0001
Send_SN = 1
TyHeader = 0xB8
ProtocolType= 0x01
IEEE64 = (b'\x08\x7A\xB3\x6A\x07\x00\x4B\x12\x00')#(b'\x08\xA6\x1D\x48\x0D\x00\x4B\x12\x00')#(b'\x08\x23\xB4\xEC\x11\x00\x4B\x12\x00')
EndPoint = 0x0E
ClusterOTA = 0x0019
HaHeader = 0x00 #type = 01 direction = 1 no_rsp = 1

def MyTxThread():
	#print('第',i,'次读取')
	while 1:
		while s.inWaiting() == 0:
			time.sleep(0.1)
			pass
		time.sleep(0.01)
		n = s.inWaiting()
		string = s.read(n)
		#IEEE64 = string[7:16]
		HexShow("\r    ReceiveBytes",string)# display the data received returning the last line.
	#print(string)
		
def PackSendData( SendMsg, endpoint, cluster, headControl, Cmd):
	SendMsg = struct.pack('<BBB', Send_SN, TyHeader, ProtocolType) + IEEE64 + struct.pack('<BHBB', endpoint, cluster, headControl, Cmd )+SendMsg
	Send_Lenth = len(SendMsg) + 6 # 6 = start_2bytes + lenth_2bytes + crc16_2bytes
	SendMsg =  struct.pack('<H',0xB55B) + struct.pack('<H',Send_Lenth) + SendMsg #add start lenth
	SendMsg = SendMsg + struct.pack('<H', cal_crc16(SendMsg, len(SendMsg))) # add crc
	#HexShow("tx", SendMsg)
	return SendMsg		

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
string = ' '
#s.setTimeout(0)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()
while(1):
	InputMsg = input('Input cluster:\n')
	SendBytes = bytes.fromhex(InputMsg)
	endpoint, cluster, headControl, Cmd = struct.unpack('<BHBB', SendBytes[0:5])
	s.write( PackSendData(SendBytes[5:], endpoint, cluster, headControl, Cmd))
s.close()
thrd.join()
