import serial
import time
import threading
def MyTxThread():
	x = 1
	circle = 0
	while x < 50:
		x = 1 + x
		print('')
		time.sleep(0.5)
		
s = serial.Serial('com9',9600)
string = ' '
s.setTimeout(2)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()
for i in range(100):
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
