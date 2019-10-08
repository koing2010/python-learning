from skrf import Network
import pylab as pl
ring_slot = Network('MesureOut corrected.s1p')
print(ring_slot)

ring_slot.plot_s_db()  # 幅度曲线
pl.show()
ring_slot.plot_s_deg()  # 相位曲线
pl.show()

ring_slot.plot_s_smith()  # 史密斯圆
pl.show()