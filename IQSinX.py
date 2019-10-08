import numpy as np
import pylab as pl
import math

t = [x/1000 for x in range(2000)]

Sin = [math.sin(math.pi * t0) for t0 in t]
Cos = [math.cos(math.pi * t0) for t0 in t]
Dut = [math.sin(math.pi * t0- 0.75*math.pi) for t0 in t]
#y = [0.2*math.cos(math.pi * 50 * t0) for t0 in t]
pl.plot([a for a in t],Sin)

#pl.plot([a for a in t],Cos)

pl.plot([a for a in t],Dut)
pl.grid(axis= 'y',linestyle='--')

pl.show()