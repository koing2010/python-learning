# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(651, 470)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(10, 50, 54, 12))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(10, 90, 54, 12))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralWidget)
        self.label_3.setGeometry(QtCore.QRect(10, 130, 54, 12))
        self.label_3.setObjectName("label_3")
        self.PortBox = QtWidgets.QComboBox(self.centralWidget)
        self.PortBox.setGeometry(QtCore.QRect(100, 50, 69, 22))
        self.PortBox.setObjectName("PortBox")
        self.BaudBox = QtWidgets.QComboBox(self.centralWidget)
        self.BaudBox.setGeometry(QtCore.QRect(100, 90, 69, 22))
        self.BaudBox.setObjectName("BaudBox")
        self.BaudBox.addItem("")
        self.BaudBox.addItem("")
        self.BaudBox.addItem("")
        self.BaudBox.addItem("")
        self.BaudBox.addItem("")
        self.BitBox = QtWidgets.QComboBox(self.centralWidget)
        self.BitBox.setGeometry(QtCore.QRect(100, 120, 69, 22))
        self.BitBox.setObjectName("BitBox")
        self.BitBox.addItem("")
        self.ParityBox = QtWidgets.QComboBox(self.centralWidget)
        self.ParityBox.setGeometry(QtCore.QRect(100, 160, 69, 22))
        self.ParityBox.setObjectName("ParityBox")
        self.ParityBox.addItem("")
        self.label_4 = QtWidgets.QLabel(self.centralWidget)
        self.label_4.setGeometry(QtCore.QRect(10, 160, 61, 16))
        self.label_4.setObjectName("label_4")
        self.label_6 = QtWidgets.QLabel(self.centralWidget)
        self.label_6.setGeometry(QtCore.QRect(10, 200, 54, 12))
        self.label_6.setObjectName("label_6")
        self.StopBox = QtWidgets.QComboBox(self.centralWidget)
        self.StopBox.setGeometry(QtCore.QRect(100, 200, 69, 22))
        self.StopBox.setObjectName("StopBox")
        self.StopBox.addItem("")
        self.OpenSerialButton = QtWidgets.QPushButton(self.centralWidget)
        self.OpenSerialButton.setGeometry(QtCore.QRect(100, 240, 71, 23))
        self.OpenSerialButton.setObjectName("OpenSerialButton")
        self.textEdit = QtWidgets.QTextEdit(self.centralWidget)
        self.textEdit.setGeometry(QtCore.QRect(200, 30, 301, 291))
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralWidget)
        self.textEdit_2.setGeometry(QtCore.QRect(200, 330, 221, 31))
        self.textEdit_2.setObjectName("textEdit_2")
        self.SendButton = QtWidgets.QPushButton(self.centralWidget)
        self.SendButton.setGeometry(QtCore.QRect(430, 330, 75, 31))
        self.SendButton.setObjectName("SendButton")
        self.Damping = QtWidgets.QTextEdit(self.centralWidget)
        self.Damping.setGeometry(QtCore.QRect(520, 50, 104, 21))
        self.Damping.setObjectName("Damping")
        self.label_5 = QtWidgets.QLabel(self.centralWidget)
        self.label_5.setGeometry(QtCore.QRect(520, 30, 71, 16))
        self.label_5.setObjectName("label_5")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 651, 23))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.OpenSerialButton.clicked.connect(self.OpenSerialPort)
        self.PortBox.currentIndex()
    def OpenSerialPort(self):
        print("OPEN CLICKED")
        print("port %d",self.PortBox.currentIndex())
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "串口"))
        self.label_2.setText(_translate("MainWindow", "波特率"))
        self.label_3.setText(_translate("MainWindow", "数据位"))
        self.BaudBox.setItemText(0, _translate("MainWindow", "9600"))
        self.BaudBox.setItemText(1, _translate("MainWindow", "19200"))
        self.BaudBox.setItemText(2, _translate("MainWindow", "38400"))
        self.BaudBox.setItemText(3, _translate("MainWindow", "57600"))
        self.BaudBox.setItemText(4, _translate("MainWindow", "115200"))
        self.BitBox.setItemText(0, _translate("MainWindow", "8"))
        self.ParityBox.setItemText(0, _translate("MainWindow", "0"))
        self.label_4.setText(_translate("MainWindow", "校验位"))
        self.label_6.setText(_translate("MainWindow", "停止位"))
        self.StopBox.setItemText(0, _translate("MainWindow", "1"))
        self.OpenSerialButton.setText(_translate("MainWindow", "打开串口"))
        self.SendButton.setText(_translate("MainWindow", "发送"))
        self.label_5.setText(_translate("MainWindow", "前置衰减db"))


