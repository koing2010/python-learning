from pylab import *
import numpy as np
import time
import crclib
import struct
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt

real = True
echo = True

if real:
	s = serial.Serial('com14', 115200, timeout=2, xonxoff=False) #might need to add enable control settings

def cmd(cmd_string):
	if echo:
		print(cmd_string)

	if real:
		s.write(bytes(cmd_string + '\n',encoding = "utf8"))
		#s.readline() #unclear if this is needed

def query(query_string):
	if echo:
		print(query_string)

	if real:
		s.write(bytes(query_string + '\n',encoding = "utf8"))
		result = s.readline()
		if echo:
			print( "-> " +  str(result, encoding = "utf-8"))
		return result

def ReadMesure(query_string):
	if echo:
		print(query_string)
	if real:
		s.write(bytes(query_string + '\n', encoding="utf8"))
		result = s.readline()
		if echo:
			powr = float(str(result, encoding="utf-8"))
			print("-> " , powr, 'dbm')
		return  powr


#display hex string
def HexShow(S_name,i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print(S_name,hex_string,'	total:',hLen)

MHz = 1000000
SerialPort = serial.Serial("com16",115200)
FrequencyStart = 10*MHz # 5Mhz
FreqSweepRate =  10*MHz # 400kHz
FreqSweepTimes = 50 #500 points
FrequencyEnd = FrequencyStart+FreqSweepRate*FreqSweepTimes
query("*IDN?")
query("*RST;*OPC?")

cmd("*SEC 0")
cmd("SYST:NONV:DIS") #disable NVRAM, manual says this is important for performance

cmd("*SEC 1")
#set input and output connectors
cmd("INP RF2")
cmd("OUTP RF3")

#setup generator
#cmd("SOURce:RFGenerator:TX:FREQuency 1MHZ")
cmd("SOUR:RFG:TX:LEVel -10")
cmd("SOUR:RFG:TX:FREQ %dE6" % (FrequencyStart/MHz)) #default level is -27dBm
query("INIT:RFG;*OPC?")

#exit()

#setup analyzer either NPOW or POW, TBD
#TODO Set BW, delay, measurement time, etc. here
#cmd("LEV:MAX 0")
#cmd("CONF:POW:CONT SCAL,NONE") #might not want this
#cmd("CONF:SUB:POW IVAL,0,1")
cmd("RFAN:BAND 1000e3")
cmd("INIT:RFAN") #unclear if I need this, it's in the example
#cmd("INIT:WPOW")
VmageCal = []


for i in range(269):
    Vphs = []
    Vmage = []
    FrequencyStart = FrequencyStart+ 1000000  # step up by 1Mhz

    cmd("RFAN:FREQ %dE6" % ((FrequencyStart * FreqSweepRate* i)/MHz ))
    cmd("SOUR:RFG:FREQ %dE6;*WAI" % ((FrequencyStart  + FreqSweepRate* i)/MHz))
    ReadMesure("READ:RFAN:POW?")
    time.sleep(0.1)
    SendMsg = struct.pack('<BBLBLL',15,0x02,FrequencyStart,0, 0,FreqSweepTimes) # L+B = 5bytes FreqCurrent

    SendMsg = struct.pack("<B", 0xFE) + SendMsg + struct.pack("<B",crclib.calcFCS(SendMsg))  # XOR the general format frame fields

    HexShow("DataRequest:", SendMsg)
    SerialPort.write(SendMsg)

    for i in range(FreqSweepTimes):
        while SerialPort.inWaiting() == 0:
            pass
        byte = SerialPort.read(4)
        Vphs.append(round(struct.unpack('<H', byte[0:2])[0] * 3327.0 / 4096.0, 4))  # uints = mV, right lead 4bits
        Vmage.append(round(struct.unpack('<H', byte[2:4])[0] * 3327.0 / 4096.0, 4))  # adc convert to Voltage, then convert to degree

    N = FreqSweepTimes  # 采样点数
    fs = FreqSweepTimes  # 采样频率
    df = fs / (N - 1)  # 分辨率
    f = [df * n for n in range(0, N)]  # 构建频率数组

    Y = np.fft.fft(Vmage) / N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
    absY = [np.abs(x) for x in Y]  # 求傅里叶变换结果的模
    print(absY[:10])
    VmageCal.append((round(absY[0],2)))

#save result
np.save('VmageCal.npy', np.array(VmageCal))