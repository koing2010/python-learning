import serial
#from serial import win32
import time
import threading
import os
import struct
import sys
# dfine every command of 
Send_Lenth = 0x0001
Send_SN = 1
TyHeader = 0xB8
ProtocolType= 0x01
IEEE64 = (b'\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00')
EndPoint = 0x0E
Cluster = 0x0019
HaHeader = 0x09

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
	print('threading has gone !')


#display hex string		
def HexShow(i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print(hex_string,'	total:',hLen)

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
Comnumb = 'com5'
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
if s._port is None:
	print('Port must be configured before it can be used.')
	while True:
		pass
		
string = ''
s.setTimeout(2)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()# start threading
			
#主体
#s.write(b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
time.sleep(0.2)
path_str = os.path.abspath('.')
path_str += '/zigbeebin/5678-1234-0000ABCF.zigbee'
file_t = open(path_str,'rb')#'rb' read bin format
bin_size = os.path.getsize(path_str);#get size of this 
if bin_size > (256-20)*1024: # 256K(total flash) -20K(boot sector)
	print("Bin file size is out of size allowed! Please recheck~~")
else:
# send handshake command:  
# format :          StatCode + Send_SN + OperateCmd + Attribution + PayloadLenth + PayloadData + CRC16
# frame size:       2bytes   + 2Byte   + 1byte      + 1byte       + 1byte        + nbytes      + 2Bytes
#Description:       PayloadLenth = n_bytes + 2_bytes_CRC16 

	for handshake_time_retry in range(3):
			#wait ack of handshake
		while s.inWaiting() == 0:#wait ack
			pass
		time.sleep(0.01)
		ack_numb = s.inWaiting()#read the numb of bytes received
		tx_string = s.read(ack_numb)
		#print(type(tx_string))
		HexShow(tx_string)
		if (ack_numb >= 14) and ((tx_string[ack_numb-1]*256 + tx_string[ack_numb-2]) == cal_crc16(tx_string,ack_numb-2)):# 2 = (SN + W_CMD + SIZE -CRC16)
			print("handshake SUCCESS !")
			
			atrrCmd = struct.unpack('<H',tx_string[21:23])# atrrCmd is tuple
			print(atrrCmd)
		else:
			print("handshake FAILED	 ! ack_numb = %d"%ack_numb)
			HexShow(tx_string)
			break
		if(atrrCmd[0] == 0x00F3):
			b_offset = 25
			Manufacture, ImageType, FileVersion, FileOffset, MaxDataSize= struct.unpack('<HHIIB',tx_string[b_offset:b_offset+13])#tx_string[b_offset+2:b_offset+4],tx_string[b_offset+4:b_offset+8],tx_string[b_offset+8:b_offset+12])
			#send total size of bin file
			print("Manufacture=%X"%Manufacture,"ImageType=%X"%ImageType,"FileVersion=%X"%FileVersion,"FileOffset=%X"%FileOffset, "MaxDataSize=%X"%MaxDataSize)
			file_t.seek(FileOffset, 0)
			ImageDtaBytes = file_t.read(MaxDataSize)
			status = 0
			tx_forme =  struct.pack('<BBB', Send_SN, TyHeader, ProtocolType) + IEEE64 + struct.pack('<BHBB',EndPoint, Cluster, HaHeader,CmdImageBlockRsp )+ struct.pack('<BHHIIB',status,Manufacture, ImageType, FileVersion, FileOffset, len(ImageDtaBytes)) + ImageDtaBytes # H 2bytes,B 1byte,I 4bytes

			Send_Lenth = len(tx_forme) + 6;# 6 = start_2bytes + lenth_2bytes + crc16_2bytes
			tx_string = struct.pack('<H',0x5BB5) + struct.pack('<H',Send_Lenth) + tx_forme
			tx_string =tx_string + struct.pack('<H',cal_crc16(tx_string,len(tx_string)))
			print("ImageBlockRsp:")
			HexShow(tx_string)
			s.write(tx_string)
			continue
		if(atrrCmd[0] == 0x00F1):
			sendmsg =(b'\x5B\xB5\x24\x00\x78\xB8\x01\x08\x7D\x7B\xBB\x0D\x00\x4B\x12\x00\x0E\x19\x00\x09\x02\x00\x78\x56\x34\x12\xCF\xAB\x00\x00\xEC\xE3\x02\x00\xD8\xCE')
			#sendmsg = bytes.fromhex(sendmsg)
			#print(type(sendmsg))
			s.flushOutput()
			w_num = s.write(sendmsg)
			print(w_num)
			continue

print('\nLoading success and jump to application...')
print('bin file has been closed !')
#s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
file_t.close()# close bin file

s.close()
input('Press Enter Key Exit~')
thrd.join()
