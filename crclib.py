#crc16 calculate
def cal_crc16(puchMsg,crc_count):
	xorCRC = 0xA001
	CRC = 0xFFFF
	for i in range(crc_count):
		CRC ^= puchMsg[i]
		for j in range(8):
			XORResult = CRC & 0x01
			CRC >>= 1
			if (XORResult & 0xFF):
				CRC ^= xorCRC
	return CRC


def CheckSum16(puchMsg):
	Sum = 0
	for i in range( len(puchMsg)):
		Sum = Sum + puchMsg[i]
	return Sum

def cal_file_crc16(puchMsg,crc_count,CRC):
	xorCRC = 0xA001
	for i in range(crc_count):
		CRC ^= puchMsg[i]
		for j in range(8):
			XORResult = CRC & 0x01
			CRC >>= 1
			if (XORResult & 0xFF):
				CRC ^= xorCRC
	return CRC

# XOR of all the bytes
def calcFCS(pMsg):
	result = 0
	for i in range(len(pMsg)):
		result = result^pMsg[i]
	return result & 0xFF