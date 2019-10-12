# this file used accumulate method

import time
import threading
import struct

import numpy as np
import pylab as pl
import math
import skrf
from skrf import Network, Frequency
from scipy import signal
from VNACalibrate import OnePortCreatIdealFile ,OnePortCreatMesureFile,Cal_Display
from VNADataRequest import  VNA_DEV as VNA
#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523
vna = VNA()

###****************##########
fs = 24  # 采样频率
N = 4080  # 采样点数
N_HALF = 1200  #
DISPLAY_MODE = 0  # 1 wave, 0 spectrum
CALIBRATION_MODE = True
df = fs / (N - 1)  # 分辨率

PORT_SEL = 0 # 0: Port1 ,  1 : port2
REFLECT_SEL = 0 # 0: Port1 Reflect,   1: Port2 Reflect
IDEAL_FILE_PAHT = 'measured/ideal/'
MESURE_FILE_PAHT = 'measured/'

def PrintMstime():
    t = time.time()
    return int(round(t * 1000))  # 毫秒级时间戳


def PrintSkrfFile(Mage, Vphs, FreqStart, FreqRate, FileName):
    MesureList = ['# MHz S MA R 50.0\n']
    File = open(FileName, 'w')
    File.write(MesureList[0])
    for size in range(len(Mage)):
        MesureList.append('%.4f   %.8f   %.4f \n' % (((FreqStart + FreqRate * size), Mage[size], Vphs[size])))
        File.write(MesureList[size + 1])
    File.closed

##计算幅度和相位, 并转换到360度
def CalImagePhase(I_ACC_Value,Q_ACC_Value):
    #print('I_ACC: %3.6f , Q_ACC: %3.6f ' % (I_ACC_Value, Q_ACC_Value))
    Phase= math.atan(Q_ACC_Value / I_ACC_Value)
    Image = np.abs(I_ACC_Value * 2 / math.cos(Phase) / N / 0x20000)
    #Image = math.sqrt( math.pow(I_ACC_Value/ N / 0x20000,2) + math.pow(Q_ACC_Value/ N / 0x20000,2) )
    PhaseInDegree = Phase / math.pi * 180

    if (Q_ACC_Value >= 0 and I_ACC_Value >= 0):
        targetPhase = PhaseInDegree
    elif (Q_ACC_Value >= 0 and I_ACC_Value < 0):
        targetPhase = 180 + PhaseInDegree
    elif (Q_ACC_Value < 0 and I_ACC_Value >= 0):
        targetPhase = 360 + PhaseInDegree
    else:
        targetPhase = 180 + PhaseInDegree
    return Image ,targetPhase #


def VNASampling(FileName, ApplayCalibration):

    WAVE_Yticks = np.arange(-1, 1.2, 0.2)

    FrequencyStart = 1500 # 目前最小频率 140Mhz
    FrequencyEnd =3500  # 最大设置4400
    FreqSwepStep = 3
    PWRlevelReset = 38
    RangSweep = []
    AbsYSweepForward = []
    AbsYSweepReflect = []
    SkImage = []

    PahseSweepForward = []
    PahseForward = 0
    ImageForwardDB = 0
    PahseSweepReflect = []
    Frequency = FrequencyStart
    PWRlevel = PWRlevelReset
    vna.SetRF_PWRlevel(PWRlevel)  # set RF output level bit[5:0]
    vna.SetSamplingCKL(0)  # set sampling clock, first Byte H4

    vna.SelectPort(PORT_SEL,  REFLECT_SEL)# (1 = Port2,1 = Port Reflect)
    vna.SetRF_LO_FRQ(Frequency)

    if(ApplayCalibration is True ):
        OnePortCreatIdealFile(IDEAL_FILE_PAHT, FrequencyStart, FrequencyEnd, FreqSwepStep) # 创建理论参考文件
        OnePortCreatMesureFile(MESURE_FILE_PAHT, FrequencyStart, FrequencyEnd, FreqSwepStep)
    #time.sleep(0,5)
    while True:
        #time.sleep(0.01)
        if (round(Frequency,1) >= FrequencyEnd):  # 显示RL 的曲线
            n_len = len(AbsYSweepForward)
            print(round(Frequency,1),n_len)
            if ( n_len == int((round(Frequency,1) - FrequencyStart) / FreqSwepStep)):
                pl.clf()  # 清楚画布上的内容
                pl.plot(RangSweep, AbsYSweepForward)  # fist scan
                pl.plot(RangSweep, AbsYSweepReflect)
                pl.title('S11 RL(dB)')
                pl.ylabel('dB')
                pl.xlabel('Frequency (MHz)')
                pl.yticks(np.arange(-60, 20, 5))
                pl.grid(axis='y', linestyle='--')
                pl.show()
                AbsYSweep = []

                pl.clf()  # 清楚画布上的内容
                # pl.plot(RangSweep,PahseSweepForward)#显示相位信息

                # SubPhase = np.subtract(np.array(PahseSweepReflect),np.array(PahseSweepForward))
                pl.plot(RangSweep, PahseSweepReflect)
                pl.title('S11 RP(°)')
                pl.xlabel('Frequency (MHz)')
                pl.ylabel('°')
                pl.yticks(np.arange(-180, 200, 30))
                pl.show()

                # 创建skrf 文件
                PrintSkrfFile(SkImage, PahseSweepReflect, FrequencyStart, FreqSwepStep,FileName)
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

                ## run, and apply calibration to a DUT and display
                if ApplayCalibration is True:
                    Cal_Display(FileName)
                else:
                    break
            else:
                pl.show()
            Frequency = FrequencyStart
            PWRlevel = PWRlevelReset
            AbsYSweepForward = []
            AbsYSweepReflect = []
            PahseSweepForward = []
            PahseSweepReflect = []
            RangSweep = []
            SkImage = []
            vna.SetRF_PWRlevel(PWRlevel)


        vna.SetRF_LO_FRQ(Frequency)
        time.sleep(0.01)


        vna.StartSamp()


        XCosValue = []
        # startMs = PrintMstime()


        while vna.SerialPort.inWaiting() == 0:
            pass
        byte = vna.SerialPort.read(16)

        IF_I_ACC = struct.unpack('<i', byte[0:4])[0]
        IF_Q_ACC =  struct.unpack('<i', byte[4:8])[0]
        IF_I_ACC_R = struct.unpack('<i', byte[8:12])[0]
        IF_Q_ACC_R = struct.unpack('<i', byte[12:16])[0]
        if (IF_I_ACC != 0):

            # I_Q = np.multiply(np.array(LoSinValue),np.array( LoCosValue))

            Image_F , PahseForward = CalImagePhase(IF_I_ACC, IF_Q_ACC)
            Image_R , PhaseReflect = CalImagePhase(IF_I_ACC_R, IF_Q_ACC_R)
            print("%.1f MHz "%Frequency,"Image_F= ", Image_F,"Image_R= ", Image_R, "\n")
            absY_F = 20 * math.log10(Image_F)  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率
            absY_R = 20 * math.log10(Image_R)

            if (DISPLAY_MODE == 1):

                pl.clf()  # 清楚画布上的内容
                n = 0
                for n in range(N_HALF):
                    if (XCosValue[n] < 0.05 and XCosValue[n] >= 0 and XCosValue[n + 1] > XCosValue[n]):
                        break
                pl.plot(XCosValue[n:n + 100])
                pl.title('WaveDisplay %d MHZ ' % Frequency + " RL(dB)= %3.2f" % absY_F)
                pl.yticks(WAVE_Yticks)
                pl.xlabel('Time (ns)')
                pl.pause(0.08)
            ''''// end if  '''

            #print('%d MHZ  %3.5f  %3.5f\n' % (Frequency, PhasePosition, targetPhase))

            AbsYSweepForward.append(absY_F)  # 幅度in dB
            PahseSweepForward.append(PahseForward)  # 相位

            AbsYSweepReflect.append(absY_R)
            SubPha = PhaseReflect - PahseForward
            if (SubPha < 0):
                   SubPha = 360 + SubPha
            if (SubPha > 180):
                    SubPha = (SubPha - 180) - 180
            SkImage.append(Image_R)  # skrf 幅度
            PahseSweepReflect.append(SubPha)
            RangSweep.append(Frequency)

            Frequency = Frequency + FreqSwepStep
              #time.sleep(0.05)
'''
            if(absY_F > -14.5 and  PWRlevel > 0):
                PWRlevel = PWRlevel - 1
                vna.SetRF_PWRlevel(PWRlevel)
                continue

            elif(absY_F < -15.5 and PWRlevel < 63):
                PWRlevel = PWRlevel + 1
                vna.SetRF_PWRlevel(PWRlevel)
                continue
'''
            # print(time.time())
            # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
if __name__ == '__main__':
    #display and applay calibration
    VNASampling('MesureOut.s1p',True)