import serial
import time
import threading
import sys
def MyTxThread():
	x = 1
	circle = 0
	while x < 50:
		x = 1 + x
		print('%d'% x)
		time.sleep(1.5)
		
def HexShow(i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		print('str',i,i_string[i])
		hvol = ord(i_string[i])
		hhex = '0x%02X' % (hvol)
		hex_string += hhex + ' '
	print('checkHex: %i_string' % (hex_string))
	
	
#Comnumb = 'com9'
Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
if s._port is None:
	print('Port must be configured before it can be used.')
	while True:
		pass
		
string = ''
s.setTimeout(2)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()
		
		
#主体
for c in range(100):
	print('第',c,'次读取')
	while s.inWaiting() == 0:
		pass
	time.sleep(0.5)
	n = s.inWaiting()
	string = s.read(n)
	HexShow(string)
#	s.write(string)
#	s.write('\x5A\xA5\x10\x01\x01\x00\x00\x00\x02\x02\x01\xA5\x5A')
	print(string)
s.close()
thrd.join()
