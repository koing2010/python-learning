import serial
#from serial import win32
import time
import threading
import os
def MyTxThread():
	time.sleep(10)
	print('threading has gone !')


#display hex string 	
def HexShow(str):
	hex_string = ''
	hLen = len(str)
	for i in range(hLen):
		hvol = str[i]
		hhex = '0x%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %str' % (hex_string))
	print('ReceiveBytes:',hex_string,'  total:',hLen)
	
###++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++###	
#Comnumb = 'com3'
Comnumb=input('输入串口号(如com9):')
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
for c in range(int(bin_size)+1):
	print('第',c,'次读取')
	s.write(file_t.read(32))#read 16 bytes and tx it
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
