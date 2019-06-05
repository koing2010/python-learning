import serial
import time
import threading
import struct

import numpy as np
import pylab as pl
import math
from scipy import signal

#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523
SerialPort = serial.Serial('com27', 1000000)  # 对应fpga 内的 100MHZ_390KHZ

def PrintMstime():
    t = time.time()
    return int(round(t * 1000))  # 毫秒级时间戳

if __name__ == '__main__':

    fs = 20  # 采样频率
    N = 2048  # 采样点数
    N_HALF = 1024 #
    df = fs / (N - 1)  # 分辨率

    N_2MHZ = int(round( 2/ df, 0))# Lo= 2Mhz 点的位置
    N_4MHZ = int(round( 4/ df, 0))


    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    Yticks = np.arange(-150, 10, 10)


    SendMsg = struct.pack('<B', 0x14)  #设置20MHz采样
    SerialPort.write(SendMsg)

    while True:
        SendMsg = struct.pack('<B',0x01) #20Mhz
        SerialPort.write(SendMsg)
        XCosValue = []
        LoCosValue = []
        LoSinValue = []
        startMs = PrintMstime()

        for i in range(   N  ):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(4)
            #Vpp = ( struct.unpack('<H', byte[0:2])[0] -2048)/2048.0
            Vpp = math.cos((byte[3]) / 40 * 2 * math.pi  + 0.25* math.pi)
            LoSinVpp =  math.cos( byte[2]/40 *2* math.pi  ) # 2pi*k  FPGA内计数是一个园周期,不乘以2
            LoCosVpp =  math.cos( byte[3]/40 *2* math.pi )
            XCosValue.append(Vpp)  # uints = mV, right lead 4bits
            LoSinValue.append(LoSinVpp)
            LoCosValue.append(LoCosVpp)
        endMs = PrintMstime()
        #print(endMs - startMs)

        if( len(XCosValue) ==   N ):


            I_X = np.multiply(np.array(LoSinValue),np.array( XCosValue))
            Q_X = np.multiply(np.array(LoCosValue), np.array( XCosValue ))
            #I_Q = np.multiply(np.array(LoSinValue),np.array( LoCosValue))

            X_value = np.fft.fft(XCosValue) * 2 / N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
            I_value = np.fft.fft(LoSinValue)*2/ N
            Q_value = np.fft.fft(LoCosValue)*2/ N
            I_Xvalue = np.fft.fft(I_X)*2/ N
            Q_Xvalue = np.fft.fft(Q_X)*2/ N


            absY = [20*math.log10(np.abs(x)+ 0.0000001)  for x in X_value]  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率
            absYsinCos = [20 * math.log10(np.abs(x) + 0.0000001) for x in I_value]


            pl.clf() #清楚画布上的内容
            pl.plot(f[0:N_HALF], absY[0:N_HALF],'-b') #[0:N_HALF]  只显示一半即可
            pl.plot(f[0:N_HALF], absYsinCos[0:N_HALF], '-g')


            I_acrcos = I_value[N_2MHZ].real / (np.abs(I_value[N_2MHZ]))
            Q_acrcos = Q_value[N_2MHZ].real / (np.abs(I_value[N_2MHZ] ))
            X_acrcos = X_value[N_2MHZ].real / (np.abs(X_value[N_2MHZ] ))
            I_Xacrcos = I_Xvalue[N_4MHZ].real/np.abs(I_Xvalue[N_4MHZ])
            Q_Xacrcos = Q_Xvalue[N_4MHZ].real / np.abs(Q_Xvalue[N_4MHZ])
            print(I_Xacrcos, Q_Xacrcos )

            if(I_Xacrcos < -1 ):
                I_Xacrcos = -1
            if(Q_Xacrcos < -1 ):
                Q_Xacrcos = -1
            if(I_Xacrcos > 1 ):
                I_Xacrcos = 1
            if(Q_Xacrcos > 1 ):
                Q_Xacrcos = 1

            I_Degree = round( (math.acos(  I_acrcos )/math.pi *180), 2)
            Q_Degree = round( (math.acos( Q_acrcos ) / math.pi * 180), 2)
            X_Degree =  round( (math.acos(X_acrcos ) / math.pi * 180), 2)
            I_X_Degree = round((math.acos(I_Xacrcos) / math.pi * 180), 2)
            Q_X_Degree = round((math.acos(Q_Xacrcos) / math.pi * 180), 2)

            I_Degree1 = 360 - I_Degree

            print("I Degree= %3.2f °" % I_Degree ,"   %3.2f °" % I_Degree1  )

            Q_Degree1 = 360 - Q_Degree
            print( "Q Degree= %3.2f °" % (Q_Degree), "   %3.2f °" % Q_Degree1 )

            Q_token = I_Degree + 90
            if(Q_token >= 360):
                Q_token = Q_token - 360

            Q_token1 = I_Degree1 + 90
            if(Q_token1 >= 360):
                Q_token1 = Q_token1 - 360

            if( ((Q_token >= Q_Degree - 5) and (Q_token <= Q_Degree + 5))):

                TrueIdegree = I_Degree
                TrueQdegree = Q_Degree
            elif  ((Q_token >= Q_Degree1 - 5) and(Q_token <= Q_Degree1 + 5)):

                TrueIdegree = I_Degree
                TrueQdegree = Q_Degree1

            if ((Q_token1 >= Q_Degree - 5) and (Q_token1 <= Q_Degree + 5)):

                TrueIdegree = I_Degree1
                TrueQdegree = Q_Degree
            elif  ((Q_token1 >= Q_Degree1 - 5) and(Q_token1 <= Q_Degree1 + 5)):
                TrueIdegree = I_Degree1
                TrueQdegree = Q_Degree1

            print("TrueIdegree = %3.2f "% TrueIdegree, "TrueQdegree = %3.2f "% TrueQdegree)

            print( "X Degree = %3.2f °" % X_Degree,  "   %3.2f °" % (360 - X_Degree) )

            I_X_Degree1 = (360 - I_X_Degree)
            print("I_X Degree = %3.2f °" % I_X_Degree, "   %3.2f °" %I_X_Degree1 )

            Q_X_Degree1 = (360 - Q_X_Degree)
            print("Q_X Degree = %3.2f °" % Q_X_Degree, "   %3.2f °" %Q_X_Degree1 )

            Q_X_token = I_X_Degree + 90
            if(Q_X_token >= 360 ):
                Q_X_token = Q_X_token - 360
            Q_X_token1 = I_X_Degree1 + 90
            if (Q_X_token1 >= 360):
                Q_X_token1 = Q_X_token1 - 360

            if (((Q_X_token >= Q_X_Degree - 5) and (Q_X_token <= Q_X_Degree + 5))):

                TrueI_Xdegree = I_X_Degree
                TrueI_Qdegree = Q_X_Degree
            elif ((Q_X_token >= Q_X_Degree1 - 5) and (Q_X_token <= Q_X_Degree1 + 5)):

                TrueI_Xdegree = I_X_Degree
                TrueI_Qdegree = Q_X_Degree1

            if ((Q_X_token1 >= Q_X_Degree - 5) and (Q_X_token1 <= Q_X_Degree + 5)):

                TrueI_Xdegree = I_X_Degree1
                TrueI_Qdegree = Q_X_Degree
            elif ((Q_X_token1 >= Q_X_Degree1 - 5) and (Q_X_token1 <= Q_X_Degree1 + 5)):
                TrueI_Xdegree = I_X_Degree1
                TrueI_Qdegree = Q_X_Degree1

            print("TrueI_Xdegree = %3.2f °" % TrueI_Xdegree, "TrueI_Qdegree   %3.2f °" % TrueI_Qdegree)
            if(TrueI_Xdegree < TrueIdegree):
                X = TrueI_Xdegree + 360 - TrueIdegree
            else:
                X = TrueI_Xdegree -TrueIdegree
            print("△ s= %3.2f °"% X)
           # print(math.atan( YsinYcos[0].real) /absYsinCos)
            #print( math.atan( YsinYcos[101].imag/ YsinYcos[101].real)  ,math.asin( YsinYcos[102].imag/ YsinYcos[102].real ) )

            print("\n")
            pl.title('FFT')
            pl.ylabel('dBm')
            pl.xlabel('Frequency (MHz)')
            pl.yticks(Yticks)

            pl.pause(0.01)
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))