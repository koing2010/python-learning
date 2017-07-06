import serial
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
sys_osal_nv_read_header = (b'\x03\x21\x08')#
#SYS_SET_TX_POWER
sys_set_tx_power= (b'\x01\x21\x14')# TX Power – 1 byte – Actual TX power setting, in dBm.
#SYS_ ZDIAGS_RESTORE_STATS_NV
sys_zdiags_restore_stats_nv = (b'\x00\x21\x1A')#This command is used to restore the statistics table from NV into the RAM table.

ZB_READ_CONFIGURATION = (b'\x01\x26\x04')# + Configid
ZB_WRITE_CONFIGURATION = (b'\x26\x05')# ConfigId + Len + Value

ZB_PERMIT_JOINING_REQUEST = (b'\x03\x26\x08')#Destination + Timeout
ZB_ALLOW_BIND = (b'\x01\x26\x02')#TimeOut
#def
def ProcessRxData( msg ):
	tempMsg = calcFCS(msg[1:len(msg)-1])
	print("%02X"%tempMsg)
	if(tempMsg == msg[len(msg)-1]):
		print("ProcessRxData: FCS success")
		if msg[2]>>5 & 0x07 is CMD0_TYPE_POLL:
			print("CMD0_TYPE_POLL")
		if msg[2]>>5 & 0x07 is CMD0_TYPE_SREQ:
			print("CMD0_TYPE_SREQ")
		if msg[2]>>5 & 0x07 is CMD0_TYPE_AREQ:
			print("CMD0_TYPE_AREQ")
		if msg[2]>>5 & 0x07 is CMD0_TYPE_SRSP:
			print("CMD0_TYPE_SRSP")
			####### Cmo0 judge ##############
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_RPC_ERR_INTERFACE:
				print("CMD0_SUBSYSTEM_RPC_ERR_INTERFACE")
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_SYS_INTERFACE:
				print("CMD0_SUBSYSTEM_SYS_INTERFACE")
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_AF_INTERFACE:
				print("CMD0_SUBSYSTEM_AF_INTERFACE")
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_ZDO_INTERFACE:
				print("CMD0_SUBSYSTEM_ZDO_INTERFACE")
				####### Cmo1 judge ##############
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_SIMPLE_API_INTERFACE:
				print("CMD0_SUBSYSTEM_SIMPLE_API_INTERFACE")
				####### Cmo1 judge ##############
				if msg[3] is 0x04:#ZB_READ_CONFIGURATION Response
					if msg[4] is 0x00:
						print("Status: SUCCESS")
						print("Configid=0x%02X" % msg[5])# The identifier for the configuration property
						if msg[5] is 0x01:
							print("IEEE64")
						elif msg[5] is 0x02:
							print(">...")
						else:
							print("unkown")
						HexShow("Len=0x%02X, vlaue= "%msg[6],msg[7:7+msg[6]])
					else:
						print("Status: FAILED")
					#elif  msg[3] is 0x04
				if (msg[3] is 0x08 ):#ZB_PERMIT_JOINING_RSP
					if(msg[4] is 0x00):#status
						print("Permit Joining Status: SUCCESS")
					else:
						print("Permit Joining Status: FAILED")

			if msg[2] & 0x1F is CMD0_SUBSYSTEM_UTIL_INTERFACE:
				print("CMD0_SUBSYSTEM_UTIL_INTERFACE")
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_APP_INTERFACE:
				print("CMD0_SUBSYSTEM_APP_INTERFACE")
	else:
		print("ProcessRxData: serial rx data fcs erro!")


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
	HexShow("DataRequest:",SendData)
	s.write(SendData)


def MyTxThread():
	print("rx thread start")
	while(1):
		while s.inWaiting() == 0:
			time.sleep(0.1)
			pass
		time.sleep(0.01)
		n = s.inWaiting()
		msg = s.read(n)
		HexShow("",msg)
		print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
		ProcessRxData(msg)
#	HexShow("\r    ReceiveBytes",string)# display the data received returning the last line.

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
s = serial.Serial(Comnumb,115200)
#s.setTimeout(0)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()

	#print(string)
DataRequest (sys_osal_nv_read_header + struct.pack("<HB", 0x0F01, 0x00) )
time.sleep(0.5)
DataRequest( sys_set_tx_power + struct.pack("<B", 0x05) )#set tx power 5dbm
time.sleep(0.5)
DataRequest( sys_zdiags_restore_stats_nv)
time.sleep(0.5)
DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x01) )
time.sleep(0.5)
DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x02) )
#time.sleep(0.5)
#DataRequest(struct.pack("<B", 0x05) + ZB_WRITE_CONFIGURATION + struct.pack("<BBH", 0x02, 0x02, 20))
time.sleep(0.5)
DataRequest( ZB_PERMIT_JOINING_REQUEST +  struct.pack("<HB", 0xFFFC, 0x00) )
thrd.join()
s.close()