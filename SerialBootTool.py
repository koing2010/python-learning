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
Comnumb = 'com10'
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
if bin_size > (256-20)*1024/32: # 256K(total flash) -20K(boot sector)
	print("Bin file size is out of size allowed! Please recheck~~")
else:
# send handshake command
	for handshake_time_retry in range(3):
		handshake_str = b'\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A'
	for c in range(int(bin_size)+1):
		print('第',c,'次读取')
		tx_string = file_t.read(32)
		tx_crc = cal_crc16(tx_string, 32)
		
		tx_tytes = struct.pack('<H',tx_crc)#low-endian
		tx_string += tx_tytes
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
