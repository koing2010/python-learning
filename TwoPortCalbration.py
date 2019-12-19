import FPGA_Calculate as VNA_Calculate
import skrf as rf
import matplotlib.pyplot as plot
import numpy as np

CALIBRATION_FILE_PATH = 'measured/throu/'
THROUGH_CAL_FILE_NAME = ['MesureThruS11', 'MesureThruS12', 'MesureThruS21', 'MesureThruS22']
S11 = [ 1, 1]
S12 = [ 1, 2]
S21 = [ 2, 1]
S22 = [ 2, 2]
S = [ S11, S12, S21, S22]
def ThroughPathCalibration():

    i = 0
    for FileName in THROUGH_CAL_FILE_NAME:
        print(FileName)
        VNA_Calculate.VNASampling(CALIBRATION_FILE_PATH + FileName, False, 'OnePort', S[i], False)  # False mease
        i = i + 1

    #four_oneports_2_twoport(s11, s12, s21, s22, *args, **kwargs)
    through = rf.four_oneports_2_twoport( \
        rf.Network(CALIBRATION_FILE_PATH + THROUGH_CAL_FILE_NAME[0] + '.s1p'),
        rf.Network(CALIBRATION_FILE_PATH + THROUGH_CAL_FILE_NAME[1] + '.s1p'),
        rf.Network(CALIBRATION_FILE_PATH + THROUGH_CAL_FILE_NAME[2] + '.s1p'),
        rf.Network(CALIBRATION_FILE_PATH + THROUGH_CAL_FILE_NAME[3] + '.s1p') )

    through.name = 'measured/Mesurethru'
    through.write_touchstone() # save the s2p 文件

    through.plot_s_db(m = 0, n = 0)
    through.plot_s_db(m = 0, n = 1)
    plot.show()
    through.plot_s_db(m = 1, n = 0)
    through.plot_s_db(m = 1, n = 1)
    plot.show()


if __name__ == '__main__':
    ThroughPathCalibration()