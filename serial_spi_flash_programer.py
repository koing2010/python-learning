import serial
import time
import threading
import struct

WriteCmd = 0x01
ReadCmd = 0x00

def MyTxThread():
	x = 1
	circle = 0
	while x < 50:
		x = 1 + x
		print('%d'% x)
		time.sleep(0.5)

def	 CheckSum(data):
	c_sum = 0
	for i in range(len(data)):
		c_sum += data[i]
	return c_sum&0xFF

def HexShow(S_name,i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print(S_name,hex_string,'	total:',hLen)
		
Comnumb = 'com16'
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
string = ' '
s.setTimeout(0)
#thrd = threading.Thread(target=MyTxThread,name='koing2010')
#thrd.start()
address = 0;
startTime = time.time()
while(1):
	#read the flash format   cmd + address + data size  + data (if necessary)
	read_cm_format = struct.pack('<BIB',ReadCmd, address, 0x10)
	read_cm_format = read_cm_format +  struct.pack('<B',CheckSum(read_cm_format))
	s.write(read_cm_format)
	#HexShow("TxData", read_cm_format)
	while s.inWaiting() == 0:
		#time.sleep(0.1)
		pass
	#time.sleep(0.01)
	n = s.inWaiting()
	string = s.read(n)
	#print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
	HexShow("\r address=%X "%address,string)# display the data received returning the last line.
	address =address + 0x10
	if(address >= 0x80000 ):
		print("reading over chip using time is %.2f Seconds" % (time.time()-startTime))
		break
	#time.sleep(1)
	#print(string)
s.close()
#thrd.join()
