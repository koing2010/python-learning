import serial
import time
import threading
def MyTxThread():
	x = 1
	circle = 0
	while x < 50:
		x = 1 + x
		print('%d'% x)
		time.sleep(0.5)
		
#Comnumb = 'com9'
Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,2400)
string = ' '
s.setTimeout(2)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()
for i in range(10000):
#	print('第',i,'次读取')
	while s.inWaiting() == 0:
		pass
	string = s.read(1)
	if chr(string[0]) == '\xaa':
#	time.sleep(0.1)
		while s.inWaiting() < 6:
			pass
		string += s.read(6)
	if i%10 == 0:
		print(string)
s.close()
thrd.join()
