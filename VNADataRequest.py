import serial
import struct
import time
class VNA_DEV():
    def __init__(self):
        self.SerialPort = serial.Serial("com27")
        self.SMsg = []

    def SetSamplingCKL(self, Divider):
        self.SMsg = struct.pack('<BBBBBB', 0xFE, (0x04 + Divider*16),0x00 ,0x00, 0x00, 0x00)  # set sampling clock, first Byte H4
        self.SendMsg()
    def SetRF_PWRlevel(self,level):
        self.SMsg = struct.pack('<BBBBBB', 0xFE, 0x06, level, 0x00, 0x00, 0x00)  # set RF output level bit[5:0]
        self.SendMsg()
    def StartSamp(self):
        self.SMsg = struct.pack('<BBBBBB', 0xFE, 0x01, 0x00, 0x00, 0x00, 0x00)  # start ADC
        self.SendMsg()
    def SetRF_LO_FRQ(self,Frequency):# uinit MHZ
        self.SMsg = struct.pack('<BBI', 0xFE, 0x03, int(Frequency * 1000))  # RF = 1000MHZ LO = RF-2MHZ
        self.SendMsg()
    def SendMsg(self):
        self.SerialPort.write(self.SMsg)
    def WriteADF_RF_Reg(self, RegData):
        print(hex(RegData))
        self.SMsg = struct.pack('<BBI', 0xFE, 0x07, RegData)  # RF = 1000MHZ LO = RF-2MHZ
        self.SendMsg()

    def WriteADF_LO_Reg(self, RegData):
        print(hex(RegData))
        self.SMsg = struct.pack('<BBI', 0xFE, 0x08, RegData)  # RF = 1000MHZ LO = RF-2MHZ
        self.SendMsg()

    def SelectPort(self,S_Paramete):
        SlectBitMap = 0
        if(S_Paramete[1] == 2): # bit0 RF -> port_1 or prot_2;#a
            SlectBitMap = 1
            print('SEL Port2')
        else:
            print('SEL Port1')

        if(S_Paramete[0] == 2): # Bit1  p1 or p2 reflect -> ADC
            SlectBitMap = SlectBitMap | 0x02
            print('DC REF2')
        else:
            print('SEL ADC1')

        # CMD_RF_PORT_and_REFLET_SW //


        self.SMsg = struct.pack('<BBBBBB', 0xFE, 0x05, SlectBitMap, 0x00, 0x00, 0x00)
        #print( self.SMsg)
        self.SendMsg()
