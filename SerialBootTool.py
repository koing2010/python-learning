import serial
#from serial import win32
import time
import threading
import os
import struct
import sys
# dfine every command of 
ReadCmd=0x01
ReadRspCmd=0x02
WriteCmd=0x03
WriteRspCmd=0x04
JumpCmd = 0x05
DefaultRspCmd = 0x06
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
		hhex = '0x%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print('ReceiveBytes:',hex_string,'	total:',hLen)

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
s.setTimeout(2)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()# start threading
			
#主体
#s.write(b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
time.sleep(0.2)
path_str = os.path.abspath('.')
path_str += '/testbin/MultiuTools.bin'
file_t = open(path_str,'rb')#'rb' read bin format
bin_size = os.path.getsize(path_str);#get size of this 
if bin_size > (256-20)*1024: # 256K(total flash) -20K(boot sector)
	print("Bin file size is out of size allowed! Please recheck~~")
else:
# send handshake command:  
# format :          StatCode + Send_SN + OperateCmd + Attribution + PayloadLenth + PayloadData + CRC16
# frame size:       2bytes   + 2Byte   + 1byte      + 1byte       + 1byte        + nbytes      + 2Bytes
#Description:       PayloadLenth = n_bytes + 2_bytes_CRC16 
	Send_SN = 1 
	for handshake_time_retry in range(3):
		#send total size of bin file
		tx_forme = struct.pack('<H',Send_SN) + struct.pack('<BBB',WriteCmd,FileSizeAtrr ,6) + struct.pack('<I', int(bin_size))# H 2bytes,B 1byte,I 4bytes
		tx_string = struct.pack('<H',0xAAAA) + tx_forme + struct.pack('<H',cal_crc16(tx_forme,len(tx_forme)))
		s.write(tx_string)
		#wait ack of handshake
		while s.inWaiting() == 0:#wait ack
			pass
		ack_numb = s.inWaiting()#read the numb of bytes received
		tx_string = s.read(2)
		tx_string = s.read(ack_numb - 2)
		
		if (ack_numb == 10) and (tx_string[2] is WriteRspCmd)and ((tx_string[7]*256 + tx_string[6]) == cal_crc16(tx_string,tx_string[4]+3)):# 2 = (SN + W_CMD + SIZE -CRC16)
			print("handshake SUCCESS !")
			HexShow(tx_string)
			break
		else:
			print((tx_string[7]*256 + tx_string[6]), cal_crc16(tx_string,tx_string[4]+3))
			print("handshake FAILED	 ! ack_numb = %d"%ack_numb)
			HexShow(tx_string)
#########################################
	offsetCount = 0x00000000
	for c in range(int(bin_size/32)+1):
		tx_string = file_t.read(32)
		tx_string = struct.pack('<I', offsetCount) + tx_string#start addrres of this frame of data
		offsetCount = offsetCount + len(tx_string)-4
		tx_forme = struct.pack('<H',Send_SN) + struct.pack('<BBB',WriteCmd,FileDataAtrr ,len(tx_string)+2)+tx_string# H 2bytes,B 1byte,I 4bytes
		tx_string = struct.pack('<H',0xAAAA) + tx_forme + struct.pack('<H',cal_crc16(tx_forme,len(tx_forme)))#low-endian
	#	tx_string += ord(chr(tx_crc&0xFF))
	#	tx_string[33] = (tx_crc>>8)&0xFF
		#print(hex())
		s.write(tx_string)#read 16 bytes and tx it
		while s.inWaiting() == 0:#wait ack
			pass
		#time.sleep(0.005)#delay 10ms
		numb = s.inWaiting()#read the numb of bytes received
		string = s.read(2) 
		string = s.read(numb-2) 
		if (numb == 10) and (string[2] is WriteRspCmd)and( (string[5] is StatusSuccess))and ((string[7]*256 + string[6]) == cal_crc16(string,string[4]+3)):# 2 = (SN + W_CMD +ATRR+ SIZE -CRC16)
		    #print('Loading... %d\r'%(c/bin_size*100),)
			sys.stdout.write("\rLoading... %.1f %%"%(c*32/bin_size*100))
			#HexShow(string)
		else:
			print((string[7]*256 + string[6]),cal_crc16(string,string[4]+3))
			print('Loading Failed  numb = %d'%numb)
			HexShow(string)
#JumpCmd
tx_forme = struct.pack('<H',Send_SN) + struct.pack('<BBB',JumpCmd,FileDataAtrr,len(tx_string)+2)+tx_string# H 2bytes,B 1byte,I 4bytes
tx_string = struct.pack('<H',0xAAAA) + tx_forme + struct.pack('<H',cal_crc16(tx_forme,len(tx_forme)))#low-endian
#	tx_string += ord(chr(tx_crc&0xFF))
#	tx_string[33] = (tx_crc>>8)&0xFF
#print(hex())
#HexShow(tx_string)
s.write(tx_string)#send mcu jump cmd
print('\nLoading success and jump to application...')
print('bin file has been closed !')
#s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
file_t.close()# close bin file

s.close()
input('Press Enter Key Exit~')
thrd.join()
