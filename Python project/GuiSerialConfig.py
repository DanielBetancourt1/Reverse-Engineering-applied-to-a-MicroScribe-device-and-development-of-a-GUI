
# - This script function launch the GUI to select the serial port settings and return these
# in order to start a serial communication.

import sys
from os import getcwd, path
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication, QStyle

import platform
import serial
from serial.tools import list_ports

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # High DPI Scaling
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # High DPI Icons

# Define function to import external files when using PyInstaller.
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

def portsavailable():
    Ports = serial.tools.list_ports.comports()
    Lp = [] #Listport
    for element in Ports:
        Lp.append(element.device)
    return Lp

def guiserial():
    GuiFilePathGuiSerial = resource_path("SerialConfigWindowHighDPI.ui")  # Find Ui file
    # Load the file with the GUI layout, buttons and widgets.
    Ui_MainWindow, QtBaseClass = uic.loadUiType(GuiFilePathGuiSerial)
    
    class SerialConfigWindow(QtWidgets.QMainWindow, Ui_MainWindow):
        def __init__(self):
            
            QtWidgets.QMainWindow.__init__(self)
            Ui_MainWindow.__init__(self)
            self.setupUi(self)

            self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_ComputerIcon')))
            
            OS = platform.system() + ' ' + platform.release()
            self.OSlabel.setText(OS)
            self.setFixedSize(self.size())
            
            self.RetryButton.setEnabled(False)
            self.RetryButton.setVisible(False)
            
            Lp = portsavailable()
            if len(Lp)>0:
                self.AvaPortlbl.setText('Select an available port:')
                self.ListPort.addItems(Lp)
                self.RetryButton.setEnabled(False)
                self.RetryButton.setVisible(False)
            else:
                self.AvaPortlbl.setText('There aren\'t available ports:')
                self.OkButton.setEnabled(False)
                self.RetryButton.setEnabled(True)
                self.RetryButton.setVisible(True)
                
            self.ListPort.itemSelectionChanged.connect(self.selectionChanged)
            self.OkButton.clicked.connect(self.on_Okclick)
            self.CancellButtom.clicked.connect(self.on_Cancellclick)
            self.RetryButton.clicked.connect(self.on_Retryclick)

            global port  # Global variable to return the value in the same way that a function does.
            global Brate  # Global variable to return the value in the same way that a function does.
            Brate = 0
            port = ''

        def selectionChanged(self):

            global port  # Global variable to return the value in the same way that a function does.
            port = self.ListPort.currentItem().text()
            self.OkButton.setEnabled(True)
            self.OkButton.setFocus(True)
            self.OkButton.setDefault(True)

        def on_Okclick(self):

            global Brate  # Global variable to return the value in the same way that a function does.

            if self.B9600.isChecked():
                Brate = 9600
            elif self.B14400.isChecked():
                Brate = 14400
            elif self.B19200.isChecked():
                Brate = 19200
            elif self.B38400.isChecked():
                Brate = 38400
            elif self.B57600.isChecked():
                Brate = 57600
            else:  # if (self.B115200.isChecked()):
                Brate = 115200
           
            self.close()
            
        def on_Cancellclick(self):
            global Brate
            global port
            Brate = 0
            port = ''
            self.close()
            print('The serial parameters were not configured')

        def on_Retryclick(self):
            Answer = QMessageBox.question(self, "Scan ports.", "Do you want to scan ports again?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if Answer == QMessageBox.Yes: 
                Lp = portsavailable()
                if len(Lp) > 0:
                    self.AvaPortlbl.setText('Select an available port:')
                    self.ListPort.addItems(Lp)
                    self.RetryButton.setEnabled(False)
                    self.RetryButton.setVisible(False)
                else:
                    self.AvaPortlbl.setText('There aren\'t available ports:')
                    self.OkButton.setEnabled(False)
                    self.RetryButton.setEnabled(True)
                    self.RetryButton.setVisible(True)
            else: 
                self.close()
                print('The serial parameters were not configured')

    def main():
        app = QApplication(sys.argv)
        # Enable High DPI display with PyQt5

        window = SerialConfigWindow()
        window.show()
        try:
            sys.exit(app.exec_())
        except SystemExit:
            pass

    if __name__ == '__main__':
        main()
    
    main()
    return port, Brate
