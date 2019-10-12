import skrf as rf
import pylab as pl
import numpy as np
from skrf.calibration import OnePort

## created necessary data for Calibration class
MeasurePath = 'measured'



## create a Calibration instance

def OnePortCreatIdealFile(filePath, F_start, F_end, F_step):
    IDEAL_FILE_NAME = ['Short.s1p', 'Open.s1p', 'Load.s1p']
    for FileName in IDEAL_FILE_NAME:
        IlealList = ['# MHz S MA R 50.0\n']
        FreqRangList = np.arange(F_start, F_end, F_step)
        File = open(filePath + FileName, 'w')
        if(FileName is 'Load.s1p'):
            Image = 0
            Phase = 0
        elif (FileName is 'Short.s1p'):
            Image = 1
            Phase = 180
        elif (FileName is 'Open.s1p'):
            Image = 1
            Phase = 0
        File.write(IlealList[0])
        for Fre in FreqRangList:
            #IlealList.append('%.4f   %.8f   %.4f \n'%(Fre ,Image, Phase ) )
            File.write('%.4f   %.8f   %.4f \n'%(Fre ,Image, Phase ))
        File.close()
def OnePortCreatMesureFile(filePath, F_start, F_end, F_step):
    MESURE_FILE_NAME = ['Mesureshort.s1p', 'Mesureopen.s1p', 'Mesureload.s1p']
    IlealList = ['! %d %d %d\n'%(F_start, F_end, F_step)+'# MHz S MA R 50.0\n']

    #读取设置文件
    InfoFile = open(filePath + 'Info.txt', 'r')
    S = InfoFile.readline()
    Str = '%d %d %d' % (F_start, F_end, F_step)
    print(S[0:-1])
    if(S[0:-1] == Str):
        InfoFile.close()
        print('file has been!')
        return


    for FileName in MESURE_FILE_NAME:
        MesureFile = open(filePath + FileName, 'r')
        TempMesureFile = open(filePath + 'Temp' + FileName, 'w+')

        TempMesureFile.write(IlealList[0])
        FreqRangList = np.arange(F_start, F_end, F_step)
        MesureLineStart = F_start - 140 + 1 # 140  是起始频率, 4400M 结束频率

        AllFile = MesureFile.readlines()
        for req in FreqRangList:
            #print(MesureLineStart)
            TempMesureFile.write(AllFile[MesureLineStart])
            #print(S[MesureLineStart])
            MesureLineStart  =  MesureLineStart + F_step

        TempMesureFile.close()
        MesureFile.close()

    # 保存好信息 表示已经生成过mesure 文件
    InfoFile = open(filePath + 'Info.txt', 'w')
    InfoFile.write('%d %d %d\n'%(F_start, F_end, F_step))
    InfoFile.close()
    #return

## run, and apply calibration to a DUT
def Cal_Display(fileName):
        # a list of Network types, holding 'ideal' responses
        my_ideals = [ \
            rf.Network(MeasurePath + '/ideal/Short.s1p'),
            rf.Network(MeasurePath + '/ideal/Open.s1p'),
            rf.Network(MeasurePath + '/ideal/Load.s1p'),
        ]

        # a list of Network types, holding 'measured' responses
        my_measured = [ \
            rf.Network(MeasurePath + '/TempMesureshort.s1p'),
            rf.Network(MeasurePath + '/TempMesureopen.s1p'),
            rf.Network(MeasurePath + '/TempMesureload.s1p'),
        ]
        cal = rf.OnePort( \
                ideals=my_ideals,
                measured=my_measured,
        )
        # run calibration algorithm
        cal.run()

        # apply it to a dut
        dut = rf.Network(fileName)
        dut_caled = cal.apply_cal(dut)
        dut_caled.name =  dut.name + ' corrected'
        dut_caled.plot_s_db()
        # plot results
        pl.yticks(np.arange(-80, 20, 10))
        pl.grid(axis='y', linestyle='--')
        pl.show()
        # save results
        dut_caled.write_touchstone()


        dut_caled.plot_s_deg()
        pl.show()
        dut_caled.plot_s_smith()
        pl.show()
if __name__ == '__main__':
        Cal_Display('MesureOut.s1p')