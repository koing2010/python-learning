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


def PrintTouchSone_1port_File(Mage, Vphs, FreqStart, FreqRate, FileName):
    MesureList = ['# MHz S MA R 50.0\n']
    File = open(FileName+ '.s1p', 'w')
    File.write(MesureList[0])
    for size in range(len(Mage)):
        MesureList.append('%.4f   %.8f   %.4f \n' % (((FreqStart + FreqRate * size), Mage[size], Vphs[size])))
        File.write(MesureList[size + 1])
    File.closed

#创建 2 Port 文件
def PrintTouchSone_2port_File(Mage, Vphs, FreqStart, FreqRate, FileName, MA_Sxx):
    MesureList = ['# MHz S MA R 50.0\n']
    File = open(FileName+ '.s2p', 'w')
    File.write(MesureList[0])

    magS11 = 0
    angS11 = 0
    magS21 = 0
    angS21 = 0
    magS12 = 0
    angS12 = 0
    magS22 = 0
    angS22 = 0
    for size in range(len(Mage)):

        if(MA_Sxx == "S11"):
            magS11 =  Mage[size]
            angS11 =  Vphs[size]
        elif (MA_Sxx == "S21"):
            magS21 =  Mage[size]
            angS21 =  Vphs[size]
        elif (MA_Sxx == "S12"):
            magS12 =  Mage[size]
            angS12 =  Vphs[size]
        elif (MA_Sxx == "S22"):
            magS22 =  Mage[size]
            angS22 =  Vphs[size]

        MesureList.append('%.4f   %.8f   %.4f    %.8f   %.4f    %.8f   %.4f    %.8f   %.4f \n' % (((FreqStart + FreqRate * size),magS11,angS11,magS21,angS21, magS12 ,angS12 ,magS22, angS22 )))
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

#  设置频率  活得 IQ 计算 Aagnitude and Angle
def SamplingMagAngle(Frequency):
    vna.SetRF_LO_FRQ(Frequency)
    time.sleep(0.01)
    vna.StartSamp()
    while vna.SerialPort.inWaiting() == 0:
        pass
    byte = vna.SerialPort.read(16)

    IF_I_ACC = struct.unpack('<i', byte[0:4])[0]
    IF_Q_ACC = struct.unpack('<i', byte[4:8])[0]
    IF_I_ACC_R = struct.unpack('<i', byte[8:12])[0]
    IF_Q_ACC_R = struct.unpack('<i', byte[12:16])[0]
    Image_F, PahseForward = CalImagePhase(IF_I_ACC, IF_Q_ACC)
    Image_R, PhaseReflect = CalImagePhase(IF_I_ACC_R, IF_Q_ACC_R)

    return   Image_F, PahseForward ,Image_R, PhaseReflect
def VNASampling(FileName, ApplayCalibration):

    WAVE_Yticks = np.arange(-1, 1.2, 0.2)

    FrequencyStart = 2000 # 目前最小频率 140Mhz
    FrequencyEnd =3000  # 最大设置4400
    FreqSwepStep = 5
    PWRlevelReset = 38

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
        OnePortCreatMesureFile(MESURE_FILE_PAHT, FrequencyStart, FrequencyEnd, FreqSwepStep)# 提取SOL的测量文件
    #time.sleep(0,5)

    FreqRangSweep = np.arange(FrequencyStart, FrequencyEnd , FreqSwepStep)
    while True:

        for Frequency in FreqRangSweep:
            Image_F, PahseForward, Image_R, PhaseReflect = SamplingMagAngle(Frequency)

            print("%.1f MHz " % Frequency, "Image_F= ", Image_F, "Image_R= ", Image_R, "\n")
            absY_F = 20 * math.log10(Image_F)  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率
            absY_R = 20 * math.log10(Image_R)

            # print('%d MHZ  %3.5f  %3.5f\n' % (Frequency, PhasePosition, targetPhase))

            AbsYSweepForward.append(absY_F)  # 幅度in dB
            PahseSweepForward.append(PahseForward)  # 相位

            AbsYSweepReflect.append(absY_R)
            SubPha = PhaseReflect - PahseForward  # 计算相位差
            if (SubPha < 0):
                SubPha = 360 + SubPha
            if (SubPha > 180):
                SubPha = (SubPha - 180) - 180
            SkImage.append(Image_R)  # skrf 幅度
            PahseSweepReflect.append(SubPha)

        #time.sleep(0.01)
        print(Frequency)

        pl.clf()  # 清楚画布上的内容
        pl.plot(FreqRangSweep, AbsYSweepForward)  # fist scan
        pl.plot(FreqRangSweep, AbsYSweepReflect)
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
        pl.plot(FreqRangSweep, PahseSweepReflect)
        pl.title('S11 RP(°)')
        pl.xlabel('Frequency (MHz)')
        pl.ylabel('°')
        pl.yticks(np.arange(-180, 200, 30))
        pl.show()

        # 创建skrf touchstone文件
        # 1 端口
        PrintTouchSone_1port_File(SkImage, PahseSweepReflect, FrequencyStart, FreqSwepStep,FileName)
        # 2 端口
        PrintTouchSone_2port_File(SkImage, PahseSweepReflect, FrequencyStart, FreqSwepStep,FileName, 'S11')


        ## run, and apply calibration to a DUT and display
        if ApplayCalibration is True:
            Cal_Display(FileName+'.s1p')
        else:
            break

        Frequency = FrequencyStart
        PWRlevel = PWRlevelReset
        AbsYSweepForward = []
        AbsYSweepReflect = []
        PahseSweepForward = []
        PahseSweepReflect = []
        RangSweep = []
        SkImage = []
        vna.SetRF_PWRlevel(PWRlevel)



        # startMs = PrintMstime()



        # I_Q = np.multiply(np.array(LoSinValue),np.array( LoCosValue))






            # print(time.time())
            # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
if __name__ == '__main__':
    #display and applay calibration
    VNASampling('MesureOut',True)