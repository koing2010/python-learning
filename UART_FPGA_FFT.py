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
    fs = 20  # 采样频率
    df = fs / (N - 1)  # 分辨率
    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    Yticks = np.arange(-150, 10, 10)


    SendMsg = struct.pack('<B', 0x04)  #设置20MHz采样
    #SerialPort.write(SendMsg)

    while True:
        SendMsg = struct.pack('<B',0x11) #
        SerialPort.write(SendMsg)
        Value = []
        LoCosValue = []
        LoSinValue = []
        startMs = PrintMstime()

        for i in range(1024):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(4)
            Vpp = ( struct.unpack('<H', byte[0:2])[0] -2048)/2048.0

            LoSinVpp =  math.cos( byte[2:3][0]/40 * 2*math.pi  ) # 2pi*k  FPGA内计数是一个园周期,不乘以2
            LoCosVpp =  math.cos( byte[3:4][0]/40 * 2*math.pi )
            Value.append(Vpp)  # uints = mV, right lead 4bits
            LoSinValue.append(LoSinVpp)
            LoCosValue.append(LoCosVpp)
        endMs = PrintMstime()
        #print(endMs - startMs)

        if( len(Value) == 1024):


            YsinXY = np.multiply(np.array(Value),np.array(LoSinValue))
            YcosXY = np.multiply(np.array(Value), np.array(LoCosValue))

            Y = np.fft.fft(Value) * 2 / N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
            I_value = np.fft.fft(YsinXY)*2/ N
            Q_value = np.fft.fft(YcosXY)*2/ N

            #print(Y);
            absY = [20*math.log10(np.abs(x)+ 0.0000001)  for x in Y]  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率
            absYsinCos = [20 * math.log10(np.abs(x) + 0.0000001) for x in I_value]


            pl.clf() #清楚画布上的内容
            pl.plot(f, absY,'-b')
            pl.plot(f, absYsinCos, '-r')

            print( "I φ= %3.2f °"% (math.acos( I_value[0].real / (np.abs(Y[101] ) + np.abs(I_value[0]) ) )/math.pi *180)  )
            print( "Q φ= %3.2f °\n" % (math.asin(  - Q_value[0].real / ( np.abs(Y[101]) + np.abs(Q_value[0])) ) / math.pi * 180))
           # print(math.atan( YsinYcos[0].real) /absYsinCos)
            #print( math.atan( YsinYcos[101].imag/ YsinYcos[101].real)  ,math.asin( YsinYcos[102].imag/ YsinYcos[102].real ) )

            pl.title('FFT')
            pl.ylabel('dBm')
            pl.xlabel('Frequency (MHz)')
            pl.yticks(Yticks)

            pl.pause(0.01)
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))