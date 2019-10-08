# -*- coding: utf-8 -*-
import numpy as np
import pylab as pl
import math
import wavemainwindow as WaveDis
import sys
from PyQt5 import QtWidgets, QtGui,QtWidgets
from PyQt5.QtWidgets import QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键
class PlotCanvas(FigureCanvas):
    def __init__(self,parent= None, width = 10, height =10, dpi = 1000):
        fig = Figure(figsize=(width,height), dpi= dpi)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure
        print( PlotCanvas.__class__.__mro__)
        super(PlotCanvas, self).__init__(fig)  # 此句必不可少，否则不能显示图形
        self.axes = fig.add_subplot(111)# 调用figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot方法
        #FigureCanvas.__init__(self,fig)# 初始化父类
        #self.setParent(parent)
        #FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding )
#        FigureCanvas.setSizePolicy(self,
#                                   QtWidgets.QSizePolicy.Expanding,
#                                   QtWidgets.QSizePolicy.Expanding)
#        FigureCanvas.updateGeometry(self)

        #self.plot()
    def plot(self):
        t = [x / 1000 for x in range(5000)]
        Sin = [math.sin(math.pi * t0) for t0 in t]
        Cos = [math.cos(math.pi * t0) for t0 in t]
        Dut = [math.sin(math.pi * t0 - 1) for t0 in t]
        #ax = self.figure.add_subplot(111)
        self.axes.plot(Sin,'r-')
        self.axes.plot(Cos,'b-')
        self.axes.plot(Dut,'g-')
        #self.draw()
        #self.axes.plot(t,Sin)




class ManWindow(WaveDis.Ui_WaveMainWindow):
    def __init__(self):
        self.mainW = QtWidgets.QMainWindow()
        #WaveDis.Ui_WaveMainWindow.__init__(self)
        self.setupUi(self.mainW )
        self.left = 5
        self.top = 5
        self.width = 100
        self.height = 100
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.m = PlotCanvas(self.left, self.top, self.width, self.height)
        self.m.plot()

        self.gridlayout =QGridLayout(self.WavegroupBox)
        self.gridlayout.addWidget(self.m, 0, 1)
        self.mainW.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #mainW = QtWidgets.QMainWindow()
    axes = ManWindow()
    #axes.setupUi(mainW)
    #mainW.show()

    sys.exit(app.exec_())

