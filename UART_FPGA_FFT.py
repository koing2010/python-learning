import serial
import time
import threading
import struct

import numpy as np
import pylab as pl
import math

#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523

if __name__ == '__main__':
    SerialPort = serial.Serial('com13', 390000)# 对应fpga 内的 100MHZ_390KHZ

    SendMsg = struct.pack('<B',0x11) #
    SerialPort.write(SendMsg)
    Value = []
    for i in range(1024):
        while SerialPort.inWaiting() == 0:
            pass
        byte = SerialPort.read(2)
        Vpp = ((struct.unpack('<H', byte[0:2])[0])-2017.4)/2048
        Value.append(round( Vpp , 6))  # uints = mV, right lead 4bits


    N = 1024 # 采样点数
    fs = 25 # 采样频率
    df = fs / (N - 1)  # 分辨率
    f = [round(df * n, 6) for n in range(0, N)]  # 构建频率数组
    Y = np.fft.fft(Value)*2/ N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
    #print(Y)
    absY = [20*math.log10(np.abs(x))  for x in Y]  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率
    Yticks = np.arange(-120,10, 10)
    pl.plot(f, absY)
    pl.title('FFT')
    pl.ylabel('dBm')
    pl.xlabel('Frequency (MHz)')
    pl.yticks(Yticks)
    pl.show()