#import serial
import time
import threading
import struct

#The subsystem of the command
CMD0_SUBSYSTEM_RPC_ERR_INTERFACE = 0
CMD0_SUBSYSTEM_SYS_INTERFACE = 1
CMD0_SUBSYSTEM_AF_INTERFACE = 4
CMD0_SUBSYSTEM_ZDO_INTERFACE = 5
CMD0_SUBSYSTEM_SIMPLE_API_INTERFACE = 6
CMD0_SUBSYSTEM_UTIL_INTERFACE = 7
CMD0_SUBSYSTEM_APP_INTERFACE = 9
# The command type
CMD0_TYPE_POLL = 0
CMD0_TYPE_SREQ = 1
CMD0_TYPE_AREQ = 2
CMD0_TYPE_SRSP = 3

sys_reset_req = (b'\x01\x41\x00\x00')
sys_version = (b'\x00\x21\x02')
sys_osal_nv_read_header = (b'\x03\x21\x08')

#def
def ProcessRxData( msg ):
	tempMsg = calcFCS(msg[0,len(msg)])
	print("%02X"%tempMsg)
	if(tempMsg == msg[len(msg)-1]):
		print()
	else:
		print("serial rx data fcs erro!")


# XOR of all the bytes
def calcFCS(pMsg):
	result = 0
	for i in range(len(pMsg)):
		result = result^pMsg[i]
	return result & 0xFF

#define the value of communication format
def DataRequest(SendData):
	# SOF  +  General format frame + FCS
	#  1byte  + 3-253bytes  +  1bytes
	SendData = struct.pack("<B", 0xFE) + SendData + struct.pack("<B",calcFCS(SendData))#XOR the general format frame fields
	HexShow("txdata",SendData)
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
		
Comnumb = 'com5'
#Comnumb=input('输入串口号(如com9):')
#s = serial.Serial(Comnumb,115200)
#s.setTimeout(0)
#thrd = threading.Thread(target=MyTxThread,name='koing2010')
#thrd.start()
#while(1):
#	#print('第',i,'次读取')
#	while s.inWaiting() == 0:
#		time.sleep(0.1)
#		pass
#	time.sleep(0.01)
#	n = s.inWaiting()
#	string = s.read(n)
#	print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
#	HexShow("\r    ReceiveBytes",string)# display the data received returning the last line.
	#print(string)
DataRequest(sys_osal_nv_read_header + struct.pack("<HB", 0x0F01, 0x00))
#s.close()
#thrd.join()
