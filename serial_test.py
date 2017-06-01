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
s = serial.Serial(Comnumb,115200)
string = ' '
s.setTimeout(0)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()
for i in range(1000):
	print('第',i,'次读取')
	while s.inWaiting() == 0:
		pass
	time.sleep(0.5)
	n = s.inWaiting()
	string = s.read(n)
	s.write(string)
	print(string)
s.close()
thrd.join()
