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
from VNACalibrate import Cal_Display
from VNADataRequest import  VNA_DEV as VNA
#  22.5527dbm.  3V 50R 对应的功率
DBM_3V = 13.523
vna = VNA()

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



def VNASampling(FileName, ApplayCalibration):
    fs = 24  # 采样频率
    N = 4080  # 采样点数
    N_HALF = 1200  #
    DISPLAY_MODE = 0  # 1 wave, 0 spectrum
    CALIBRATION_MODE = True
    df = fs / (N - 1)  # 分辨率



    WAVE_Yticks = np.arange(-1, 1.2, 0.2)

    FrequencyStart = 1000
    FrequencyEnd = 4000
    FreqSwepStep = 10
    PWRlevelReset = 40
    RangSweep = []
    ForwardOrReflect = True
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
    vna.SetReceiveCH(0) # set forward or reflection  level bit[0][0] = 1 reflect= 1， forward = 0

    while True:
        #time.sleep(0.01)
        if (Frequency >= FrequencyEnd):  # 显示RL 的曲线

            if (len(AbsYSweepForward) == int((FrequencyEnd - FrequencyStart) / FreqSwepStep)):
                pl.clf()  # 清楚画布上的内容
                pl.plot(RangSweep, AbsYSweepForward)  # fist scan
                pl.plot(RangSweep, AbsYSweepReflect)
                pl.title('S11 RL(dB)')
                pl.ylabel('dB')
                pl.xlabel('Frequency (MHz)')
                pl.yticks(np.arange(-60, 20, 10))
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


        if (ForwardOrReflect is True):
            ##Forward
            vna.SetReceiveCH(0) # set forward or reflection  level bit[0][0] reflect= 1， forward = 0
            RangSweep.append(Frequency)
            vna.SetRF_LO_FRQ(Frequency)
            time.sleep(0.01)
        else:
            ## Reflectoin
            vna.SetReceiveCH(1) # set forward or reflection  level bit[0][0] reflect= 1， forward = 0
            #time.sleep(0.05)

        vna.StartSamp()


        XCosValue = []
        # startMs = PrintMstime()


        while vna.SerialPort.inWaiting() == 0:
            pass
        byte = vna.SerialPort.read(8)

        IF_I_ACC = struct.unpack('<i', byte[0:4])[0]
        IF_Q_ACC =  struct.unpack('<i', byte[4:8])[0]
        if (IF_I_ACC != 0):

            # I_Q = np.multiply(np.array(LoSinValue),np.array( LoCosValue))
            IF_I_ACC = IF_I_ACC
            IF_Q_ACC = IF_Q_ACC
            print('I_ACC: %3.6f , Q_ACC: %3.6f ' % (IF_I_ACC, IF_Q_ACC))
            PhasePosition = math.atan(IF_Q_ACC / IF_I_ACC)
            Image = np.abs(IF_I_ACC * 2 /math.cos(PhasePosition)/N/0x20000)
            print("%d MHz "%Frequency,"Image= ", Image, "\n")
            absY = 20 * math.log10(Image)  # 求傅里叶变换结果的模.  DBM_3V 3v对应的功率

            if (DISPLAY_MODE == 1):

                pl.clf()  # 清楚画布上的内容
                n = 0
                for n in range(N_HALF):
                    if (XCosValue[n] < 0.05 and XCosValue[n] >= 0 and XCosValue[n + 1] > XCosValue[n]):
                        break
                pl.plot(XCosValue[n:n + 100])
                pl.title('WaveDisplay %d MHZ ' % Frequency + " RL(dB)= %3.2f" % absY)
                pl.yticks(WAVE_Yticks)
                pl.xlabel('Time (ns)')
                pl.pause(0.08)
            ''''// end if  '''

            PhasePosition = PhasePosition / math.pi * 180
            targetPhase = PhasePosition
            if (IF_Q_ACC >= 0 and IF_I_ACC >= 0  ):
                targetPhase = PhasePosition
            elif(IF_Q_ACC >= 0 and IF_I_ACC < 0):
                targetPhase = 180 + PhasePosition
            elif(IF_Q_ACC < 0 and IF_I_ACC >= 0):
                targetPhase = 360 + PhasePosition
            else:
                targetPhase = 180 + PhasePosition

            #print('%d MHZ  %3.5f  %3.5f\n' % (Frequency, PhasePosition, targetPhase))
            if (ForwardOrReflect is True):
                ForwardOrReflect = False
                AbsYSweepForward.append(absY)  # 幅度
                PahseSweepForward.append(targetPhase)  # 相位
                PahseForward = targetPhase
                ImageForwardDB = absY
            else:
                ForwardOrReflect = True
                AbsYSweepReflect.append(absY)
                SubPha = targetPhase - PahseForward
                if (SubPha < 0):
                   SubPha = 360 + SubPha
                if (SubPha > 180):
                    SubPha = (SubPha - 180) - 180
                SkImage.append(Image)  # skrf 幅度
                PahseSweepReflect.append(SubPha)
                Frequency = Frequency + FreqSwepStep
'''
                if(ImageForwardDB > -9.7 and  PWRlevel > 0):
                    PWRlevel = PWRlevel - 1
                    vna.SetRF_PWRlevel(PWRlevel)
                    #time.sleep(0.05)

                elif(ImageForwardDB < -10.3 and PWRlevel < 63):
                    PWRlevel = PWRlevel + 1
                    vna.SetRF_PWRlevel(PWRlevel)
                    #time.sleep(0.05)
'''
            # print(time.time())
            # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
if __name__ == '__main__':
    #display and applay calibration
    VNASampling('MesureOut.s1p',True)