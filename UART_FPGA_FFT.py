import serial
import time
import threading
import struct

import numpy as np
import pylab as pl
import math

#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523
SerialPort = serial.Serial('com27', 1000000)  # 对应fpga 内的 100MHZ_390KHZ

def PrintMstime():
    t = time.time()
    return int(round(t * 1000))  # 毫秒级时间戳

if __name__ == '__main__':

    N = 1024  # 采样点数
    fs = 25  # 采样频率
    df = fs / (N - 1)  # 分辨率
    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    Yticks = np.arange(-150, 10, 10)


    SendMsg = struct.pack('<B', 0x04)  #设置50MHz采样
    #SerialPort.write(SendMsg)

    while True:
        SendMsg = struct.pack('<B',0x11) #
        SerialPort.write(SendMsg)
        Value = []
        startMs = PrintMstime()

        for i in range(1024):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(2)
            Vpp = ( struct.unpack('<H', byte[0:2])[0] -2050)/2048.0
            #Vpp = struct.unpack('<F', byte[0:4])[0]
            Value.append(Vpp)  # uints = mV, right lead 4bits
        endMs = PrintMstime()
        print(endMs - startMs)

        if( len(Value) == 1024):
            Y = np.fft.fft(Value)*2/ N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
            #print(Y)
            absY = [20*math.log10(np.abs(x)+ 0.0000001)  for x in Y]  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率
            pl.clf() #清楚画布上的内容
            pl.plot(f, absY,'-b')


            pl.title('FFT')
            pl.ylabel('dBm')
            pl.xlabel('Frequency (MHz)')
            pl.yticks(Yticks)

            pl.pause(0.01)
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))