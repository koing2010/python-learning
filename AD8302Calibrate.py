from pylab import *
import numpy as np
import time
import crclib
import struct
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt


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


SerialPort = serial.Serial("com16",115200)
FrequencyStart = 1000000 # 1Mhz
FreqSweepRate =  00000 # 0kHz
FreqSweepTimes = 100 #100 points

VmageCal = []


for i in range(180):
    Vphs = []
    Vmage = []
    FrequencyStart = FrequencyStart+ 1000000  # step up by 1Mhz
    SendMsg = struct.pack('<BBLBLL',15,0x02,FrequencyStart,0, FreqSweepRate,FreqSweepTimes) # L+B = 5bytes FreqCurrent

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