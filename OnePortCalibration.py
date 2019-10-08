import FPGA_Calculate as VNA_Calculate

CALIBRATION_FILE_NAME = ['MesureShort.s1p', 'MesureOpen.s1p', 'MesureLoad.s1p']

CALIBRATION_FILE_PATH = 'measured/'

# create calibrate file using SHORT  OPEN and LOAD component
if __name__ == '__main__':
    for FileName in CALIBRATION_FILE_NAME:
        print(FileName)
        VNA_Calculate.VNASampling(CALIBRATION_FILE_PATH + FileName,False)# False mease