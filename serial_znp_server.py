import serial
import time
import threading
import struct

#For AF
AF_DEFAULT_RADIUS = 0x1E

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

ZB_START_REQUEST = (b'\x00\x26\x00')
ZB_PERMIT_JOINING_REQUEST = (b'\x03\x26\x08')#Destination + Timeout
ZB_ALLOW_BIND = (b'\x01\x26\x02')#TimeOut

#def
def ProcessRxData( msg ):
	if len(msg) < msg[1]+4:
		print("rx lenth erro")
		return ""

	tempMsg = calcFCS(msg[1:msg[1]+4])
	print("GetDeviceRsp:")
	if(tempMsg == msg[msg[1]+4]):
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
				if(msg[3] == 0x00):
					print("  AF status success")
				else:
					print("  AF status Faild")

			if msg[2] & 0x1F is CMD0_SUBSYSTEM_ZDO_INTERFACE:
				print("CMD0_SUBSYSTEM_ZDO_INTERFACE")
				####### Cmo1 judge ##############
			if msg[2] & 0x1F is CMD0_SUBSYSTEM_SIMPLE_API_INTERFACE:
				print("CMD0_SUBSYSTEM_SIMPLE_API_INTERFACE")
				####### Cmo1 judge ##############
				if msg[3] is 0x00:
					print("CMD1 ZB_START_CONFIRM")
				if msg[3] is 0x04:#ZB_READ_CONFIGURATION Response
					print("CMD1 ZB_READ_CONFIGURATION")
					if msg[4] is 0x00:
						print("Status: SUCCESS")
						print("Configid=0x%02X" % msg[5])# The identifier for the configuration property
						if msg[5] is 0x01:
							print("IEEE64")
							HexShow("\r ", msg[7:7 + msg[6]])
						elif msg[5] is 0x02:
							print(">...")
						elif msg[5] is 0x84:
							print("Chanlist is ")
							HexShow("\r", msg[7:7 + msg[6]])
						elif msg[5] is 0x83:
							print("PANID is ")
							HexShow("\r", msg[7:7 + msg[6]])
						else:
							print("unkown")
							HexShow("Len=0x%02X, vlaue= "%msg[6],msg[7:7+msg[6]])
					else:
						print("Status: FAILED")
					#elif  msg[3] is 0x04
				if (msg[3] is 0x08 ):#ZB_PERMIT_JOINING_RSP
					print("ZB_PERMIT_JOINING_RSP")
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
# if have data more
	if len(msg) > (msg[1]+4):
		Remsg = msg[msg[1]+5 :len(msg)]
		return Remsg
	else:
		return ""


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

# write a configuration parameter to the CC2530-ZNP device
def zb_write_configratiion( ConfigId, lenth, Value):
	msg = struct.pack("<BBBB",0x26,0x05, ConfigId, lenth) + Value
	msg = struct.pack("<B", len(Value) + 2 ) + msg
	DataRequest(msg)

#AF_REGISTER
def AF_RegisterAppEndpointDescription(EndPoint, AppProfId, AppdeviceId, AppdevVer, LatencyReq, AppNumInclusters,\
									  AppInclusterList, AppNumberOutClusters, AppoutClusterList):
	msg = struct.pack("<BHHBBB", EndPoint, AppProfId, AppdeviceId, AppdevVer, LatencyReq, AppNumInclusters)\
		  + AppInclusterList + struct.pack("<B", AppNumberOutClusters) + AppoutClusterList;
	HexShow( "AF_REGISTER", msg)
	DataRequest(struct.pack("<B", len(msg)) + struct.pack("<BB", 0x24, 0x00) + msg  )  # cmd0= 0x24 + Cmd1=0x00

# AF_DATA_REQUEST
def AF_DataRequest(DstAddr, DestEndpoint, SrcEndpiont, ClusterID, TransID, Options, Radius, DataLen, pData):
	msg = struct.pack("<H",DstAddr) + truct.pack("<B",DestEndpoint) + struct.pack("<B", SrcEndpiont)  + \
		  struct.pack("<H", ClusterID) + struct.pack("<B" ,TransID) + struct.pack("<B" ,Options) + \
		  struct.pack("<B",Radius) + struct.pack("<B", DataLen) + pData
	DataRequest(  struct.pack("<B",len(msg)) + struct.pack("<BB",0x24,0x01) + msg   )# cmd0= 0x24 + Cmd1=0x01

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
		while len(msg):
			msg = ProcessRxData(msg)
			print(">>>>>")
		# space space
		print("\n")

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
#zb_write_configratiion(0x83, 0x02, struct.pack("<H", 0x6789))#set panid
time.sleep(0.5)
#zb_write_configratiion(0x84, 0x04, struct.pack("<I", 0x04000000))#set chanlist
time.sleep(1)
#DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x03) )
time.sleep(0.5)
#DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x87) )
time.sleep(0.5)
DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x84) )
time.sleep(0.5)
DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x83) )
#time.sleep(0.5)
DataRequest(ZB_START_REQUEST)
time.sleep(0.5)
AF_RegisterAppEndpointDescription(0x01, 0x0104, 0x0000, 0x00, 0x00, 1,struct.pack("<H", 0x0006), 1,struct.pack("<H", 0x0006))
time.sleep(0.5)
DataRequest( ZB_PERMIT_JOINING_REQUEST +  struct.pack("<HB", 0xFFFC, 0x20) )

thrd.join()
s.close()