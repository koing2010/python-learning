import serial
import time
from multiprocessing import Process
import os
def MyTxProcess(name):
	x = 1
	print(x)
	circle = 0
	while x < 50:
		x = 1 + x
		buf = input('no.'% x)
		time.sleep(0.5)
		
if __name__=='__main__':
	s = serial.Serial('com9',9600)
	string = ' '
	pro = Process(target=MyTxProcess,args=('seria',))
	pro.start()
	for i in range(100):
		print('第',i,'次读取')
		while s.inWaiting() == 0:
			pass
		time.sleep(0.5)
		n = s.inWaiting()
		string = s.read(n)
		s.write(string)
		print(string)
	s.close()#关闭串口
	time.sleep(0.1)
	pro.join()
