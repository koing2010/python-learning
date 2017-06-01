import serial
import time
import threading
det_msg = (b'\x5A\xA5\x10\x01\x06\x00\x00\x00\x13\x01\x01\x01\xE3\xB5\x0A\x00\x4B\x12\x00\x01\x01\x01\x00\x00\x00\x00\x00\x40\xA5\x5A')
det_msg1 = (b'\x5A\xA5\x10\x01\x06\x00\x00\x00\x13\x01\x01\x0A\x82\xBB\x0D\x00\x4B\x12\x00\x01\xC0\x04\x00\x00\x00\x00\x00\x00\xA5\x5A')
def MyTxThread():
	x = 1
	circle = 0
	while x < 50:
		x = 1 + x
		# print('\n读取随机数%d'% x)
		# HexShow(det_msg)
		# time.sleep(5)
		# s.write(det_msg) 
		# time.sleep(5)
		# s.write(det_msg1) 
#display hex string 	
def HexShow(i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print('ReceiveBytes:',hex_string,'  total:',hLen)
	
	
Comnumb = 'com19'
#Comnumb=input('输入串口号(如com4):')
s = serial.Serial(Comnumb,115200)
string = ' '
s.setTimeout(0)
#thrd = threading.Thread(target=MyTxThread,name='koing2010')
#thrd.start()
for i in range(10000):
#	print('第',i,'次读取')
	while s.inWaiting() == 0:#wait ack
		pass
	time.sleep(0.02)#delay 20ms
	numb = s.inWaiting()#read the numb of bytes received
	string = s.read(numb)
	print('%d'% numb)
	if (numb == 35)&(string[0] == 0x5a)&(string[1] == 0xa5)&(string[9] == 0x85):
		print("随机数读取成功")
	if (numb == 28 or numb == 32)&(string[0] == 0x5a)&(string[1] == 0xa5)&(string[9] == 0x85):
		HexShow(string)
		if(string[21] == 0x04)&(string[20] == 0xC0):#cluster 0x04c0
			if(string[22] == 0x00)&(string[21] == 0x00):#atrribute 0x0000
				print("PM25读取成功 PM2.5 = %d",string[25]*256+string[24])
		if(string[19] == 0x00)&(string[20] == 0x05):#cluster 0x0500
			if(string[22] == 0x02)&(string[21] == 0x00):#atrribute 0x0002
				print("Alarm Report")
				print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		if(string[19] == 0x05)&(string[20] == 0x04):#cluster 0x0405
			if(string[22] == 0x00)&(string[21] == 0x00):#atrribute 0x0000
				print("humidity %% %.2f "%(int(string[25]*256+string[24])/100.0))#% need '%%'
				print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
		if(string[19] == 0x02)&(string[20] == 0x04):#cluster 0x0402
			if(string[22] == 0x00)&(string[21] == 0x00):#atrribute 0x0000
				print("temperature %.2f ℃"%(int(string[25]*256+string[24])/100.0))
				print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

s.close()
#thrd.join()
