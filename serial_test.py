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

START_L_STATE = 0
START_H_STATE = 1
LEN_L_STATE = 2
LEN_H_STATE = 3
DATA_STATE = 4
def MyTxThread():
	#print('第',i,'次读取')
	i = 0
	RxStatus= START_L_STATE
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
			if byte[0] <128:
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
			LenTemp +=1 
			
			n = s.inWaiting()
			if n <= (LenToken - LenTemp):
				string += s.read(n)
				LenTemp += n
			else:
				string += s.read(LenToken - LenTemp)
				LenTemp += (LenToken - LenTemp)
			
			if LenTemp == LenToken:
				RxStatus = START_L_STATE
				i = i+1
				print("i= ",i)
				HexShow("\rReceiveBytes:",string)# display the data received returning the last line.
		else:
			RxStatus = START_L_STATE
				

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
	
Comnumb = 'com17'
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
string = ' '
#s.setTimeout(0)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()
OPEN_MSG="5B B5 17 00 00 B8 01 08 78 82 BB 0D 00 4B 12 00 01 06 00 01 01 93 00"
CLOSE_MSG="5B B5 17 00 00 B8 01 08 78 82 BB 0D 00 4B 12 00 01 06 00 01 00 52 C0"
n = 0
while True:
	#InputMsg = input('Input cluster:\n')
	#SendBytes = bytes.fromhex(InputMsg)
	#endpoint, cluster, headControl, Cmd = struct.unpack('<BHBB', SendBytes[0:5])
	#s.write( PackSendData(SendBytes[5:], endpoint, cluster, headControl, Cmd))
	if n < 10:
		n = n+1
		s.write(bytes.fromhex(OPEN_MSG))
		print("Send: OPEN,  ",n)
		time.sleep(0.05)
		s.write(bytes.fromhex(CLOSE_MSG))
		n= n + 1
		print("Send: CLOSE, ",n )
		time.sleep(0.05)
s.close()
thrd.join()
