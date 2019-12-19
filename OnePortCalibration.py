import FPGA_Calculate as VNA_Calculate

PORT1_CAL_FILE_NAME = ['MesureShort', 'MesureOpen', 'MesureLoad']
PORT2_CAL_FILE_NAME = ['MesureShortPort2', 'MesureOpenPort2', 'MesureLoadPort2']
CALIBRATION_FILE_PATH = 'measured/'

S11 = [ 1, 1]
S22 = [ 2, 2]

def OnePortCalibration():
    # Port1 S O L calibration, S11

    for FileName in PORT1_CAL_FILE_NAME:
        print(FileName)
        VNA_Calculate.VNASampling( CALIBRATION_FILE_PATH + FileName, False, 'OnePort' , S11, True)# False mease

    # 校准之后再次测量的时候需要更新TemMesure文件
    InfoFile = open(CALIBRATION_FILE_PATH + 'Info.txt', 'w')
    InfoFile.write('%d %d %d\n'%(0, 0, 0))
    InfoFile.close()

    # Port2 SOL  calibration ,S22
    for FileName in PORT2_CAL_FILE_NAME:
        print(FileName)
        VNA_Calculate.VNASampling( CALIBRATION_FILE_PATH + FileName, False, 'OnePort', S22, True)# False mease

    InfoFile = open(CALIBRATION_FILE_PATH + 'InfoPort2.txt', 'w')
    InfoFile.write('%d %d %d\n'%(0, 0, 0))
    InfoFile.close()

# create calibrate file using SHORT  OPEN and LOAD component
if __name__ == '__main__':
    OnePortCalibration()