import serial
import time
import threading
import struct


SUCCESS = 0
FALURE = 1
#OPTION
AF_WILDCARD_PROFILEID         =     0x02   # Will force the message to use Wildcard ProfileID
AF_ACK_REQUEST                =     0x10   # Will force APS to callback to preprocess before calling NWK layer
AF_SUPRESS_ROUTE_DISC_NETWORK =     0x20   # Supress Route Discovery for intermediate routes
                                           # (route discovery preformed for initiating device)
AF_EN_SECURITY                =    0x40    # APS security
AF_SKIP_ROUTING               =    0x80    #ship routing


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

# called when this node receives a zdo/ zdp response
ZDO_RESPONSE_BIT = 0x8000
Active_EP_req = 0x0005
Match_Desc_req = 0x0006
Match_Desc_rsp = Match_Desc_req | ZDO_RESPONSE_BIT
Active_EP_rsp =  (Active_EP_req | ZDO_RESPONSE_BIT)

Device_annce = 0x0013

def ProcessZDOmsgs(SrcAddr, WasBroadcast, ClusterID, SecurityUse, SeqNum, pData):
	if ClusterID is Match_Desc_req:
		print("Match_Desc_req")
		MatchList = (b'\x01')
		ZDO_Mactch_Desc_Rsp(SrcAddr, SeqNum, SUCCESS, 0xFFFD, 1, MatchList)#(DesAddr, SeqNum, Status, NwkAddr, MatchLength, MatchList):

	if ClusterID is Device_annce:
		print("Device_annce")
		HexShow("nwkAddr",pData[0:2])
		HexShow("extAddr",pData[2:])
		dstAddr =struct.unpack( "<H", pData[0:2])
		ZDP_ActiveEPReq(dstAddr[0], SeqNum,dstAddr[0])
	if ClusterID == Active_EP_rsp:
		print("Active_EP_rsp ")
		if (pData[0] is 0):
			print("\rSUCCESS ", "NwkAddrOfInterest: %04X"%(pData[1]+pData[2]*256))
			minEndpoint = 1;
			for i in range(pData[3]):
				if pData[3+i] < minEndpoint:
					minEndpoint = pData[3+i]
			zcl_msg = struct.pack("<BBBHH", 0x00, SeqNum + 1, 0x00, 0x0004,0x0005)
			AF_DataRequest(SrcAddr,minEndpoint,1,0x0000,1,AF_SUPRESS_ROUTE_DISC_NETWORK|AF_EN_SECURITY,30,len(zcl_msg),zcl_msg)

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
			if msg[3] is 0x80:
				print("AF_DATA_CONFIRM")
				if msg[1] is 0x03:
					print("Status:%02X "%msg[4],"Endpoint:%02X"%msg[5], "TranID:%02X"%msg[6])
				else:
					print("leth erro")
			if msg[3] is 0x81:
				print("AF_INCOMING_MESSAGE")
				if msg[1] < 9:
					print("leth erro")
				else:
					print("GroupID:%04X "%(msg[4]+msg[5]*256), "ClusterID:%04X "%(msg[6]+msg[7]*256), \
						 "SrcAddr: %04X "%(msg[8]+msg[9]*256), "SrcEndpoint：%02X "%msg[10], "DestEndpoint：%02X "%msg[11],\
						"WasBroadcast: %02X " % msg[12], "LinkQuality: %02X " % msg[13], "SecurityUse: %02X " % msg[14], \
						"Timestamp: %08X " % struct.unpack("<I",msg[15:19]),"TransSeqNumber: %02X " % msg[19], "len: %02X " % msg[20])
					HexShow("data:",msg[21:msg[20]+21])#data zcl frame
			if msg[3] is 0xFF:#ZDO message incoming
				print("ZDO_ MSG_CB_INCOMING")
				if msg[1] < 9:
					print("ZDO_MSG Data lenth erro!!!")
				else:
					print("SrcAddr:%04X "%(msg[4]+msg[5]*256),"WasBroadcast: %02X "%msg[6], "ClusterID: %04X "%\
					(msg[8]*256+msg[7]), "SecurityUse: %02X "%msg[9], "SqeNum: %02X "%msg[10], "MacDstAddr: %02X"%(msg[11]+msg[12]*256))
					HexShow("Data:",msg[13:msg[1]+4])
					ProcessZDOmsgs((msg[4]+msg[5]*256),msg[6], (msg[8]*256+msg[7]), msg[9],msg[10],msg[13:msg[1]+4])  # (SrcAddr, WasBroadcast, ClusterID, SecurityUse, SeqNum, pData):

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




#define the value of communication format
def DataRequest(SendData):
	# SOF  +  General format frame + FCS
	#  1byte  + 3-253bytes  +  1bytes
	SendData = struct.pack("<B", 0xFE) + SendData + struct.pack("<B",calcFCS(SendData))#XOR the general format frame fields
	HexShow("DataRequest:",SendData)
	s.write(SendData)
#call this fucntion ro register of an imcoming over the air zdo message probably a response message but requests can also be received
def ZDO_RegisterForZDOMsgCB(ClsusterID):
	DataRequest(struct.pack("<BBBH",0x02,0x25,0x3E,ClsusterID))

def ZDO_RemoveForZDOMsgCB(ClusterID):
	DataRequest(struct.pack("<BBBH"), 0x02,0x25,0x3F,ClusterID)

def ZDP_MgmtPermitJoinReq( dstAddr, duration, TcSignificance ):
	DataRequest(struct.pack("<BBBBHBB", 0x05, 0x25, 0x36, 0x02, dstAddr, duration, TcSignificance ))

def ZDO_Send_Data(DesAddr, Transeq, Cmd, lenth, zod_msg):
	msg = struct.pack("<BBHBHB", 0x45, 0x28, DesAddr, Transeq, Cmd, lenth) + zod_msg
	DataRequest(struct.pack("<B", len(msg) - 2) + msg)

def ZDP_ActiveEPReq(dstAddr,SeqNum, NWKAddrOfInterest ):
	msg = struct.pack("<H", NWKAddrOfInterest)
	ZDO_Send_Data(dstAddr, SeqNum, Active_EP_req, len(msg), msg)

#This callback message is in response to the ZDO Match Descriptor Request
def ZDO_Mactch_Desc_Rsp(DesAddr, SeqNum, Status, NwkAddr, MatchLength, MatchList):
	msg = struct.pack("<BHB", Status,NwkAddr,MatchLength)+ MatchList
	ZDO_Send_Data(DesAddr, SeqNum, Match_Desc_rsp, len(msg), msg)

#This function processes a Management Leave Request and generates the response.
def  ZDO_ProcessMgmtLeaveReq(DstAddr, pDeviceAddr, RemoveChildren_Rejoin):
	msg = struct.pack("<BBBH", 0x0B, 0x25, 0x34, DstAddr)+ pDeviceAddr + struct.pack("<B",RemoveChildren_Rejoin)
	DataRequest( msg )

def ZDP_EPRsp(DesAddr, SeqNum, Status, NwkAddr, lenth, EPList):
	msg = struct.pack("<BHB", Status,NwkAddr,lenth)+ EPList
	ZDO_Send_Data(DesAddr, SeqNum, Active_EP_rsp, len(msg), msg)

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
	msg = struct.pack("<H",DstAddr) + struct.pack("<B",DestEndpoint) + struct.pack("<B", SrcEndpiont)  + \
		  struct.pack("<H", ClusterID) + struct.pack("<B" ,TransID) + struct.pack("<B" ,Options) + \
		  struct.pack("<B",Radius) + struct.pack("<B", DataLen) + pData
	DataRequest(  struct.pack("<B",len(msg)) + struct.pack("<BB",0x24,0x01) + msg   )# cmd0= 0x24 + Cmd1=0x01

def MyTxThread():
	print("rx thread start")
	while(1):
		while s.inWaiting() == 0:
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
		
Comnumb = 'com13'
#Comnumb=input('输入串口号(如com9):')
s = serial.Serial(Comnumb,115200)
#s.setTimeout(0)
thrd = threading.Thread(target=MyTxThread,name='koing2010')
thrd.start()

	#print(string)
#DataRequest (sys_osal_nv_read_header + struct.pack("<HB", 0x0F01, 0x00) )
#time.sleep(0.5)
#DataRequest( sys_set_tx_power + struct.pack("<B", 0x05) )#set tx power 5dbm
#time.sleep(0.5)
#DataRequest( sys_zdiags_restore_stats_nv)
#time.sleep(0.5)
"""
zb_write_configratiion(0x83, 0x02, struct.pack("<H", 0x6789))#set panid
#time.sleep(0.5)
#time.sleep(0.5)
#zb_write_configratiion(0x03, 0x01, struct.pack("<B", 0x02))#reset factry
zb_write_configratiion(0x8F, 0x01, struct.pack("<B", 0x01))#set clear
time.sleep(0.1)
zb_write_configratiion(0x84, 0x04, struct.pack("<I", 0x04000000))#set chanlist
"""
#time.sleep(1)
#DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x03) )
#time.sleep(0.5)
#DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x87) )
#time.sleep(0.5)

DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x84) )
time.sleep(0.1)
DataRequest( ZB_READ_CONFIGURATION + struct.pack("<B", 0x83) )
#time.sleep(0.5)
DataRequest(ZB_START_REQUEST)
time.sleep(0.1)
AF_RegisterAppEndpointDescription(0x01, 0x0104, 0x0000, 0x00, 0x00, 1,struct.pack("<H", 0x0006), 1,struct.pack("<H", 0x0006))
time.sleep(0.1)
ZDO_RegisterForZDOMsgCB(Match_Desc_req)# mesh req
time.sleep(0.1)
ZDO_RegisterForZDOMsgCB(Device_annce)#
time.sleep(0.1)
ZDO_RegisterForZDOMsgCB(Active_EP_rsp)
time.sleep(0.1)
#DataRequest( ZB_PERMIT_JOINING_REQUEST +  struct.pack("<HB", 0xFFFC, 0x10) )
ZDP_MgmtPermitJoinReq(0xFFFC,20,1)

DataRequest(struct.pack("<BBB",0x00,0x21,0x04))

"""
while(1):
    InputMac = input("duration = ")
    if len(InputMac) is 29:
        msg = bytes.fromhex(InputMac)
        desAddr = struct.unpack("<H",msg[0:2])
        ZDO_ProcessMgmtLeaveReq(desAddr[0], msg[2:] , 0)
    else:
        print("InPut lentherro")
"""
"""
while(1):
	InputMac = input("duration = ")
	duration = bytes.fromhex(InputMac)
	ZDP_MgmtPermitJoinReq(0xFFFC, duration[0], 1)
"""
status = 0x01
seqnum = 0x01
zcl_msg = struct.pack("<BBBH", 0x00,seqnum ,0x00, 0x0000)#zcl_fc + SeqNum + cmd + Variable
AF_DataRequest(0x95FC, 1, 1, 0x0006, 1, AF_SUPRESS_ROUTE_DISC_NETWORK | AF_EN_SECURITY, 30, len(zcl_msg), zcl_msg)
seqnum +=1
zcl_msg = struct.pack("<BBBH", 0x00,seqnum ,0x00, 0x0000)#zcl_fc + SeqNum + cmd + Variable
AF_DataRequest(0x95FC, 2, 1, 0x0006, 1, AF_SUPRESS_ROUTE_DISC_NETWORK | AF_EN_SECURITY, 30, len(zcl_msg), zcl_msg)
time.sleep(4)

while 1:
	seqnum += 1
	if status is 1:
		status = 0x00
		zcl_msg = struct.pack("<BBB",0x01,0x02,0x01)#zcl_fc + SeqNum + cmd + Variable
	else:
		status = 0x01
		zcl_msg = struct.pack("<BBB", 0x01, 0x00, 0x00)
	AF_DataRequest(0x95FC,1,1,0x0006,1,AF_SUPRESS_ROUTE_DISC_NETWORK|AF_EN_SECURITY,30,len(zcl_msg),zcl_msg)
	time.sleep(4)

thrd.join()
s.close()