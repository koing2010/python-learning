import numpy as np
import pylab as pl
import math
# 采样步长
t = [x/1024.0 for x in range(1024)]
test = [i for i  in range(1024) ]
# 设计的采样值
#y = [2.0 + 3.0 * math.cos(2.0 * math.pi * 50 * t0 )+ 1.5 * math.cos(2.0 * math.pi * 75 * t0 )+  1.0 * math.cos(2.0 * math.pi * 150 * t0)+  2.0 * math.cos(2.0 * math.pi * 220 * t0)for t0 in t ]
y = [0.2*math.cos(math.pi * 50 * t0) for t0 in t]
y1 = [0.2*math.cos(math.pi * 50 * t0 +math.pi /2) for t0 in t]

B = [5*math.sin( math.pi * 70 * t0 ) for t0 in t]
#pl.plot([a*1048 for a in t],y)

#pl.show()
#pl.plot([a*1048 for a in t],B)

#pl.show()
z = [a*b for a,b in zip(y,B)]
z1 = [a*b for a,b in zip(y,y1)]

pl.plot([a*1024 for a in t],z)
pl.plot([a*1024 for a in t],z1)
pl.show()
N=len(t)    # 采样点数
fs=1024.0     # 采样频率
df = fs/(N-1)   # 分辨率
f = [df*n for n in range(0,N)]   # 构建频率数组


Y = np.fft.fft(z)*2/N  #*2/N 反映了FFT变换的结果与实际信号幅值之间的关系
testY = np.fft.fft(test)*2/N
absY = [np.abs(x) for x in testY]      #求傅里叶变换结果的模
print(absY)
i=0
#while i < len(absY):
# if absY[i]>0.01:
#    print("freq:M, Y: %5.2f + %5.2f j, A:%3.2f, phi: %6.1f"%(i, Y[i].real, Y[i].imag, absY[i],math.atan2(Y[i].imag,Y[i].real)*180/math.pi))
#    i+=1
pl.plot(f,absY)
pl.show()