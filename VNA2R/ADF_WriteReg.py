from  VNADataRequest import VNA_DEV as VNA
import time
VNA_2R = VNA()


def Cal_R0_value(FreMHZ):
    FreKhz = int( FreMHZ * 1000)
    #R4=0x00AC803C;               #步进2khz
    Freqint=int((FreKhz<<2)/24000);
    Freqfrac=int((FreKhz>>1)%3000);
    R0= (Freqint<<15)+ (Freqfrac<<3);
    print("R0=", hex(R0))
    return int(R0)

LO_ADF_REG0 = Cal_R0_value(1000)#1002MHZ
RF_ADF_REG0 = Cal_R0_value(998)#1000MZH
ADF_REG1 = 0x0800DDC1 #32'H0800DDC1,
ADF_REG2 = 0x00004E42 #32'H04005FC2,
ADF_REG3 = 0x00008043#32'H000004B3,
ADF_REG4 = 0x00AC803C#32'H00AA003C,
ADF_REG5 = 0x00400005;

#set LO  register
VNA_2R.WriteADF_LO_Reg(ADF_REG5)
VNA_2R.WriteADF_LO_Reg(ADF_REG4)
VNA_2R.WriteADF_LO_Reg(ADF_REG3)
VNA_2R.WriteADF_LO_Reg(ADF_REG2)
VNA_2R.WriteADF_LO_Reg(ADF_REG1)
VNA_2R.WriteADF_LO_Reg(LO_ADF_REG0)
#set RF  register
VNA_2R.WriteADF_RF_Reg(ADF_REG5)
VNA_2R.WriteADF_RF_Reg(ADF_REG4)
VNA_2R.WriteADF_RF_Reg(ADF_REG3)
VNA_2R.WriteADF_RF_Reg(ADF_REG2)
VNA_2R.WriteADF_RF_Reg(ADF_REG1)
VNA_2R.WriteADF_RF_Reg(RF_ADF_REG0)