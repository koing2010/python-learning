# this file used accumulate method
import serial
import time
import threading
import struct

import numpy as np
import pylab as pl
import math
import  skrf
from skrf import Network, Frequency
from scipy import signal
from VNACalibrate import Cal_Display

#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523
SerialPort = serial.Serial('com27')

def PrintMstime():
    t = time.time()
    return int(round(t * 1000))  # 毫秒级时间戳
def PrintSkrfFile(Mage, Vphs, FreqStart, FreqRate):
    MesureList= ['# MHz S MA R 50.0\n']
    File = open('MesureOut.s1p','w')
    File.write(MesureList[0])
    for size in range(len(Mage)):
        MesureList.append( '%.4f   %.8f   %.4f \n'%(((FreqStart+FreqRate*size),Mage[size], Vphs[size])))
        File.write(MesureList[size+1])
    File.closed

if __name__ == '__main__':

    fs = 24  # 采样频率
    N = 2400  # 采样点数
    N_HALF = 1200 #
    DISPLAY_MODE = 0 # 1 wave, 0 spectrum
    df = fs / (N - 1)  # 分辨率

    N_2MHZ = int(round( 2/ df, 0))# Lo= 2Mhz 点的位置
    N_4MHZ = int(round( 4/ df, 0))


    f = [round(df * n, 5) for n in range(0, N)]  # 构建频率数组
    FFT_Yticks = np.arange(-150, 20, 10)
    WAVE_Yticks = np.arange(-1, 1.2, 0.2)


    FrequencyStart = 1000
    FrequencyEnd = 4000
    FreqSwepStep = 10
    RangSweep = []
    ForwardOrReflect = True
    AbsYSweepForward = []
    AbsYSweepReflect = []
    SkImage = []

    PahseSweepForward = []
    PahseForward = 0
    PahseSweepReflect = []
    Frequency = FrequencyStart

    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x04, 0x00, 0x00, 0x00, 0x00)  # set sampling clock, first Byte H4
    SerialPort.write(SendMsg)
    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x06,0x01, 0x00, 0x00, 0x00)  # set RF output level bit[5:0]
    SerialPort.write(SendMsg)
    SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05,0x01, 0x00, 0x00, 0x00)  # set forward or reflection  level bit[0][0] = 1 reflect 0
    SerialPort.write(SendMsg)
    while True:

        if (ForwardOrReflect is True):
            ##Forward
            SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05, 0x01, 0x00, 0x00, 0x00)  # set forward or reflection  level bit[0][0] = 1 reflect 0
        else:
            ## Reflectoin
            SendMsg = struct.pack('<BBBBBB', 0xFE, 0x05, 0x00, 0x00, 0x00,0x00)  # set forward or reflection  level bit[0][0] = 1 reflect 0
        SerialPort.write(SendMsg)

        if(Frequency >= FrequencyEnd): # 显示RL 的曲线

            if(len(AbsYSweepForward )== int((FrequencyEnd - FrequencyStart)/FreqSwepStep)):
                pl.clf()  # 清楚画布上的内容
                pl.plot(RangSweep,AbsYSweepForward) # fist scan
                pl.plot(RangSweep,AbsYSweepReflect)
                pl.title( 'S11 RL(dB)')
                pl.ylabel('dB')
                pl.xlabel('Frequency (MHz)')
                pl.yticks( np.arange(-60, 20, 10))
                pl.show()
                AbsYSweep = []

                pl.clf()  # 清楚画布上的内容
                #pl.plot(RangSweep,PahseSweepForward)#显示相位信息

                #SubPhase = np.subtract(np.array(PahseSweepReflect),np.array(PahseSweepForward))
                pl.plot(RangSweep,PahseSweepReflect)
                pl.title( 'S11 RP(°)')
                pl.xlabel('Frequency (MHz)')
                pl.ylabel('°')
                pl.yticks( np.arange(-180, 200, 30))
                pl.show()

                #创建skrf 文件
                PrintSkrfFile(SkImage, PahseSweepReflect, FrequencyStart, FreqSwepStep)
                '''
                ring_slot = Network('MesureOut.s1p')
                print(ring_slot)
  
                ring_slot.plot_s_db() # 幅度曲线
                pl.show()
                ring_slot.plot_s_deg()#相位曲线
                pl.show()

                ring_slot.plot_s_smith()#史密斯圆
                pl.show()
                '''

                Cal_Display('MesureOut.s1p')
            else:
                pl.show()
            Frequency = FrequencyStart
            AbsYSweepForward = []
            AbsYSweepReflect = []
            PahseSweepForward = []
            PahseSweepReflect = []
            RangSweep = []
            SkImage = []

        if(ForwardOrReflect is True):
            RangSweep.append(Frequency)
            SendMsg = struct.pack('<BBI', 0xFE, 0x03, Frequency * 1000)  # 设置1000MHz采样
            SerialPort.write(SendMsg)

        time.sleep(0.06)
        SendMsg = struct.pack('<BBBBBB', 0xFE, 0x01, 0x00, 0x00, 0x00, 0x00) #start ADC
        SerialPort.write(SendMsg)
        XCosValue = []
        IF_I_Value = []
        IF_Q_Value = []
        IF_I_ACC = 0
        IF_Q_ACC = 0
        IF_ACC = 0
        #startMs = PrintMstime()

        for i in range(   N  ):
            while SerialPort.inWaiting() == 0:
                pass
            byte = SerialPort.read(4)
            Vpp = ( struct.unpack('<H', byte[0:2])[0] -2048)/2048.0
            #Vpp = math.sin((byte[2]) / 24.0  *2* math.pi  +1.25*math.pi)
            LoSinVpp =  math.sin( byte[2]/24.0 *2* math.pi  ) # 2pi*k  FPGA内计数
            LoCosVpp =  math.sin( byte[3]/24.0 *2* math.pi )
            XCosValue.append(Vpp)  # uints = mV, right lead 4bits
            IF_I_ACC = IF_I_ACC + LoSinVpp*Vpp
            IF_Q_ACC = IF_Q_ACC + LoCosVpp*Vpp
        #endMs = PrintMstime()
        #print(endMs - startMs)

        if( len(XCosValue) ==   N ):

            #I_Q = np.multiply(np.array(LoSinValue),np.array( LoCosValue))
            IF_I_ACC = IF_I_ACC/N
            IF_Q_ACC = IF_Q_ACC/N
            print('%3.6f   %3.6f \n' % (IF_I_ACC, IF_Q_ACC))
            PhasePosition=  math.atan(-IF_Q_ACC/IF_I_ACC)
            Image = np.abs(IF_I_ACC*2/math.cos(PhasePosition))
            absY = 20 * math.log10(Image)  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率

            if (DISPLAY_MODE == 1):

                pl.clf()  # 清楚画布上的内容
                n = 0
                for n in range(N_HALF):
                    if(XCosValue[n] < 0.05 and XCosValue[n] >= 0 and XCosValue[n+1] > XCosValue[n]):
                        break
                pl.plot(XCosValue[n:n+100])
                pl.title( 'WaveDisplay %d MHZ '%Frequency+" RL(dB)= %3.2f"%absY)
                pl.yticks(WAVE_Yticks)
                pl.xlabel('Time (ns)')
                pl.pause(0.08)
            ''''// end if  '''

            PhasePosition = PhasePosition/math.pi * 180
            targetPhase = 0
            if(IF_I_ACC >= 0 and IF_Q_ACC >= 0):
                targetPhase = PhasePosition
            elif(IF_I_ACC < 0 and IF_Q_ACC > 0):
                targetPhase = 180 + PhasePosition
            elif(IF_I_ACC < 0 and IF_Q_ACC < 0):
                targetPhase = 180 + PhasePosition
            else:
                targetPhase  = 360 + PhasePosition

            print('%d MHZ  %3.5f  %3.5f\n'%(Frequency, PhasePosition,targetPhase) )
            if (ForwardOrReflect is True):
                ForwardOrReflect = False
                AbsYSweepForward.append(absY) #幅度
                PahseSweepForward.append(targetPhase)# 相位
                PahseForward = targetPhase
            else:
                ForwardOrReflect = True
                AbsYSweepReflect.append(absY)
                SubPha = PahseForward - targetPhase
                if(SubPha < 0):
                    SubPha = 360 + SubPha
                if(SubPha > 180):
                    SubPha = (SubPha -180)-180
                SkImage.append(Image)   #skrf 幅度
                PahseSweepReflect.append(SubPha)
                Frequency = Frequency + FreqSwepStep
            #print(time.time())
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
