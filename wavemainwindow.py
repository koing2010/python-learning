# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wavemainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WaveMainWindow(object):
    def setupUi(self, WaveMainWindow):
        WaveMainWindow.setObjectName("WaveMainWindow")
        WaveMainWindow.resize(692, 438)
        self.centralWidget = QtWidgets.QWidget(WaveMainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.WavegroupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.WavegroupBox.setGeometry(QtCore.QRect(20, 10, 371, 351))
        self.WavegroupBox.setObjectName("WavegroupBox")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralWidget)
        self.lcdNumber.setGeometry(QtCore.QRect(490, 40, 64, 23))
        self.lcdNumber.setObjectName("lcdNumber")
        self.StartpushButton = QtWidgets.QPushButton(self.centralWidget)
        self.StartpushButton.setGeometry(QtCore.QRect(470, 210, 75, 23))
        self.StartpushButton.setObjectName("StartpushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit.setGeometry(QtCore.QRect(460, 130, 121, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(460, 160, 121, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(420, 130, 31, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(420, 160, 21, 16))
        self.label_2.setObjectName("label_2")
        WaveMainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(WaveMainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 692, 23))
        self.menuBar.setObjectName("menuBar")
        WaveMainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(WaveMainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        WaveMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(WaveMainWindow)
        self.statusBar.setObjectName("statusBar")
        WaveMainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(WaveMainWindow)
        QtCore.QMetaObject.connectSlotsByName(WaveMainWindow)

    def retranslateUi(self, WaveMainWindow):
        _translate = QtCore.QCoreApplication.translate
        WaveMainWindow.setWindowTitle(_translate("WaveMainWindow", "WaveMainWindow"))
        self.WavegroupBox.setTitle(_translate("WaveMainWindow", "WaveGroupBox"))
        self.StartpushButton.setText(_translate("WaveMainWindow", "SCAN"))
        self.label.setText(_translate("WaveMainWindow", "SART"))
        self.label_2.setText(_translate("WaveMainWindow", "END"))


