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

    fs = 24  # 采样频率
    N = 4000  # 采样点数
    N_HALF = 2000 #
    DISPLAY_MODE = 0# 1 wave, 0 spectrum
    df = fs / (N - 1)  # 分辨率  m'n

    N_2MHZ = int(round( 2/ df, 0)) # Lo= 2Mhz 点的位置
    N_4MHZ = int(round( 4/ df, 0))


    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    FFT_Yticks = np.arange(-150, 10, 10)
    WAVE_Yticks = np.arange(-1, 1.2, 0.2)


    FrequencyStart = 140
    FrequencyEnd = 4000
    FreqSwepStep = 10
    RangSweep = []
    AbsYSweep_F = []
    AbsYSweep_R = []
    PahseSweep_F = []
    PahseSweep_R = []
    Frequency = FrequencyStart

    '''
    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x04, 0x00, 0x00, 0x00, 0x00)  # set sampling clock, first Byte H4
    SerialPort.write(SendMsg)
    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05,0x00, 0x00, 0x00, 0x00)  # set forward or reflection
    SerialPort.write(SendMsg)'''
    while True:
        Frequency = Frequency + FreqSwepStep
        if(Frequency >= FrequencyEnd): # 显示RL 的曲线
            print(len(AbsYSweep_F))
            if(len(AbsYSweep_F )== len(AbsYSweep_R )):
                pl.clf()  # 清楚画布上的内容
                pl.plot(RangSweep,AbsYSweep_F ) # fist scan
                pl.plot(RangSweep,AbsYSweep_R) # secound scan
                pl.title( 'S11 RL(dB)')
                pl.ylabel('dB')
                pl.xlabel('Frequency (MHz)')
                pl.yticks( np.arange(-60, 10, 10))
                pl.show()
                AbsYSweep_F = []
                AbsYSweep_R = []

                pl.clf()  # 清楚画布上的内容
                #pl.plot(RangSweep,PahseSweep[0:int((FrequencyEnd - FrequencyStart)/FreqSwepStep)])#显示相位信息
                #pl.plot(RangSweep, PahseSweep[int((FrequencyEnd - FrequencyStart) / FreqSwepStep):])

                SubPhase = np.subtract(np.array(PahseSweep_R),np.array(PahseSweep_F))
                pl.plot(RangSweep,SubPhase)
                pl.title( 'S11 RP(°)')
                pl.xlabel('Frequency (MHz)')
                pl.ylabel('°')
                pl.yticks( np.arange(0, 370, 30))
                pl.show()
                PahseSweep_F = PahseSweep_R = []#清除保存的相位


            else:
                pl.show()
            Frequency = FrequencyStart+ FreqSwepStep
            RangSweep = []
        RangSweep.append(Frequency)
        SendMsg = struct.pack('<BBI', 0xFE, 0x03, Frequency * 1000)  # 设置1000MHz采样
        SerialPort.write(SendMsg)
        time.sleep(0.01)
        SendMsg = struct.pack('<BBBBBB', 0xFE, 0x11, 0x00, 0x00, 0x00, 0x00) #start ADC
        SerialPort.write(SendMsg)
        XCosValue = []
        LoCosValue = []
        LoSinValue = []
        startMs = PrintMstime()
        ReflectXCosValue= []

        for i in range(   N  ):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(8)
            ForworVpp = ( struct.unpack('<H', byte[0:2])[0] -2048)/2048.0 # byte[0] + byte[1] reflect
            ReflectVpp = ( struct.unpack('<H', byte[2:4])[0] -2048)/2048.0 # byte[2] + byte[3] forward
            #Vpp = math.cos((byte[2]) / 24 * 2 * math.pi  + 0* math.pi)
            LoSinVpp =  math.cos( byte[4]/24 *2* math.pi  ) # 2pi*k  FPGA内计数
            LoCosVpp =  math.cos( byte[5]/24 *2* math.pi )

            XCosValue.append(ForworVpp)  # uints = mV, right lead 4bits
            ReflectXCosValue.append(ReflectVpp)
            LoSinValue.append(LoSinVpp)
            LoCosValue.append(LoCosVpp)
        endMs = PrintMstime()
        #print(endMs - startMs)

        if( len(XCosValue) ==   N ):


            FORWARD_I_X = np.multiply(np.array(LoSinValue),np.array( XCosValue))
            FORWARD_Q_X = np.multiply(np.array(LoCosValue), np.array( XCosValue ))

            FORWARD_I_X_ACC = np.sum(FORWARD_I_X)/N
            FORWARD_Q_X_ACC =  np.sum(FORWARD_Q_X)/N


            print(FORWARD_I_X_ACC , FORWARD_Q_X_ACC)

            FORWARD_PhasePosition = math.atan(-FORWARD_Q_X_ACC / FORWARD_I_X_ACC)
            FORWARD_Image = np.abs(FORWARD_I_X_ACC * 2 /( math.cos(FORWARD_PhasePosition)) )
            FORWARD_ImageDb = 20 * math.log10(FORWARD_Image)
            print("FORWARD_Image_dB= %2.2f"%(FORWARD_ImageDb) )

            REFLECT_I_X = np.multiply(np.array(LoSinValue),np.array( ReflectXCosValue))
            REFLECT_Q_X = np.multiply(np.array(LoCosValue), np.array( ReflectXCosValue ))
            #I_Q = np.multiply(np.array(LoSinValue),np.array( LoCosValue))
            REFLECT_I_X_ACC = np.sum(REFLECT_I_X)/N
            REFLECT_Q_X_ACC =  np.sum(REFLECT_Q_X)/N
            print(REFLECT_I_X_ACC , REFLECT_Q_X_ACC)
            REFLECT_PhasePosition = math.atan(-REFLECT_Q_X_ACC / REFLECT_I_X_ACC)
            REFLECT_Image = np.abs(REFLECT_I_X_ACC * 2 /( math.cos(REFLECT_PhasePosition)) )
            REFLECT_ImageDb =  20 * math.log10(REFLECT_Image)

            print("REFLECT_Image_dB= %2.2f"%(REFLECT_ImageDb))

            AbsYSweep_F.append(FORWARD_ImageDb)
            AbsYSweep_R.append(REFLECT_ImageDb)
            PahseSweep_F.append(FORWARD_PhasePosition)
            PahseSweep_R.append(REFLECT_PhasePosition)
            X_value = np.fft.fft(XCosValue) * 2 / N  # *2/N 反映了FFT变换的结果与实际信号幅值之间的关系
            Reflect_FFT_Value =  np.fft.fft(ReflectXCosValue) * 2 / N



            absY = [20*math.log10(np.abs(x)+ 0.0000001)  for x in X_value]  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率

            Reflect_FFT_ValueAbs = [20*math.log10(np.abs(x)+ 0.0000001)  for x in Reflect_FFT_Value]#反射接收ADC


            pl.clf() #清楚画布上的内容

            if(DISPLAY_MODE == 0):
                pl.plot(f[0:N_HALF], absY[0:N_HALF],'-b') #[0:N_HALF]  只显示一半即可
                pl.plot(f[0:N_HALF], Reflect_FFT_ValueAbs[0:N_HALF], '-y')

                #pl.plot(f[0:N_HALF], absYsinCos[0:N_HALF], '-g')

                pl.title( 'FFT %d MHZ '%Frequency+"For_RL(dB)= %3.2f"%absY[N_2MHZ] + "REF_DB= %3.2f"%Reflect_FFT_ValueAbs[N_2MHZ])
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



            pl.pause(0.01)
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))