import skrf as rf
from pylab import *
import numpy as np
import time
import crclib
import struct
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt

from skrf import Network, Frequency

real = True
echo = True

if real:
	s = serial.Serial('com14', 115200, timeout=2, xonxoff=False) #might need to add enable control settings

def cmd(cmd_string):
	if echo:
		print(cmd_string)

	if real:
		s.write(bytes(cmd_string + '\n',encoding = "utf8"))
		#s.readline() #unclear if this is needed

def query(query_string):
	if echo:
		print(query_string)

	if real:
		s.write(bytes(query_string + '\n',encoding = "utf8"))
		result = s.readline()
		if echo:
			print( "-> " +  str(result, encoding = "utf-8"))
		return result

def ReadMesure(query_string):
	if echo:
		print(query_string)
	if real:
		s.write(bytes(query_string + '\n', encoding="utf8"))
		result = s.readline()
		if echo:
			powr = float(str(result, encoding="utf-8"))
			print("-> " , powr, 'dbm')
		return  powr


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

MHz = 1000000
SerialPort = serial.Serial("com16",115200)
FrequencyStart = 10*MHz # 5Mhz
FreqSweepRate =  1*MHz # 400kHz
FreqSweepTimes = 400 #500 points
FrequencyEnd = FrequencyStart+FreqSweepRate*FreqSweepTimes


#MAIN
#sweep settings (MHz)




query("*IDN?")
query("*RST;*OPC?")

cmd("*SEC 0")
cmd("SYST:NONV:DIS") #disable NVRAM, manual says this is important for performance

cmd("*SEC 1")
#set input and output connectors
cmd("INP RF2")
cmd("OUTP RF3")

#setup generator
#cmd("SOURce:RFGenerator:TX:FREQuency 1MHZ")
cmd("SOUR:RFG:TX:LEVel -10")
cmd("SOUR:RFG:TX:FREQ %dE6" % (FrequencyStart/MHz)) #default level is -27dBm
query("INIT:RFG;*OPC?")

#exit()

#setup analyzer either NPOW or POW, TBD
#TODO Set BW, delay, measurement time, etc. here
#cmd("LEV:MAX 0")
#cmd("CONF:POW:CONT SCAL,NONE") #might not want this
#cmd("CONF:SUB:POW IVAL,0,1")
cmd("RFAN:BAND 1000e3")
cmd("INIT:RFAN") #unclear if I need this, it's in the example
#cmd("INIT:WPOW")


MageCal = np.load('VmageCal.npy')# load the cal file

SendMsg = struct.pack('<BBLBLL',15,0x02,FrequencyStart,0, FreqSweepRate, 1) # L+B = 5bytes FreqCurrent

SendMsg = struct.pack("<B", 0xFE) + SendMsg + struct.pack("<B",crclib.calcFCS(SendMsg))  # XOR the general format frame fields

HexShow("DataRequest:", SendMsg)


Vphs = []
Vmage = []
t1 = time.time()
PwrMesureList = []
LastDegree = 1
for i in range(FreqSweepTimes):

    cmd("RFAN:FREQ %dE6" % ((FrequencyStart * FreqSweepRate* i)/MHz ))
    cmd("SOUR:RFG:FREQ %dE6;*WAI" % ((FrequencyStart  + FreqSweepRate* i)/MHz))
    ReadMesure("READ:RFAN:POW?")
    #time.sleep(0.1)
    SerialPort.write(SendMsg)
    while SerialPort.inWaiting() == 0:
        pass
    byte = SerialPort.read(4)
    Degree = round( struct.unpack('<H',byte[0:2])[0]*3327.0/4096.0/10 -180, 4)
    #if(Degree < -175):
     # LastDegree = -1
    #if(LastDegree ==-1 and Degree > -3 ):
     #   LastDegree = 1
    Degree = LastDegree*Degree


    Vphs.append(Degree)# adc convert to Voltage, then convert to degree

    MageADC = struct.unpack('<H', byte[2:4])[0] * 3327.0 / 4096.0

    Cal = MageCal[int((FrequencyStart + FreqSweepRate*i)/10000000)]
    Relg = (MageADC - Cal)/30.0# get log value
    Relg  = MageADC/30
    Relg =Relg/ 20.0
    if( Relg  > 1):
       Relg = 0.9999
    if (Relg < -1):
          Relg = -0.9999

    T =Relg# math.pow(10,Relg )
    print('Relg= ',Relg,'   T= ',T )
    Vmage.append(round(T , 4))# uints = mV, right lead 4bits

print(Vphs[:10])
print(Vmage[:10])
ring_slot = Network('horn antenna.s1p')
print(ring_slot)
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
t = np.arange(FrequencyStart/MHz,(FreqSweepRate*FreqSweepTimes+FrequencyStart)/MHz, FreqSweepRate/MHz)#5Mhz - 200Mhz  0.4mhz step up
VMageYscale = np.arange(-1,1, 0.1)
VphsYscale =   np.arange(-180, 180, 10)


#plt.ion() #activre display
#fig=plt.figure()
#ax=fig.add_subplot(1,1,1)
#ax.set_ylim(0,180)
#x.set_xlim(0,FreqSweepRate/1000000*FreqSweepTimes)#K
#for i in range(10):
#    try:
#        ax.lines.remove(lines[0])
#    except Exception:
#        pass
#    lines = ax.plot(t,Vmage)
#    plt.pause(1)



plt.plot(t,Vmage)#(x , y)
plt.ylabel('Vmage (T_)')
plt.xlabel('Frequency (MHz)')
plt.yticks(VMageYscale)
plt.show()


plt.plot(t,Vphs)#(x , y)
plt.ylabel('Degree (°)')
plt.xlabel('Frequency (MHz)')
plt.yticks(VphsYscale)
plt.show()

N=FreqSweepTimes    # 采样点数
fs= FreqSweepTimes  # 采样频率
df = fs/(N-1)   # 分辨率
f = [df*n for n in range(0,N)]   # 构建频率数组

Y = np.fft.fft(Vphs)/N  #*2/N 反映了FFT变换的结果与实际信号幅值之间的关系
absY = [np.abs(x) for x in Y]      #求傅里叶变换结果的模
#print(absY)

plt.plot(f,absY)
plt.show()

def PrintSkrfFile(Mage, Vphs, FreqStart, FreqRate, FreqTime):
    MesureList= ['# MHz S MA R 50.0\n']
    File = open('MesureOut.s1p','w')
    File.write(MesureList[0])
    for size in range(len(Mage)):
        MesureList.append( '%.4f   %.4f   %.4f \n'%(((FreqStart+FreqRate*size)/MHz,Mage[size], Vphs[size])))
        File.write(MesureList[size+1])
    File.closed

PrintSkrfFile(Vmage,Vphs,FrequencyStart,FreqSweepRate,FreqSweepTimes)

ring_slot = Network('MesureOut.s1p')
print(ring_slot)

ring_slot.plot_s_db()
plt.show()
ring_slot.plot_s_deg()
plt.show()


ring_slot.plot_s_smith()
plt.show()


SerialPort.closed