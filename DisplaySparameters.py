from skrf import Network
import matplotlib.pyplot as plot
import numpy as np

Ant1_S1 = Network("C:/Users/koing/vna.3.2/export/VNA_190917_212703.s2p")
Ant_S1 = Network("C:/Users/koing/vna.3.2/export/VNA_190917_221806.s2p")
Ant2_S1 = Network("C:/Users/koing/vna.3.2/export/VNA_190923_140629.s2p")
#Ant_S1.plot_s_db()
#Ant1_S1.plot_s_db()
plot.grid(axis='y', linestyle='--')
plot.grid(axis='x', linestyle='--')
plot.yticks(np.arange(0, 40, 2))
plot.xticks(np.arange(0, 6000000000, 500000000))
(Ant1_S1/Ant_S1).plot_s_db()
(Ant1_S1/Ant2_S1).plot_s_db()
#(Ant_S1/Ant2_S1).plot_s_db()
plot.show()