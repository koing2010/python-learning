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
        File = open(filePath+ 'ideal/' + FileName, 'w')
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

#creat two port ideal file
def TwoPortCreatIdealFile(filePath, F_start, F_end, F_step):
    IDEAL_FILE_NAME = ['thru.s2p','short, short.s2p', 'open, open.s2p', 'load, load.s2p']

    #   [ MagS11, AngS11, MagS21, AngS21, MagS12, AngS12, MagS22, AngS22]
    MagAng = [ 0,0,  0,0,  0,0,  0,0 ]
    for FileName in IDEAL_FILE_NAME:
        IlealList = ['# MHz S MA R 50.0\n']
        FreqRangList = np.arange(F_start, F_end, F_step)
        File = open(filePath + FileName, 'w')
        if(FileName is 'thru.s2p'):
            MagAng = [ 0,0,  0,0,  0,0,  0,0 ]
        elif (FileName is 'short, short.s2p'):
            MagAng = [0, 0, 0, 0, 0, 0, 0, 0]
        elif (FileName is 'open, open.s2p'):
            MagAng = [0, 0, 0, 0, 0, 0, 0, 0]
        elif (FileName is 'load, load.s2p'):
            MagAng = [0, 0, 0, 0, 0, 0, 0, 0]

        File.write(IlealList[0])
        for Fre in FreqRangList:
            #IlealList.append('%.4f   %.8f   %.4f \n'%(Fre ,Image, Phase ) )
            File.write('%.4f   %.8f   %.4f    %.8f   %.4f    %.8f   %.4f    %.8f   %.4f \n' % ((Fre, MagAng[0:]))) #,  MagAng[1],  MagAng[2],  MagAng[3],  MagAng[4],  MagAng[5],  MagAng[6],  MagAng[7])))
        File.close()

def OnePortCreatMesureFile(filePath, F_start, F_end, F_step, Port):

    IlealList = ['! %d %d %d\n'%(F_start, F_end, F_step)+'# MHz S MA R 50.0\n']
    if (Port == [2, 2]):
        print("Port2 Selected")
        MESURE_FILE_NAME = ['MesureShortPort2.s1p', 'MesureOpenPort2.s1p', 'MesureLoadPort2.s1p']
        InfoFile = open(filePath + 'InfoPort2.txt', 'r')
    else:
        MESURE_FILE_NAME = ['MesureShort.s1p', 'MesureOpen.s1p', 'MesureLoad.s1p']
        InfoFile = open(filePath + 'Info.txt', 'r')
    #读取设置文件

    S = InfoFile.readline()
    Str = '%d %d %d' % (F_start, F_end, F_step)
    print(S[0:-1])
    if(S[0:-1] == Str):
        InfoFile.close()
        print('file has been!')
        return

    #创建Ideal 文件
    OnePortCreatIdealFile( filePath, F_start, F_end, F_step)

    for FileName in MESURE_FILE_NAME:
        MesureFile = open(filePath + FileName, 'r')
        TempMesureFile = open(filePath + 'Temp' + FileName, 'w+')

        TempMesureFile.write(IlealList[0])
        FreqRangList = np.arange(F_start, F_end, F_step)
        MesureLineStart = F_start - 140 + 3 # 140  是起始频率, 4400M 结束频率

        AllFile = MesureFile.readlines()
        #print(AllFile)
        for req in FreqRangList:
            #print(MesureLineStart)
            TempMesureFile.write(AllFile[MesureLineStart])
            #print(S[MesureLineStart])
            MesureLineStart  =  MesureLineStart + F_step
            #print(MesureLineStart , F_step)

        TempMesureFile.close()
        MesureFile.close()

    # 保存好信息 表示已经生成过mesure 文件
    if (Port == [2, 2]):
        InfoFile = open(filePath + 'InfoPort2.txt', 'w')
        InfoFile.write('%d %d %d\n'%(F_start, F_end, F_step))
        InfoFile.close()
    else:
        InfoFile = open(filePath + 'Info.txt', 'w')
        InfoFile.write('%d %d %d\n'%(F_start, F_end, F_step))
        InfoFile.close()
    #return

## run, and apply calibration to a DUT
def Cal_Display(fileName , PortNum, Port):
        # a list of Network types, holding 'ideal' responses

        IdealShort = rf.Network(MeasurePath + '/ideal/Short.s1p')
        IdealOpen  = rf.Network(MeasurePath + '/ideal/Open.s1p')
        IdealLoad  = rf.Network(MeasurePath + '/ideal/Load.s1p')


        # a list of Network types, holding 'measured' responses




        if(PortNum  == 'OnePort' ):
            my_ideals   = [IdealShort, IdealOpen ,IdealLoad]
            if(Port == [2,2]):
                print("Port2 Selected")
                my_measured = [ \
                    rf.Network(MeasurePath + '/TempMesureShortPort2.s1p'),
                    rf.Network(MeasurePath + '/TempMesureOpenPort2.s1p'),
                    rf.Network(MeasurePath + '/TempMesureLoadPort2.s1p'),]
            else:
                print("Port1 Selected")
                my_measured = [ \
                rf.Network(MeasurePath + '/TempMesureShort.s1p'),
                rf.Network(MeasurePath + '/TempMesureOpen.s1p'),
                rf.Network(MeasurePath + '/TempMesureLoad.s1p'),]
            cal = rf.OnePort( \
                ideals=my_ideals,
                measured=my_measured,
            )
        else:  # PortNum = TwoPort
            freqs =  IdealShort.f
            #print(freqs)
            through_delay = 51.1e-12
            d = 2 * np.pi * through_delay
            through_s = [[[0, np.exp(-1j * d * f)], [np.exp(-1j * d * f), 0]] for f in freqs]
            through_i = rf.Network( s=through_s, f= freqs, f_unit='Hz' )
            #print(through_i)
            my_ideals   = [
                rf.two_port_reflect( IdealShort, IdealShort ),
                rf.two_port_reflect( IdealOpen, IdealOpen ),
                rf.two_port_reflect( IdealLoad, IdealLoad ),
                through_i , ]
            my_measured = [ \
                rf.two_port_reflect( rf.Network(MeasurePath + '/TempMesureShort.s1p'), rf.Network(MeasurePath + '/TempMesureShortPort2.s1p') ),
                rf.two_port_reflect( rf.Network(MeasurePath + '/TempMesureOpen.s1p'), rf.Network(MeasurePath + '/TempMesureOpenPort2.s1p' ) ),
                rf.two_port_reflect( rf.Network(MeasurePath + '/TempMesureLoad.s1p'), rf.Network(MeasurePath + '/TempMesureLoadPort2.s1p' ) ),
                rf.Network(MeasurePath + '/Mesurethru.s2p'),]

            # SOLT is  12-term error model
            cal = rf.TwelveTerm(\
                ideals=my_ideals,
                measured=my_measured,
                n_thrus=1,
                isolation=rf.two_port_reflect(rf.Network(MeasurePath + '/TempMesureLoad.s1p'), rf.Network(MeasurePath + '/TempMesureLoadPort2.s1p' )  ),
            )


        # run calibration algorithm
        cal.run()

        # apply it to a dut
        dut = rf.Network(fileName)
        dut_caled = cal.apply_cal(dut)
        dut_caled.name =  dut.name + 'Corrected'
        #dut_caled.plot_s_db(m=0,n=1)
        #dut_caled.plot_s_db(m=1, n=0)
        dut_caled.plot_s_db()
        # plot results
        pl.yticks(np.arange(-80, 20, 10))
        pl.grid(axis='y', linestyle='--')
        pl.show()
        #“” save results
        dut_caled.write_touchstone()
        dut_caled.plot_s_deg()
        pl.show()
        dut_caled.plot_s_smith(m=0,n=0)
        pl.show()
if __name__ == '__main__':
    OnePortCreatMesureFile('measured/', 2000, 3000, 10, 'OnePort' )
    Cal_Display('MesureOut.s2p', 'TwoPort',[1,1])