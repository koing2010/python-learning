#!/usr/bin/python

import serial
import time
import pylab as pl
import numpy as np


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
#MAIN
#sweep settings (MHz)
freq_start = 10
freq_end = 2650
divisor = 10

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
cmd("SOUR:RFG:TX:LEVel 0")
cmd("SOUR:RFG:TX:FREQ %dE6" % freq_start) #default level is -27dBm
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

t1 = time.time()
PwrMesureList = []
for f in range(int(freq_start/divisor),int(freq_end/divisor)):
	#cmd("POW:FREQ:CENT %dE6" % f)
	cmd("RFAN:FREQ %dE6" % (f*divisor))
	cmd("SOUR:RFG:FREQ %dE6;*WAI" % (f*divisor))
	#query("SOUR:RFG:FREQ %dE6;*OPC?" % f)
	#query("READ:SUB:POW?") #may not work with SCAL
	PwrMesureList.append( ReadMesure("READ:RFAN:POW?"))
	print(f*divisor," MHz")
	#time.sleep(0.01)
	#query("READ:WPOW?")

t2 = time.time()
print("%0.3fs for %d points, %f points/s" % (t2-t1, (freq_end-freq_start)/divisor, (freq_end-freq_start)/(t2-t1)/divisor))

Xscale =   np.arange(freq_start, freq_end, divisor)
Yticks =   np.arange(-60, 10, 10)
pl.plot(Xscale,PwrMesureList)
pl.ylabel('S21 dBm')
pl.xlabel('Frequency (MHz)')
pl.yticks(Yticks)
pl.grid(axis= 'y',linestyle='--')
pl.show()

t1 = time.time()
PwrOpenMesureList = []
for f in range(int(freq_start/divisor),int(freq_end/divisor)):
	#cmd("POW:FREQ:CENT %dE6" % f)
	cmd("RFAN:FREQ %dE6" % (f*divisor))
	cmd("SOUR:RFG:FREQ %dE6;*WAI" % (f*divisor))
	#query("SOUR:RFG:FREQ %dE6;*OPC?" % f)
	#query("READ:SUB:POW?") #may not work with SCAL
	PwrOpenMesureList.append( ReadMesure("READ:RFAN:POW?"))
	print(f*divisor," MHz")
	time.sleep(0.01)
	#query("READ:WPOW?")

t2 = time.time()
print("%0.3fs for %d points, %f points/s" % (t2-t1, freq_end-freq_start, (freq_end-freq_start)/(t2-t1)))

pl.plot(Xscale,PwrMesureList)

pl.plot(Xscale,PwrOpenMesureList)
Dir = [a - b for a,b in zip(PwrOpenMesureList,PwrMesureList)]

pl.plot(Xscale,Dir)
pl.ylabel('S21 dBm')
pl.xlabel('Frequency (MHz)')
pl.yticks(Yticks)
pl.grid(axis= 'y',linestyle='--')
pl.show()