import struct
import crclib

TyHeader = 0x38
ProtocolType = 0x01
zdo_endpoint = 0

#Send Mesage to Coordinator
def PackSendDataToModle( SendMsg, clusterCmd, Fc, Cmd ):
	SendMsg = struct.pack('<BBB', 0x01, TyHeader, ProtocolType) + struct.pack('<BHBB', zdo_endpoint, clusterCmd, Fc, Cmd) + SendMsg
	Send_Lenth = len(SendMsg) + 6 # 6 = start_2bytes + lenth_2bytes + crc16_2bytes
	SendMsg =  struct.pack('<H',0xB55B) + struct.pack('<H',Send_Lenth) + SendMsg #add start lenth
	SendMsg = SendMsg + struct.pack('<H', crclib.cal_crc16(SendMsg, len(SendMsg))) # add crc
	return SendMsg