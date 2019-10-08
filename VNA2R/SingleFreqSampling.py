import struct
import time

import math
import numpy as np
import pylab as pl
import serial

SerialPort = serial.Serial('com27')

def PrintMstime():
    t = time.time()
    return int(round(t * 1000))  # 毫秒级时间戳

if __name__ == '__main__':

    fs = 40  # 采样频率
    N = 1200  # 采样点数
    N_HALF = 600 #
    DISPLAY_MODE = 0# 1 wave, 0 spectrum
    df = fs / (N - 1)  # 分辨率

    N_2MHZ = int(round( 2/ df, 0))# Lo= 2Mhz 点的位置
    N_4MHZ = int(round( 4/ df, 0))


    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    FFT_Yticks = np.arange(-150, 10, 10)
    WAVE_Yticks = np.arange(-1, 1.2, 0.2)


    Frequency = 2500

    FreqSwepStep = 0

    FrequencyEnd = 4400

    SendMsg = struct.pack('<BBI', 0xFE, 0x03, Frequency * 1000)  # 设置1000MHz采样
    SerialPort.write(SendMsg)

    while True:
        if(  FreqSwepStep != 0 and Frequency <= FrequencyEnd):
            Frequency = Frequency + FreqSwepStep
            SendMsg = struct.pack('<BBI', 0xFE, 0x03,int( Frequency * 1000))  # 设置1000MHz采样
            SerialPort.write(SendMsg)
            time.sleep(0.1)

        SendMsg = struct.pack('<BBBBBB', 0xFE, 0x11, 0x00, 0x00, 0x00, 0x00) #start ADC
        SerialPort.write(SendMsg)
        XCosValue = []
        LoCosValue = []
        LoSinValue = []
        startMs = PrintMstime()
        ReflectXCosValue= []
        for i in range( N ):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(4)
            ReflectVpp = ( struct.unpack('<H', byte[0:2])[0] -2048)/2048.0  # byte[0] + byte[1] reflect
            ForworVpp = ( struct.unpack('<H', byte[2:4])[0] -2048)/2048.0  # byte[2] + byte[3] forward
            #Vpp = math.cos((byte[2]) / 24 * 2 * math.pi  + 0* math.pi)
            byte = SerialPort.read(4)
            LoSinVpp =  math.cos( byte[0]/24 *2* math.pi  ) # 2pi*k  FPGA内计数
            LoCosVpp =  math.cos( byte[1]/24 *2* math.pi )
            XCosValue.append(ForworVpp )  # uints = mV, right lead 4bits
            ReflectXCosValue.append( ReflectVpp)


        if( len(XCosValue) ==   N ):
            X_value = np.fft.fft(XCosValue) * 2 / N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
            Reflect_FFT_Value =  np.fft.fft(ReflectXCosValue) * 2 / N




            absY = [20*math.log10(np.abs(x)+ 0.0000001)  for x in X_value]  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率


            Reflect_FFT_ValueAbs = [20*math.log10(np.abs(x)+ 0.0000001)  for x in Reflect_FFT_Value]#反射接收ADC


            pl.clf() #清楚画布上的内容

            if(DISPLAY_MODE == 0):
                pl.plot(f[0:N_HALF], absY[0:N_HALF],'-b') #[0:N_HALF]  只显示一半即可
                pl.plot(f[0:N_HALF], Reflect_FFT_ValueAbs[0:N_HALF], '-y')

                #pl.plot(f[0:N_HALF], absYsinCos[0:N_HALF], '-g')

                pl.title( 'FFT %4.1f MHZ '%Frequency+" RL(dB)= %3.2f"%Reflect_FFT_ValueAbs[N_2MHZ])
                pl.ylabel('dBm')
                pl.xlabel('Frequency (MHz)')
                pl.yticks(FFT_Yticks)
            elif (DISPLAY_MODE == 1):
                n = 0
                for n in range(N_HALF):
                   if(XCosValue[n] < 0.1 and XCosValue[n] >= 0 and XCosValue[n+1] > XCosValue[n]):
                       break
                pl.plot(XCosValue[n:n+ 120])
                pl.plot(ReflectXCosValue[n:n + 120])
                #pl.plot(XCosValue)
               # pl.plot(ReflectXCosValue)
                pl.title( 'WaveDisplay %d MHZ '%Frequency+" RL(dB)= %3.2f"%Reflect_FFT_ValueAbs[N_2MHZ])
                pl.yticks(WAVE_Yticks)
                pl.xlabel('Time (ns)')
            ''''// end if  '''
            pl.pause(0.01)




