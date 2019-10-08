import struct
import time

import math
import numpy as np
import pylab as pl
import serial

#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523
SerialPort = serial.Serial('com27')

def PrintMstime():
    t = time.time()
    return int(round(t * 1000))  # 毫秒级时间戳

if __name__ == '__main__':

    fs = 25  # 采样频率
    N = 2400  # 采样点数
    N_HALF = 1200 #
    DISPLAY_MODE = 1# 1 wave, 0 spectrum
    df = fs / (N - 1)  # 分辨率

    N_2MHZ = int(round( 2/ df, 0))# Lo= 2Mhz 点的位置
    N_4MHZ = int(round( 4/ df, 0))


    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    FFT_Yticks = np.arange(-150, 10, 10)
    WAVE_Yticks = np.arange(-1, 1.2, 0.2)


    FrequencyStart = 150
    FrequencyEnd = 4000
    FreqSwepStep = 10
    RangSweep = []
    AbsYSweep = []
    PahseSweep = []
    Frequency = FrequencyStart

    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x04, 0x00, 0x00, 0x00, 0x00)  # set sampling clock, first Byte H4
    SerialPort.write(SendMsg)
    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x06, 35, 0x00, 0x00, 0x00)  # set RF output level bit[5:0]
    SerialPort.write(SendMsg)
    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05,0x01, 0x00, 0x00, 0x00)  # set forward or reflection  level bit[0][0] = 1 reflect 0
    SerialPort.write(SendMsg)
    while True:
        Frequency = Frequency + FreqSwepStep
        if(Frequency > FrequencyEnd): # 显示RL 的曲线
            print(len(AbsYSweep))
            if(len(AbsYSweep )== int((FrequencyEnd - FrequencyStart)*2/FreqSwepStep)):
                pl.clf()  # 清楚画布上的内容
                pl.plot(RangSweep,AbsYSweep[0:int((FrequencyEnd - FrequencyStart)/FreqSwepStep) ]) # fist scan
                pl.plot(RangSweep,AbsYSweep[int((FrequencyEnd - FrequencyStart)/FreqSwepStep):]) # secound scan
                pl.title( 'S11 RL(dB)')
                pl.ylabel('dB')
                pl.xlabel('Frequency (MHz)')
                pl.yticks( np.arange(-60, 10, 10))
                pl.show()
                AbsYSweep = []

                pl.clf()  # 清楚画布上的内容
                #pl.plot(RangSweep,PahseSweep[0:int((FrequencyEnd - FrequencyStart)/FreqSwepStep)])#显示相位信息
                #pl.plot(RangSweep, PahseSweep[int((FrequencyEnd - FrequencyStart) / FreqSwepStep):])

                SubPhase = np.subtract(np.array(PahseSweep[0:int((FrequencyEnd - FrequencyStart)/FreqSwepStep)]),np.array(PahseSweep[int((FrequencyEnd - FrequencyStart) / FreqSwepStep):]))
                pl.plot(RangSweep,SubPhase)
                pl.title( 'S11 RP(°)')
                pl.xlabel('Frequency (MHz)')
                pl.ylabel('°')
                pl.yticks( np.arange(0, 370, 30))
                pl.show()
                PahseSweep = []#清除保存的相位
                SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05, 0x01, 0x00, 0x00,0x00)  # set forward or reflection  level bit[0][0] = 1 reflect 0

            else:
                pl.show()
                SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05, 0x00, 0x00, 0x00,0x00)  # set forward or reflection  level bit[0][0] = 1 reflect 0
            SerialPort.write(SendMsg)
            Frequency = FrequencyStart+ FreqSwepStep
            RangSweep = []
        RangSweep.append(Frequency)
        SendMsg = struct.pack('<BBI', 0xFE, 0x03, Frequency * 1000)  # 设置1000MHz采样
        SerialPort.write(SendMsg)
        time.sleep(0.1)
        SendMsg = struct.pack('<BBBBBB', 0xFE, 0x11, 0x00, 0x00, 0x00, 0x00) #start ADC
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
            #Vpp = math.cos((byte[2]) / 24 * 2 * math.pi  + 0* math.pi)
            LoSinVpp =  math.cos( byte[2]/24 *2* math.pi  ) # 2pi*k  FPGA内计数
            LoCosVpp =  math.cos( byte[3]/24 *2* math.pi )
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
            AbsYSweep.append(absY[N_2MHZ])

            pl.clf() #清楚画布上的内容

            if(DISPLAY_MODE == 0):
                pl.plot(f[0:N_HALF], absY[0:N_HALF],'-b') #[0:N_HALF]  只显示一半即可
                #pl.plot(f[0:N_HALF], absYsinCos[0:N_HALF], '-g')

                pl.title( 'FFT %d MHZ '%Frequency+" RL(dB)= %3.2f"%absY[N_2MHZ])
                pl.ylabel('dBm')
                pl.xlabel('Frequency (MHz)')
                pl.yticks(FFT_Yticks)
            elif (DISPLAY_MODE == 1):
                n = 0
                for n in range(N_HALF):
                    if(XCosValue[n] < 0.05 and XCosValue[n] >= 0 and XCosValue[n+1] > XCosValue[n]):
                        break
                pl.plot(XCosValue[n:n+96])
                pl.title( 'WaveDisplay %d MHZ '%Frequency+" RL(dB)= %3.2f"%absY[N_2MHZ])
                pl.yticks(WAVE_Yticks)
                pl.xlabel('Time (ns)')
            ''''// end if  '''



            I_acrcos = I_value[N_2MHZ].real / (np.abs(I_value[N_2MHZ]))
            Q_acrcos = Q_value[N_2MHZ].real / (np.abs(I_value[N_2MHZ] ))
            X_acrcos = X_value[N_2MHZ].real / (np.abs(X_value[N_2MHZ] ))
            I_Xacrcos = I_Xvalue[0].real/ (1.0* np.abs(X_value[N_2MHZ] ))
            Q_Xacrcos = Q_Xvalue[0].real/ (1.0 * np.abs(X_value[N_2MHZ] ))
            '''
            print(np.abs(X_value[N_2MHZ] ))
            print(I_Xacrcos, Q_Xacrcos )
            '''
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
            I_X_Degree_pol =  (360 - I_X_Degree)

            PhasePosition = 0
            if( (I_X_Degree - Q_X_Degree >= 83 and I_X_Degree - Q_X_Degree <= 90) or ((I_X_Degree - (360 - Q_X_Degree) >= 83 and I_X_Degree - (360 - Q_X_Degree) <= 90))):
                #print("1->%3.2f "% I_X_Degree)
                PhasePosition = I_X_Degree

            elif( (I_X_Degree_pol - Q_X_Degree >= 83 and I_X_Degree_pol - Q_X_Degree <= 90) or ((I_X_Degree_pol - (360 - Q_X_Degree) >= 83 and I_X_Degree_pol - (360 - Q_X_Degree) <= 90))):
                #print("2->%3.2f "% I_X_Degree_pol)
                PhasePosition = I_X_Degree_pol
            elif( (I_X_Degree + Q_X_Degree >= 83 and I_X_Degree + Q_X_Degree <= 90) or ( I_X_Degree + (360 - Q_X_Degree) >= 83 and I_X_Degree + (360 - Q_X_Degree)) <= 90):
                #print("3->%3.2f "% I_X_Degree)
                PhasePosition = I_X_Degree
            elif( (I_X_Degree_pol + Q_X_Degree >= 83 and I_X_Degree_pol + Q_X_Degree <= 90) or ( I_X_Degree_pol + (360 - Q_X_Degree) >= 83 and I_X_Degree_pol + (360 - Q_X_Degree)) <= 90):
                #print("3->%3.2f "% I_X_Degree_pol)
                PhasePosition = I_X_Degree_pol

            print('%d MHZ  %3.2f \n'%(Frequency, PhasePosition) )
            PahseSweep.append(PhasePosition)
            pl.pause(0.01)
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))