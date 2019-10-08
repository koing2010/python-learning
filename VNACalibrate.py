import skrf as rf
import pylab as pl
import numpy as np
from skrf.calibration import OnePort

## created necessary data for Calibration class
MeasurePath = 'measured'

# a list of Network types, holding 'ideal' responses
my_ideals = [\
        rf.Network(MeasurePath + '/ideal/Short.s1p'),
        rf.Network(MeasurePath + '/ideal/Open.s1p'),
        rf.Network(MeasurePath + '/ideal/Load.s1p'),
        ]

# a list of Network types, holding 'measured' responses
my_measured = [\
        rf.Network(MeasurePath + '/Mesureshort.s1p'),
        rf.Network(MeasurePath + '/Mesureopen.s1p'),
        rf.Network(MeasurePath + '/Mesureload.s1p'),
        ]

## create a Calibration instance
cal = rf.OnePort(\
        ideals = my_ideals,
        measured = my_measured,
        )


## run, and apply calibration to a DUT
def Cal_Display(fileName):
        # run calibration algorithm
        cal.run()

        # apply it to a dut
        dut = rf.Network(fileName)
        dut_caled = cal.apply_cal(dut)
        dut_caled.name =  dut.name + ' corrected'
        dut_caled.plot_s_db()
        # plot results
        pl.yticks(np.arange(-60, 20, 10))
        pl.grid(axis='y', linestyle='--')
        pl.show()
        # save results
        dut_caled.write_touchstone()


        dut_caled.plot_s_deg()
        pl.show()
        dut_caled.plot_s_smith()
        pl.show()
if __name__ == '__main__':
        Cal_Display('MesureOut.s1p')