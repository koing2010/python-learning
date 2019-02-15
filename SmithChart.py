import skrf as rf
from pylab import *

import time
import crclib
import struct
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt

from skrf import Network, Frequency

#display hex string
def HexShow(S_name,i_string):
	hex_string = ''
	hLen = len(i_string)
	for i in range(hLen):
		hvol = i_string[i]
		hhex = '%02X' % (hvol)
		hex_string += hhex + ' '
#	print('ReceiveBytes: %i_string' % (hex_string))
	print(S_name,hex_string,'	total:',hLen)


SerialPort = serial.Serial("com16",115200)
FrequencyStart = 5000000 # 5Mhz
FreqSweepRate =  400000 # 400kHz
FreqSweepTimes = 200 #500 points
SendMsg = struct.pack('<BBLBLL',15,0x02,FrequencyStart,0, FreqSweepRate,FreqSweepTimes) # L+B = 5bytes FreqCurrent

SendMsg = struct.pack("<B", 0xFE) + SendMsg + struct.pack("<B",crclib.calcFCS(SendMsg))  # XOR the general format frame fields

HexShow("DataRequest:", SendMsg)

SerialPort.write(SendMsg)
Vphs = []
Vmage = []
for i in range(FreqSweepTimes):
    while SerialPort.inWaiting() == 0:
        pass
    byte = SerialPort.read(4)
    Vphs.append(struct.unpack('<H', byte[0:2])[0]*3327.0/4096.0)# uints = mV
    Vmage.append(struct.unpack('<H',byte[2:4])[0]*3327.0/4096.0/10)# adc convert to Voltage, then convert to degree

print(Vphs)
print(Vmage)
#ring_slot = Network('horn antenna.s1p')
#print(ring_slot)
#ring_slot.plot_s_db()
#plt.show()

#ring_slot.plot_s_deg()
#plt.show()

#ring_slot.plot_s_smith()
#plt.show()
#freq = Frequency(1,10,101,'ghz')
#ntwk = Network(frequency=freq, s= [-1, 1j, 0], z0=50, name='slippy')
#shape(ring_slot.s)

#import numpy as np
t = np.arange(5.0,0.4*FreqSweepTimes+5.0, 0.4)#5Mhz - 200Mhz  0.4mhz step up
plt.plot(t,Vmage)#(x , y)

plt.ylabel('Vmage (°)')
plt.xlabel('Frequency (MHz)')

plt.show()
plt.plot(t,Vphs)#(x , y)

plt.ylabel('S21 ')
plt.xlabel('Frequency (MHz)')

plt.show()
SerialPort.closed