import serial
import time
import threading
import struct
# XOR of all the bytes
def calcFCS(pMsg):
	result = 0
	for i in range(len(pMsg)):
		result = result^pMsg[i]
	return result & 0xFF

#define the value of communication format
def DataRequest(SendData,):
	# SOF  +  General format frame + FCS
	#  1byte  + 3-253bytes  +  1bytes
	SendData = struct.pack("<B", 0xFE) + SendData + calcFCS(SendData)#XOR the general format frame fields
	s.write(SendData)


def MyTxThread():
	x = 1
	circle = 0
	while x < 50:
		x = 1 + x
		print('%d'% x)
		time.sleep(0.5)

def HexShow(S_name,i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print(S_name,hex_string,'	total:',hLen)
		
Comnumb = 'com14'
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
string = ' '
s.setTimeout(0)
#thrd = threading.Thread(target=MyTxThread,name='koing2010')
#thrd.start()
while(1):
	#print('第',i,'次读取')
	while s.inWaiting() == 0:
		time.sleep(0.1)
		pass
	time.sleep(0.01)
	n = s.inWaiting()
	string = s.read(n)
	print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
	HexShow("\r    ReceiveBytes",string)# display the data received returning the last line.
	#print(string)
s.close()
#thrd.join()
