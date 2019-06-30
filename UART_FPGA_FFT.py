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

    fs = 25  # 采样频率
    N = 2048  # 采样点数
    N_HALF = 1024 #
    df = fs / (N - 1)  # 分辨率

    N_2MHZ = int(round( 2/ df, 0))# Lo= 2Mhz 点的位置
    N_4MHZ = int(round( 4/ df, 0))


    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    Yticks = np.arange(-150, 10, 10)


    Frequency = 200
    while True:
        Frequency = Frequency + 10
        if(Frequency > 4200):
            Frequency = 200
        SendMsg = struct.pack('<BBI', 0xFE, 0x03, Frequency * 1000)  # 设置1000MHz采样
        SerialPort.write(SendMsg)
        time.sleep(0.05)
        SendMsg = struct.pack('<BBBBBB', 0xFE, 0x01, 0x00, 0x00, 0x00, 0x00) #20Mhz
        SerialPort.write(SendMsg)
        XCosValue = []
        LoCosValue = []
        LoSinValue = []
        startMs = PrintMstime()

        for i in range(   N  ):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(4)
            Vpp = ( struct.unpack('<H', byte[0:2])[0] -2048)/2048.0
            #Vpp = math.cos((byte[3]) / 100 * 2 * math.pi  + 0.25* math.pi)
            LoSinVpp =  math.cos( byte[2]/100 *2* math.pi  ) # 2pi*k  FPGA内计数
            LoCosVpp =  math.cos( byte[3]/100 *2* math.pi )
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
            absYsinCos = [20 * math.log10(np.abs(x) + 0.0000001) for x in I_Xvalue]


            pl.clf() #清楚画布上的内容
            pl.plot(f[0:N_HALF], absY[0:N_HALF],'-b') #[0:N_HALF]  只显示一半即可
            #pl.plot(f[0:N_HALF], absYsinCos[0:N_HALF], '-g')
            '''
            n = 0
            for n in range(N_HALF):
                if(XCosValue[n] < 0.05 and XCosValue[n] >= 0 and XCosValue[n+1] > XCosValue[n]):
                    break
            pl.plot(XCosValue[n:n+100])'''



            I_acrcos = I_value[N_2MHZ].real / (np.abs(I_value[N_2MHZ]))
            Q_acrcos = Q_value[N_2MHZ].real / (np.abs(I_value[N_2MHZ] ))
            X_acrcos = X_value[N_2MHZ].real / (np.abs(X_value[N_2MHZ] ))
            I_Xacrcos = I_Xvalue[0].real/ (1.07* np.abs(X_value[N_2MHZ] ))
            Q_Xacrcos = Q_Xvalue[0].real/ (1.07 * np.abs(X_value[N_2MHZ] ))

            print(np.abs(X_value[N_2MHZ] ))
            print(I_Xacrcos, Q_Xacrcos )
            if(I_acrcos < -1 ):
                I_acrcos = -1
            if(Q_acrcos < -1 ):
                Q_acrcos = -1
            if(I_acrcos > 1 ):
                I_acrcos = 1
            if(Q_acrcos > 1 ):
                Q_acrcos = 1

            if(I_Xacrcos < -1 ):
                I_Xacrcos = -1
            if(Q_Xacrcos < -1 ):
                Q_Xacrcos = -1
            if(I_Xacrcos > 1 ):
                I_Xacrcos = 1
            if(Q_Xacrcos > 1 ):
                Q_Xacrcos = 1

            I_Degree = round( (math.acos(  I_acrcos ) / math.pi * 180), 2)
            Q_Degree = round( (math.acos( Q_acrcos ) / math.pi * 180), 2)
            X_Degree =  round( (math.acos(X_acrcos ) / math.pi * 180), 2)
            I_X_Degree = round((math.acos(I_Xacrcos) / math.pi * 180), 2)
            Q_X_Degree = round((math.acos(Q_Xacrcos) / math.pi * 180), 2)

            I_Degree1 = 360 - I_Degree

            print("I Degree= %3.2f °" % I_Degree ,"   %3.2f °" % I_Degree1  )

            Q_Degree1 = 360 - Q_Degree
            print( "Q Degree= %3.2f °" % (Q_Degree), "   %3.2f °" % Q_Degree1 )

            print("X_Degree = %3.2f °" % (X_Degree), "   %3.2f °" % (360 - X_Degree))

            print("I_X_Degree = %3.2f °" % (I_X_Degree), "   %3.2f °" % (360 - I_X_Degree) )

            print("Q_X_Degree = %3.2f °" % (Q_X_Degree), "   %3.2f °" % (360 - Q_X_Degree) )

           # print(math.atan( YsinYcos[0].real) /absYsinCos)
            #print( math.atan( YsinYcos[101].imag/ YsinYcos[101].real)  ,math.asin( YsinYcos[102].imag/ YsinYcos[102].real ) )

            print("\n")
            pl.title( 'FFT %d MHZ '%Frequency+" RL(dB)= %3.2f"%absY[N_2MHZ])
            pl.ylabel('dBm')
            pl.xlabel('Frequency (MHz)')
            pl.yticks(Yticks)

            pl.pause(0.01)
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))