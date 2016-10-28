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
	
	
#Comnumb = 'com4'
Comnumb=input('输入串口号(如com4):')
s = serial.Serial(Comnumb,9600)
string = ' '
s.setTimeout(2)
#thrd = threading.Thread(target=MyTxThread,name='koing2010')
#thrd.start()
for i in range(10000):
#	print('第',i,'次读取')
	while s.inWaiting() == 0:#wait ack
		pass
	time.sleep(0.1)#delay 10ms
	numb = s.inWaiting()#read the numb of bytes received
	string = s.read(numb)
	if (numb == 18)&(string[3] == 0x0e):
		HexShow(string)
		if string[9]&0x01 :#bit0
			print("Open")
		else:
			print("Close")
		if string[9]&0x02 :#bit1
			print("负离子 Open")
		else:
			print("负离子 Close")
		if string[9]&0x04 :#bit2
			print("紫外灯 Open")
		else:
			print("紫外灯 Close")
		if string[9]&0x08 :#bit3
			print("Auto Open")
		else:
			print("Auto Close")
		if string[9]&0x10 :#bit4
			print("Sleep Open")
		else:
			print("Sleep Close")
		print("fan level=",string[10],"    timer=",string[11],'hours')
		if string[12] == 0:
			print("filter element = OK")
		else:
			print("filter element = FALSE")
		print("temperature=",string[13]-10,'℃',"    humidity=",string[14],"%","    PM2.5=",string[15]*256+string[16])
s.close()
#thrd.join()
