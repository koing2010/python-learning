import serial
#from serial import win32
import time
import threading
import os
import struct
def MyTxThread():
	time.sleep(10)
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
	print('ReceiveBytes:',hex_string,'  total:',hLen)

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
path_str += '/testbin/MultiuTools.bin'
file_t = open(path_str,'rb')#'rb' read bin format
bin_size = os.path.getsize(path_str)/32;#get size of this 
if bin_size > (256-20)*1024: # 256K(total flash) -20K(boot sector)
	print("Bin file size is out of size allowed! Please recheck~~")
else:
# send handshake command:  
# 2Byte start code AA AA  + 2Bytes code SN + 1byte lenth of frame except start code + nbytes datas +2bytes crc16
# the frame size  = 2bytes + 2Byte + 1byte + 2bytes + nbytes
	Send_SN = 1 
	for handshake_time_retry in range(3):
		#send total size of bin file
		tx_forme = struct.pack('<H',Send_SN) + struct.pack('<B',4) + struct.pack('<I', int(bin_size))# H 2bytes,B 1byte,I 4bytes
		tx_string = struct.pack('<H',0xAAAA) + tx_forme +   struct.pack('<H',cal_crc16(tx_forme,7))
		s.write(tx_string)
		#wait ack of handshake
		while s.inWaiting() == 0:#wait ack
			pass
		ack_numb = s.inWaiting()#read the numb of bytes received
		tx_string = s.read(2)
		tx_string = s.read(ack_numb - 2)
		
		if (ack_numb == 11) and ((tx_string[8]*256 + tx_string[7]) == cal_crc16(tx_string,tx_string[2]+3)):
			print("handshake SUCCESS !")
			HexShow(tx_string)
			break
		else:
			print("handshake FAILED  ! ack_numb = %d"%ack_numb)
			HexShow(tx_string)
	for c in range(int(bin_size)+1):
		print('第',c,'次读取')
		tx_string = file_t.read(32)
		tx_crc = cal_crc16(tx_string, 32)
		
		tx_string += struct.pack('<H',tx_crc)#low-endian
	#	tx_string += ord(chr(tx_crc&0xFF))
	#	tx_string[33] = (tx_crc>>8)&0xFF
		#print(hex())
		s.write(tx_string)#read 16 bytes and tx it
		while s.inWaiting() == 0:#wait ack
			pass
		time.sleep(0.01)#delay 10ms
		numb = s.inWaiting()#read the numb of bytes received
		string = s.read(numb)
		HexShow(string)
#	s.write(string)
#	s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
file_t.close()# close bin file
print('bin file has been closed !')
s.close()
input('Enter Key')
thrd.join()
