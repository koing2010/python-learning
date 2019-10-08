import uiwindow
import  sys
from PyQt5 import QtWidgets, QtGui

class Window(uiwindow.Ui_MainWindow):
    def __init__(self):
        uiwindow.Ui_MainWindow.setupUi.__init__(self)
        uiwindow.Ui_MainWindow.retranslateUi.__init__(self)
    def OpenSerialPort(self):
        print("OPEN CLICKED TTTT")
        print("Port ", self.PortBox.currentIndex())
        print("BaudRate ",self.BaudBox.currentText())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QMainWindow()
    ex = Window()
    ex.setupUi(w)
    w.show()

    sys.exit(app.exec_())
