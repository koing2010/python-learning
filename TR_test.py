import FPGA_Calculate as VNA_Calculate
import skrf as rf
import matplotlib.pyplot as plot

CALIBRATION_FILE_PATH = 'measured/throu/'
THROUGH_CAL_FILE_NAME = ['MesureThruS11', 'MesureThruS12', 'MesureThruS21', 'MesureThruS22']
S11 = [1, 1]
S12 = [1, 2]
S21 = [2, 1]
S22 = [2, 2]
#def VNASampling(FileName, ApplayCalibration, PortNum, S_Paramete, DisplaySampling):
VNA_Calculate.VNASampling( CALIBRATION_FILE_PATH + THROUGH_CAL_FILE_NAME[1], True, 'OnePort', S21, True)  # False mease