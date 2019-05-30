# - This script was developed in order to generate an alternative to the original MicroScribe software, adding
# compatibility with multiple platforms, and OS versions in which python can be executed. Some additional features
# were added to expand the original functions of the software.

# - This project was carried out in the EAFIT University in Medellin Colombia, where this digitizer
# was about to be thrown away due to the obsolescence of the software. At the moment this device can be used to digitize
# data from impellers and the obtained data can be easily used in the incorporated GUI or exported to other software.

# - # @Autor. This entire project was developed for Juan Daniel Isaza, Mechanical engineer from EAFIT University.

#%% - Main script

# - Import required libraries

from datetime import datetime
start = datetime.now()
import sys
from os import makedirs, path
from numpy import *
from sympy.solvers import solve
from sympy import symbols

# - Libraries for the GUI
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QStyle, QAction, QSystemTrayIcon

from matplotlib.backends.qt_compat import QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

# - Import specific functions (Modules) required for the communication, read and data processing.
import Protocolo as prot
import Read as R
import SerialConfig as SC
import GuiSerialConfig as GUIserial

# Enable High DPI display with PyQt5
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    # High DPI Scaling

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    # High DPI Icons

try:
    [port, Brate] = GUIserial.guiserial()  # Call the GUI for the serial parameters.

    if port != '' and Brate != 0:
        settings = SC.configport(port, Brate)
    else:
        print('Cancelling execution: Corrupt Serial Port parameters')
        sys.exit()

    TxRx = settings[0]

    [Encoderfactor, cA, sA, A, D, cB, sB, D_ID, Pnm, MN, SN, CS, PF, FV] = prot.protocolo(TxRx)  # Start communications.

    # - Start Class to Update coordinates (Multi Thread).
    class UpdateCoordinatesClass(QThread):
        def __init__(self, parent=None):
            super(UpdateCoordinatesClass, self).__init__(parent)

            self.M = empty((0, 3), int)
            self.pedal = 'None'
            self.coordinates = empty((0, 3), int)
            self.TimeNow_NewData = datetime.now()
            self.TimeAfter_NewData = datetime.now()
            self.TimeTol = 1000  # Tolerance in time [ms]

        newdata = pyqtSignal(list)

        def run(self):
            while self.Doloop:

                TxRx.flushInput()
                [self.M, self.coordinates, self.pedal] = R.read(TxRx, Encoderfactor, cA, sA, A, D, cB, sB)

                # - Avoid capture multiple data with a single pedal press
                if self.pedal != 'None':
                    self.TimeNow_NewData = datetime.now()
                    difference = self.TimeNow_NewData - self.TimeAfter_NewData
                    if (int(difference.total_seconds() * 1000)) > self.TimeTol:
                        self.pedal = self.pedal
                    else:
                        self.pedal = 'None'
                    self.TimeAfter_NewData = datetime.now()

                self.newdata.emit([self.M, self.coordinates, self.pedal])


    # Define function to import external files when using PyInstaller.
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(".")

        return path.join(base_path, relative_path)

    # - Start GUI Class.
    GuiFilePathMainWindow = resource_path("MainFunctionsHighDPI.ui")  # Find Ui file
    # Load the file with the GUI layout, buttons and widgets.
    Ui_MainWindow, QtBaseClass = uic.loadUiType(GuiFilePathMainWindow)

    class MSGUI(QtWidgets.QMainWindow, Ui_MainWindow):
        def __init__(self):
            QtWidgets.QMainWindow.__init__(self)
            Ui_MainWindow.__init__(self)
            self.setupUi(self)

            # - Set configuration for the Window.
            self.setWindowTitle('New MicroScribe Utility Software')
            self.setWindowIcon(QtGui.QIcon(resource_path('MsIcon')))
            self.setFixedSize(self.size())

            # - Set initial values for Widgets.
            # Some others values were assigned previously in the Qt designer console.
            self.Pnmlbl.setText(str(Pnm))
            self.MNlbl.setText(str(MN))
            self.SNlbl.setText(str(SN))
            self.D_IDlbl.setText(str(D_ID))
            self.FVlbl.setText(str(FV))
            self.CSlbl.setText(str(CS))
            self.PFlbl.setText(str(PF))
            self.Mail.setText(u'<p> Juan Isaza <a href='"'mailto:jisazab@eafit.edu.co'"'>jisazab@eafit.edu.co</a>  </p>')


            self.tabWidget.setCurrentIndex(0)
            self.Digits.setValue(4)
            self.InstructionsBtn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
            self.InstructionsBtnDIP.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
            self.InstructionsBtn_SP.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))

            # Header labels for tables
            self.MdataLtable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Manually data left table
            self.MdataRtable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Manually data Right table
            self.Adatatable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Automatic data table
            self.ERtable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Estimate radius data table
            self.ScanPlanesTable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Scan planes data table
            self.Captureddatatable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Data in plane table
            self.TwoDdatatable.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Data in plane table
            self.PlaneAngle1Table.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Angle between planes table
            self.PlaneAngle2Table.setHorizontalHeaderLabels(['X', 'Y', 'Z'])  # Angle between planes table
            self.actualtable = QtWidgets.QTableWidget()  # Table for copy data

            # - Setting the plot
            self.canvas = ThreeDplot(self)
            self.canvas.move(135, 16)

            # - Initializing variables.
            self.Units = 'mm'  # By default
            self.Digit = self.Digits.value()  # 4 digits (Decimals) by default
            self.pedal = 'None'
            self.Doloop = True  # Start loop to read coordinates
            self.coordinates = empty((0, 3), int)
            self.coordinatesi = [0, 0, 0]
            self.coordinatesO = [0, 0, 0]
            self.coordinatesA = [0, 0, 0]
            self.Origin = [0, 0, 0]
            self.M = empty((3, 3), int)
            self.Originlabel.setText(str(self.Origin))

            # - Arrays to save data
            self.MdataLP = empty((0, 3), int)  # Manually data left pedal
            self.MdataRP = empty((0, 3), int)  # Manually data left pedal
            self.Adata = empty((0, 3), int)  # Automatic data array
            self.Rpoint = empty((0, 3), int)  # Estimate Radius point
            self.ScanPlanesData = empty((0, 3), int)  # Scan planes Data
            self.Dinplane = empty((0, 3), int)  # Data in plane
            self.Doutplane = empty((0, 3), int)  # Data out the plane
            self.PlaneAngle1A = empty((0, 3), int)  # Estimate angle Array plane 1
            self.PlaneAngle2A = empty((0, 3), int)  # Estimate angle Array plane 2

            # - Automatic data variables
            self.Adatanumber = 0  # Automatic data capture each ...
            self.now = datetime.now()
            self.after = datetime.now()
            self.Autocollect = False

            # - Measure length variables
            self.X1, self.Y1, self.Z1 = [0, 0, 0]
            self.X2, self.Y2, self.Z2 = [0, 0, 0]
            self.Delta = empty((0, 3), int)
            self.direction = empty((0, 3), int)
            self.distance = 0

            # - Initializing variables for estimate radius.
            self.V = empty((0, 3), int)  # Initialize vector array between points
            self.Vu = empty((0, 3), int)  # Initialize unit vector array between points
            self.t = empty((0, 3), int)  # Coordinates for Tail vector for estimate radius
            self.N = empty((0, 3), int)  # Normal vector array for estimate radius
            self.Mx = empty((0, 3), int)  # Mediatrix vector array for estimate radius
            self.center = empty((0, 3), int)  # Center vector array for estimate radius
            self.R = empty((0, 1), int)  # Radius vector array for estimate
            self.center = 0
            self.Radius = 0
            self.Nv = 0

            # - Scan planes variables
            self.Ppoint_SP = empty((0, 3), int)
            self.Ppoint_SPR = empty((0, 3), int)
            self.Normal_SP = empty((0, 3), int)
            self.EndPoint_SP = empty((0, 3), int)
            self.Pip_SP = 0
            self.d_toPlane_SP = 0
            self.partitions = 0
            self.PlanesToScan = empty((0, 3), int)
            self.PlanesToScan_O = empty((0, 3), int)
            self.Tol_SC = 2
            self.ScanPlanesBool = False
            self.Actualdistance = 0
            self.d_toOrigin_SP = 0
            self.d_OriginToEp_SP = 0

            # - Data in plane variables
            self.Planepoint = empty((0, 3), int)
            self.Ppointr = empty((0, 3), int)
            self.Nu = empty((0, 3), int)  # Plane unit vector
            self.d = 0
            self.Pfi = empty((0, 3), int)

            # - Angle between planes variables
            self.Normal1 = empty((0, 3), int)
            self.Normal2 = empty((0, 3), int)
            self.dist1 = 0
            self.dist2 = 0

            # - Connections to functions

            self.Digits.valueChanged.connect(self.Digitvalue)
            self.tabWidget.currentChanged.connect(self.TabChange)
            self.tabWidget.currentChanged.connect(self.updatePlot)
            self.OriginBtn.clicked.connect(self.on_Origin)
            self.InBtn.toggled.connect(self.UnitsInches)
            self.AdataValue.textChanged.connect(self.AdataVchange)
            self.StartAutoData.clicked.connect(self.StartAutotada)
            self.StopAutoData.clicked.connect(self.StopAutotada)
            self.StartStopBtn_SP.clicked.connect(self.EnableScanPlanes)

            self.InstructionsBtn.clicked.connect(self.ERinstructions)
            self.InstructionsBtn_SP.clicked.connect(self.SPinstructions)
            self.InstructionsBtnDIP.clicked.connect(self.DIPinstructions)

            # - Delete data buttons
            self.DeleteDataL.clicked.connect(self.On_deleteLeft)
            self.DeleteDataR.clicked.connect(self.On_deleteRight)
            self.DeleteAutoData.clicked.connect(self.On_DeleteAutoData)
            self.DeleteDataRadius.clicked.connect(self.On_DeleteDataRadius)
            self.Delete_SP.clicked.connect(self.On_DeleteSP)
            self.DeleteDIP.clicked.connect(self.On_DeleteDIP)
            self.DeleteABP.clicked.connect(self.On_DeleteABP)

            # - Start thread to update coordinates
            self.threadCoordinates = UpdateCoordinatesClass()
            self.threadCoordinates.Units = self.Units
            self.threadCoordinates.Doloop = self.Doloop
            self.threadCoordinates.start()
            self.threadCoordinates.newdata.connect(self.updateCoordinates)

            # - Selection, copy and delete data variables.
            self.AllArrays = [self.MdataLP, self.MdataRP, self.Adata, self.Rpoint,
                              self.ScanPlanesData, self.Dinplane, self.Doutplane,
                              self.PlaneAngle1A, self.PlaneAngle2A]
            self.AllArraysi = zeros_like(self.AllArrays)
            self.AllArrays_others = []
            self.selectedData = empty((0, 3), int)
            self.clip = QtWidgets.QApplication.clipboard()

            #  Update current table (Widget)
            self.MdataLtable.cellClicked.connect(self.MdataLtableSelect)
            self.MdataLtable.currentCellChanged.connect(self.MdataLtableSelect)
            self.MdataRtable.cellClicked.connect(self.MdataRtableSelect)
            self.MdataRtable.currentCellChanged.connect(self.MdataRtableSelect)
            self.Adatatable.clicked.connect(self.SelectedDatainActualTable)
            self.Adatatable.currentCellChanged.connect(self.SelectedDatainActualTable)
            self.ERtable.clicked.connect(self.SelectedDatainActualTable)
            self.ERtable.currentCellChanged.connect(self.SelectedDatainActualTable)
            self.ScanPlanesTable.clicked.connect(self.SelectedDatainActualTable)
            self.ScanPlanesTable.currentCellChanged.connect(self.SelectedDatainActualTable)
            self.Captureddatatable.cellClicked.connect(self.SelectedCaptureddatatable)
            self.Captureddatatable.currentCellChanged.connect(self.SelectedCaptureddatatable)
            self.TwoDdatatable.cellClicked.connect(self.SelectedCaptureddatatable)
            self.TwoDdatatable.currentCellChanged.connect(self.SelectedCaptureddatatable)
            self.PlaneAngle1Table.cellClicked.connect(self.SelectedPlaneAngle1Table)
            self.PlaneAngle1Table.currentCellChanged.connect(self.SelectedPlaneAngle1Table)
            self.PlaneAngle2Table.cellClicked.connect(self.SelectedPlaneAngle2Table)
            self.PlaneAngle2Table.currentCellChanged.connect(self.SelectedPlaneAngle2Table)
            self.actualtable.currentCellChanged.connect(self.SelectedDatainActualTable)

            # - GUI general buttons
            self.Exportplot.clicked.connect(self.on_Exportplot)
            self.ExportAllDataBtn.clicked.connect(self.on_ExportAllData)
            self.ExportActualDataBtn.clicked.connect(self.on_ExportData)
            self.DelSelection.clicked.connect(self.on_DeleteData)
            self.EndButton.clicked.connect(self.on_EndButton)

        def updateCoordinates(self, result):

            [self.M, self.coordinates, self.pedal] = result

            global mmBtnChecked  # In order to share this data between classes
            mmBtnChecked = self.mmBtn.isChecked()
            if self.mmBtn.isChecked():
                self.Units = 'mm'
                self.coordinates = self.coordinates * 25.4
            else:
                self.Units = 'In'

            coordinatesO = self.coordinates - self.Origin
            coordinatesO = [round(elem, self.Digit) for elem in coordinatesO]
            self.coordinatesO = coordinatesO

            self.PedalStatus.setText(self.pedal)

            if self.pedal != 'None':
                self.NewData()

            if linalg.norm(
                    self.coordinates - self.coordinatesi) != 0 or self.pedal != 'None':  # If there are any change
                self.updatePlot()

                # - Check here the functions that auto capture data.
                if self.tabWidget.currentIndex() == 1:  # Take data automatically.

                    if self.Autocollect is True:

                        if self.AutoUnits.isChecked() and \
                                linalg.norm(self.coordinates - self.coordinatesA) >= self.Adatanumber:
                            self.coordinatesA = self.coordinates
                            self.NewData()

                        self.now = datetime.now()
                        difference = self.now - self.after
                        if self.Automs.isChecked() and (int(difference.total_seconds() * 1000)) >= self.Adatanumber:
                            self.after = self.now
                            self.NewData()

                if self.tabWidget.currentIndex() == 4:  # Scan planes.

                    if size(self.EndPoint_SP) == 3 and self.partitions != 0 and self.ScanPlanesBool is True:
                        VectorP_P = array(self.coordinatesO) - self.Pip_SP  # Vector actual coordinate to plane
                        self.Actualdistance = VectorP_P.dot(self.Normal_SP)

                        if isclose(self.PlanesToScan, self.Actualdistance, atol=self.Tol_SC).any():
                            self.CapturePlane()

            self.coordinatesi = self.coordinates

        def NewData(self):

            if self.tabWidget.currentIndex() == 0:  # Take data manually

                if self.pedal == 'left':
                    if not all(isin(self.coordinatesO,
                                    self.MdataLP)):  # Check if all coordinates are new in this array.

                        self.MdataLP = vstack((array(self.MdataLP), self.coordinatesO))  # Save data from pedal

                        rowPosition = self.MdataLtable.rowCount()

                        self.MdataLtable.insertRow(rowPosition)
                        #  display captured data
                        self.MdataLtable.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                        self.MdataLtable.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                        self.MdataLtable.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

                if self.pedal == 'Right':
                    if not all(isin(self.coordinatesO,
                                    self.MdataRP)):  # Check if all coordinates are new in this array.

                        self.MdataRP = vstack((array(self.MdataRP), self.coordinatesO))  # Save data from pedal
                        rowPosition = self.MdataRtable.rowCount()

                        self.MdataRtable.insertRow(rowPosition)
                        #  display captured data
                        self.MdataRtable.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                        self.MdataRtable.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                        self.MdataRtable.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

            elif self.tabWidget.currentIndex() == 1:  # Take data automatically.

                if not all(isin(self.coordinatesO,
                                self.Adata)):  # Check if all coordinates are new in this array.

                    self.Adata = vstack((array(self.Adata), self.coordinatesO))  # Save data from pedal
                    rowPosition = self.Adatatable.rowCount()

                    self.Adatatable.insertRow(rowPosition)
                    #  display captured data
                    self.Adatatable.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                    self.Adatatable.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                    self.Adatatable.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

            elif self.tabWidget.currentIndex() == 2:  # Measure length.

                if self.pedal == 'left':
                    self.X1 = self.coordinatesO[0]
                    self.Y1 = self.coordinatesO[1]
                    self.Z1 = self.coordinatesO[2]

                    self.Xp1.setText(str(self.coordinatesO[0]))
                    self.Yp1.setText(str(self.coordinatesO[1]))
                    self.Zp1.setText(str(self.coordinatesO[2]))

                if self.pedal == 'Right':
                    self.X2 = self.coordinatesO[0]
                    self.Y2 = self.coordinatesO[1]
                    self.Z2 = self.coordinatesO[2]

                    self.Xp2.setText(str(self.coordinatesO[0]))
                    self.Yp2.setText(str(self.coordinatesO[1]))
                    self.Zp2.setText(str(self.coordinatesO[2]))

                if self.X1 != 0 and self.X2 != 0:
                    Dx = self.X2 - self.X1
                    Dy = self.Y2 - self.Y1
                    Dz = self.Z2 - self.Z1
                    Delta = [Dx, Dy, Dz]
                    self.Delta = [round(elem, self.Digit) for elem in Delta]

                    self.labelDelta.setText(str(self.Delta))

                    self.distance = round(sqrt((Dx) ** 2 + (Dy) ** 2 + (Dz) ** 2), self.Digit)

                    self.labelDistance.setText(str(self.distance) + ' ' + str(self.Units))
                    if self.distance != 0:
                        self.direction = [x / self.distance for x in self.Delta]  # Unit vector
                        self.direction = [round(elem, self.Digit) for elem in self.direction]
                        self.labelDirection.setText(str(self.direction))
                    else:
                        self.labelDirection.setText(str(0))

            elif self.tabWidget.currentIndex() == 3:  # Estimate radius.

                if not all(isin(self.coordinatesO, self.Rpoint)):  # Check if all coordinates are new in this array.

                    if self.pedal == 'left' or self.pedal == 'Right':
                        self.Rpoint = vstack((array(self.Rpoint), self.coordinatesO))  # Save data from pedal
                        rowPosition = self.ERtable.rowCount()

                        self.ERtable.insertRow(rowPosition)
                        #  display captured data
                        self.ERtable.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                        self.ERtable.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                        self.ERtable.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

                        if len(self.Rpoint) >= 3:
                            self.EstimateRadiusfunction()
                        else:
                            self.Centerlbl.setText(str(''))
                            self.Radiouslbl.setText(str(''))
                            self.NormalVectorlbl.setText(str(''))

            elif self.tabWidget.currentIndex() == 4:  # Scan planes.

                if self.pedal == 'left':

                    if not all(isin(self.coordinatesO,
                                    self.Ppoint_SP)):  # Check if all coordinates are new in this array.

                        if size(self.Ppoint_SP) < 9:
                            self.Ppoint_SP = vstack((self.Ppoint_SP, self.coordinatesO))  # Save data from pedal

                            self.Ppoint_SPR = around(self.Ppoint_SP, decimals=2)  # Round all elements inside the array
                            self.PointsLbl_SP.setText(str(self.Ppoint_SPR))

                        elif size(self.Ppoint_SP) == 9 and size(self.EndPoint_SP) < 3:
                            self.EndPoint_SP = vstack((self.EndPoint_SP, self.coordinatesO))

                            self.EndPoint_SPR = around(self.EndPoint_SP,
                                                       decimals=2)  # Round all elements inside the array
                            self.StopPointLbl.setText(str(self.EndPoint_SPR))

                        elif size(self.Ppoint_SP) == 9 and size(self.EndPoint_SP) == 3:
                            Answer = QMessageBox.question(self, "Redefine Plane.",
                                                          "Do you want to redefine the plane and delete captured data?"
                                                          , QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if Answer == QMessageBox.Yes:
                                self.On_DeleteSP()

                        if size(self.Ppoint_SP) == 9:  # If all required points to compute the plane were digitized.
                            Normal_SP = self.ComputeNormal(self.Ppoint_SP)  # Unit normal

                            if linalg.norm(Normal_SP) != 0:
                                self.Normal_SP = Normal_SP
                                Normal_SPR = around(self.Normal_SP, decimals=3)
                                self.NormalLbl_SP.setText(str(Normal_SPR))

                            else:
                                self.On_DeleteSP()

                        if size(self.EndPoint_SP) == 3 and self.partitions == 0:
                            self.Pip_SP = self.Ppoint_SP[0]  # A point in the plane
                            VectorP_P = self.EndPoint_SP - self.Pip_SP  # Vector point to plane
                            VectorO_P = zeros(3) - self.Pip_SP  # Vector Origin to plane
                            VectorO_EP = zeros(3) - self.EndPoint_SPR  # Vector Origin to End point
                            self.d_toPlane_SP = VectorP_P.dot(self.Normal_SP)
                            self.d_toOrigin_SP = VectorO_P.dot(self.Normal_SP)
                            self.d_OriginToEp_SP = VectorO_EP.dot(self.Normal_SP)  # Dist. from origin to end point

                            self.partitions = abs(self.d_toPlane_SP / self.NPlanes_SP.value())  # Separation between planes
                            self.PlanesToScan = linspace(0, self.d_toPlane_SP, self.NPlanes_SP.value())

                            self.PlanesToScan_O = linspace(self.d_toOrigin_SP, self.d_OriginToEp_SP,
                                                           self.NPlanes_SP.value())

                            self.Tol_SC = int(self.partitions / 20)  # Tolerance to capture plane
                            self.StartStopBtn_SP.setEnabled(True)
                            self.StartStopBtn_SP.setDefault(True)
                            self.StartStopBtn_SP.setFocus()

                if self.pedal == 'Right':
                    self.CapturePlane()

            elif self.tabWidget.currentIndex() == 5:  # data in plane.

                if self.pedal == 'left':

                    if not all(isin(self.coordinatesO,
                                    self.Planepoint)):  # Check if all coordinates are new in this array.

                        if len(self.Planepoint) < 3:
                            self.Planepoint = vstack(
                                (array(self.Planepoint), self.coordinatesO))  # Save data from pedal

                            self.Ppointr = around(self.Planepoint, decimals=2)  # Round all elements inside the array
                            self.PointsLbl.setText(str(self.Ppointr))

                        elif len(self.Planepoint) == 3:
                            Answer = QMessageBox.question(self, "Redefine Plane.",
                                                          "Do you want to redefine the plane and delete captured data?"
                                                          , QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if Answer == QMessageBox.Yes:
                                self.On_DeleteDIP()

                    if len(self.Planepoint) == 3:  # If all required points to compute the plane were digitized.

                        cp = self.ComputeNormal(self.Planepoint)

                        if linalg.norm(cp) != 0:
                            cp = cp / linalg.norm(cp)
                            self.Nu = array(cp)
                            cp = around(cp, decimals=3)
                            self.NormalLbl.setText(str(cp))
                            Pin = self.Planepoint[0]  # Point in the plane
                            self.d = -Pin.dot(self.Nu)

                        else:
                            self.Planepoint = empty((0, 3), int)
                            self.NormalLbl.setText(str(''))
                            self.PointsLbl.setText(str(''))

                if self.pedal == 'Right':
                    self.Doutplane = vstack((self.Doutplane, self.coordinatesO))  # Save data from pedal
                    rowPosition = self.Captureddatatable.rowCount()

                    self.Captureddatatable.insertRow(rowPosition)
                    #  display captured data
                    self.Captureddatatable.setItem(rowPosition, 0,
                                                   QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                    self.Captureddatatable.setItem(rowPosition, 1,
                                                   QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                    self.Captureddatatable.setItem(rowPosition, 2,
                                                   QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

                    if linalg.norm(self.Nu) != 0:
                        self.ProjectData()

            elif self.tabWidget.currentIndex() == 6:  # Angle between plane.

                if self.pedal == 'left':

                    if not all(isin(self.coordinatesO,
                                    self.PlaneAngle1A)):  # Check if all coordinates are new in this array.

                        self.PlaneAngle1A = vstack((self.PlaneAngle1A, self.coordinatesO))

                        rowPosition = self.PlaneAngle1Table.rowCount()
                        self.PlaneAngle1Table.insertRow(rowPosition)
                        #  display captured data
                        self.PlaneAngle1Table.setItem(rowPosition, 0,
                                                      QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                        self.PlaneAngle1Table.setItem(rowPosition, 1,
                                                      QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                        self.PlaneAngle1Table.setItem(rowPosition, 2,
                                                      QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

                        if len(self.PlaneAngle1A) >= 3:

                            self.Normal1 = self.ComputeNormal(self.PlaneAngle1A)
                            Nm1 = around(self.Normal1, decimals=3)
                            self.Normal1_lbl.setText(str(Nm1))
                        else:
                            self.Normal1_lbl.setText(str(''))

                if self.pedal == 'Right':

                    if not all(isin(self.coordinatesO,
                                    self.PlaneAngle2A)):  # Check if all coordinates are new in this array.

                        self.PlaneAngle2A = vstack((self.PlaneAngle2A, self.coordinatesO))

                        rowPosition = self.PlaneAngle2Table.rowCount()
                        self.PlaneAngle2Table.insertRow(rowPosition)
                        #  display captured data
                        self.PlaneAngle2Table.setItem(rowPosition, 0,
                                                      QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
                        self.PlaneAngle2Table.setItem(rowPosition, 1,
                                                      QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
                        self.PlaneAngle2Table.setItem(rowPosition, 2,
                                                      QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

                        if len(self.PlaneAngle2A) >= 3:
                            self.Normal2 = self.ComputeNormal(self.PlaneAngle2A)
                            Nm2 = around(self.Normal2, decimals=3)
                            self.Normal2_lbl.setText(str(Nm2))
                        else:
                            self.Normal2_lbl.setText(str(''))

                if len(self.PlaneAngle1A) >= 3 and len(self.PlaneAngle2A) >= 3:
                    angle = arccos(dot(self.Normal1, self.Normal2) /
                                   (linalg.norm(self.Normal1) * linalg.norm(self.Normal2)))
                    angled = round(degrees(angle), 3)
                    self.AngleBplanes.setText(str(angled))
                else:
                    self.AngleBplanes.setText(str(''))

            if self.mmBtn.isEnabled():
                self.AllArrays = [self.MdataLP, self.MdataRP, self.Adata, self.Rpoint,
                                  self.ScanPlanesData, self.Dinplane, self.Doutplane,
                                  self.PlaneAngle1A, self.PlaneAngle2A]
                self.AllArrays_others = [self.Origin, self.X1, self.Y1, self.Z1,
                                         self.X2, self.Y2, self.Z2,
                                         self.Ppoint_SP, self.Normal_SP, self.EndPoint_SP,
                                         self.Planepoint, self.Ppointr]

                if not size(self.AllArrays) == 0 or not size(self.AllArrays_others) == 0:
                    self.InBtn.setEnabled(False)
                    self.mmBtn.setEnabled(False)
                    self.OriginBtn.setEnabled(False)

        def updatePlot(self):

            self.Xcoordinate.setText(str(self.coordinatesO[0]))
            self.Ycoordinate.setText(str(self.coordinatesO[1]))
            self.Zcoordinate.setText(str(self.coordinatesO[2]))

            self.canvas.Stylus(x=self.coordinatesO[0], y=self.coordinatesO[1], z=self.coordinatesO[2],
                               Nx=-self.M[0, 2], Ny=-self.M[1, 2], Nz=-self.M[2, 2])  # Call stylus

            if self.tabWidget.currentIndex() == 0:  # Digitize manually.
                self.canvas.plotpointL(x=self.MdataLP[:, 0], y=self.MdataLP[:, 1],
                                       z=self.MdataLP[:, 2])  # Call left plot
                self.canvas.plotpointR(x=self.MdataRP[:, 0], y=self.MdataRP[:, 1],
                                       z=self.MdataRP[:, 2])  # Call Right plot.

            elif self.tabWidget.currentIndex() == 1:  # Digitize automatically
                self.actualtable = self.Adatatable

                self.canvas.plotpointL(x=self.Adata[:, 0], y=self.Adata[:, 1],
                                       z=self.Adata[:, 2], lbl='Automatic data')  # Call left plot

            elif self.tabWidget.currentIndex() != 1 and self.Autocollect is True:
                self.StopAutotada()

            elif self.tabWidget.currentIndex() == 2 and self.distance != 0:  # Measure length.

                self.canvas.plotVector(x=self.X2, y=self.Y2, z=self.Z2,
                                       Nx=self.direction[0], Ny=self.direction[1], Nz=self.direction[2],
                                       distance=self.distance)

            elif self.tabWidget.currentIndex() == 3:  # Estimate radius
                self.actualtable = self.ERtable
                self.canvas.plotpointR(x=self.Rpoint[:, 0], y=self.Rpoint[:, 1],
                                       z=self.Rpoint[:, 2], lbl='Points in curvature')  # Call Blue plot

            elif self.tabWidget.currentIndex() == 4:  # Scan planes.
                self.actualtable = self.ScanPlanesTable

                self.canvas.plotpointR(x=self.Ppoint_SP[:, 0], y=self.Ppoint_SP[:, 1],
                                       z=self.Ppoint_SP[:, 2], lbl='Points in plane')  # Call Blue plot

                self.canvas.plotpointL(x=self.EndPoint_SP[:, 0], y=self.EndPoint_SP[:, 1],
                                       z=self.EndPoint_SP[:, 2], lbl='End point')  # Call left plot

                self.canvas.plotpointOlive(x=self.ScanPlanesData[:, 0], y=self.ScanPlanesData[:, 1],
                                           z=self.ScanPlanesData[:, 2], lbl='Captured plane')  # Call Green plot.

                if size(self.Normal_SP) == 3 and size(self.Ppoint_SP, 0) >= 3 and size(self.EndPoint_SP) >= 3:  # If normal was computed..
                    PlaneRange = self.Ppoint_SP  # vstack((self.Ppoint_SP, self.Dinplane))
                    self.canvas.plotPlane(P=PlaneRange, Nu=self.Normal_SP, d=self.PlanesToScan_O, lbl='Planes')

            elif self.tabWidget.currentIndex() == 5:  # Data in plane.
                self.actualtable = self.Captureddatatable

                self.canvas.plotpointL(x=self.Dinplane[:, 0],
                                       y=self.Dinplane[:, 1],
                                       z=self.Dinplane[:, 2], lbl='Projected data')  # Call Blue plot

                self.canvas.plotpointR(x=self.Doutplane[:, 0],
                                       y=self.Doutplane[:, 1],
                                       z=self.Doutplane[:, 2], lbl='Captured data')  # Call Red plot.

                self.canvas.plotpointOlive(x=self.Planepoint[:, 0],
                                           y=self.Planepoint[:, 1],
                                           z=self.Planepoint[:, 2], lbl='Points in plane')  # Call Green plot.

                if size(self.Nu) == 3 and size(self.Planepoint, 0) == 3:  # If normal was computed..
                    PlaneRange = vstack((self.Planepoint, self.Dinplane))
                    self.canvas.plotPlane(P=PlaneRange, Nu=self.Nu, d=self.d, lbl='Plane')

            elif self.tabWidget.currentIndex() == 6:  # Angle between 2 planes.

                self.canvas.plotpointL(x=self.PlaneAngle1A[:, 0], y=self.PlaneAngle1A[:, 1],
                                       z=self.PlaneAngle1A[:, 2], lbl='Points in Plane 1')  # Call left plot
                self.canvas.plotpointR(x=self.PlaneAngle2A[:, 0], y=self.PlaneAngle2A[:, 1],
                                       z=self.PlaneAngle2A[:, 2], lbl='Points in Plane 2')  # Call Right plot.

                if size(self.Normal1) == 3 and size(self.PlaneAngle1A, 0) == 3:  # If normal was computed..
                    Pipl1 = self.PlaneAngle1A[0]  # Point in the plane 1.
                    self.dist1 = -Pipl1.dot(self.Normal1)
                    self.canvas.plotPlane(P=self.PlaneAngle1A, Nu=self.Normal1, d=self.dist1, lbl='Plane 1')

                if size(self.Normal2) == 3 and size(self.PlaneAngle2A, 0) == 3:  # If normal was computed..
                    Pipl2 = self.PlaneAngle2A[0]  # Point in the plane 1.
                    self.dist2 = -Pipl2.dot(self.Normal2)
                    self.canvas.plotPlane2(P=self.PlaneAngle2A, Nu=self.Normal2, d=self.dist2, lbl='Plane 2')

        def TabChange(self):
            self.canvas.axes.cla()
            self.canvas.axes.set_title('Captured points and Stylus')
            self.canvas.initVariablesPlot()  # Reset variables to draw a new set of plots

        def on_Origin(self):

            Answer = QMessageBox.question(self, "Select Origin.",
                                          "Please move the stylus tip to the new Origin and then press Ok",
                                          QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
            if Answer == QMessageBox.Ok:
                print('New origin')
                self.Origin = self.coordinates
                OriginR = [round(elem, 2) for elem in self.Origin]

                self.Originlabel.setText(str(OriginR))
                coordinatesO = self.coordinates - self.Origin
                self.Xcoordinate.setText(str(coordinatesO[0]))
                self.Ycoordinate.setText(str(coordinatesO[1]))
                self.Zcoordinate.setText(str(coordinatesO[2]))

                self.InBtn.setEnabled(False)
                self.mmBtn.setEnabled(False)
                self.OriginBtn.setEnabled(False)
            else:
                pass

        def UnitsInches(self):

            if (self.mmBtn.isChecked()):
                self.InBtn.setChecked(False)

                self.Origin = [x * 25.4 for x in self.Origin]
                print('Origin units mm', self.Origin)
                OriginR = [round(elem, 2) for elem in self.Origin]  # Display with 2 digits.
                self.Originlabel.setText(str(OriginR))
                self.AutoUnits.setText('mm')
            else:
                self.mmBtn.setChecked(False)

                self.Origin = [x / 25.4 for x in self.Origin]
                print('Origin units In', self.Origin)
                OriginR = [round(elem, 2) for elem in self.Origin]
                self.Originlabel.setText(str(OriginR))
                self.AutoUnits.setText('Inch')

        def Digitvalue(self):
            self.Digit = self.Digits.value()
            # - Update coordinates with the new number of digits
            self.Xcoordinate.setText(str(self.coordinatesO[0]))
            self.Ycoordinate.setText(str(self.coordinatesO[1]))
            self.Zcoordinate.setText(str(self.coordinatesO[2]))

        def AdataVchange(self):
            Adatanumber = self.AdataValue.text()
            try:
                self.Adatanumber = int(Adatanumber)
                self.StartAutoData.setEnabled(True)
                self.StartAutoData.setDefault(True)
                self.StopAutoData.setEnabled(True)

            except Exception:  # Avoid errors
                self.AdataValue.clear()
                self.StartAutoData.setEnabled(False)
                self.StartAutoData.setDefault(False)
                self.StopAutoData.setEnabled(False)
                self.Autocollect = False
                self.Capturelabel.setText('Enter a valid value (integer)')

        def StartAutotada(self):

            self.StopAutoData.setDefault(True)
            self.StartAutoData.setDefault(False)

            if self.Automs.isChecked() and self.Autocollect == False:
                self.AutoUnits.setChecked(False)

                msgBox = QtWidgets.QMessageBox()
                msgBox.setIcon(QtWidgets.QMessageBox.Information)
                msgBox.setWindowTitle("Initial point.")
                msgBox.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
                msgBox.setBaseSize(QtCore.QSize(650, 300))
                msgBox.setText("Please move the stylus tip to the initial point and then press OK.")
                msgBox.setInformativeText("Move the tip SLOWLY.")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok)
                Answer = msgBox.exec_()

                if Answer == QMessageBox.Ok:
                    self.Autocollect = True
                    self.Capturelabel.setText('Capturing data...')
                else:
                    self.Autocollect = False
                    self.Capturelabel.setText('Data Capturing is paused')

            elif self.AutoUnits.isChecked() and self.Autocollect is False:
                self.Automs.setChecked(False)

                msgBox = QtWidgets.QMessageBox()
                msgBox.setIcon(QtWidgets.QMessageBox.Information)
                msgBox.setWindowTitle("Initial point.")
                msgBox.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
                msgBox.setBaseSize(QtCore.QSize(650, 300))
                msgBox.setText("Please move the stylus tip to the initial point and then press OK.")
                msgBox.setInformativeText("Move the tip SLOWLY.")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok)
                Answer = msgBox.exec_()

                if Answer == QMessageBox.Ok:
                    self.Autocollect = True
                    self.Capturelabel.setText('Capturing data...')
                else:
                    self.Autocollect = False
                    self.Capturelabel.setText('Data Capturing is paused')

        def StopAutotada(self):

            self.StopAutoData.setDefault(False)
            self.StartAutoData.setDefault(True)

            self.Autocollect = False
            self.Capturelabel.setText('Data Capturing is paused')

        def EstimateRadiusfunction(self):

            self.V = empty((0, 3), int)  # Initialize vector array between points
            self.Vu = empty((0, 3), int)  # Initialize unit vector array between points
            self.t = empty((0, 3), int)  # Coordinates for Tail vector for estimate radius
            self.N = empty((0, 3), int)  # Normal vector array for estimate radius
            self.Mx = empty((0, 3), int)  # Mediatrix vector array for estimate radius
            self.center = empty((0, 3), int)  # Center vector array for estimate radius
            self.R = empty((0, 1), int)  # Radius vector array for estimate

            for i in range(0, len(self.Rpoint) - 1):
                Vi = array(self.Rpoint[i + 1] - self.Rpoint[i])
                self.V = vstack((self.V, Vi))  # Vector between points

                if linalg.norm(Vi) != 0:
                    Vui = Vi / linalg.norm(Vi)
                    self.Vu = vstack((self.Vu, Vui))  # Unit Vector
                    ti = self.Rpoint[i] + Vui * linalg.norm(self.V[i]) / 2
                    self.t = vstack((self.t, ti))  # tail position of the mediatrix director
                else:
                    break

            for i in range(0, len(self.Vu) - 1):
                Ni = cross(self.Vu[i + 1], self.Vu[i])

                if linalg.norm(Ni) != 0:
                    Ni = Ni / linalg.norm(Ni)
                    self.N = vstack((self.N, Ni))
                else:
                    break

            self.Nv = mean(self.N, axis=0)

            for i in range(0, len(self.Vu)):
                Mi = cross(self.Vu[i], self.Nv)
                self.Mx = vstack((self.Mx, Mi))  # Mediatrix

            for i in range(0, len(self.N)):

                x, y, z = symbols('x y z')
                Eq_1 = (x - self.t[i][0]) * self.Mx[i][1] - (y - self.t[i][1]) * self.Mx[i][0]
                Eq_2 = (x - self.t[i + 1][0]) * self.Mx[i + 1][1] - (y - self.t[i + 1][1]) * self.Mx[i + 1][0]
                Eq_3 = (y - self.t[i][1]) * self.Mx[i][2] - (z - self.t[i][2]) * self.Mx[i][1]
                U = solve([Eq_1, Eq_2, Eq_3], (x, y, z), real=True)

                if len(U) >= 3:
                    centeri = [U[x], U[y], U[z]]
                    self.center = vstack((self.center, centeri))

                    for i in range(0, len(self.Rpoint)):
                        Ri = int((self.Rpoint[i, 0] - U[x]) ** 2 + (self.Rpoint[i, 1] - U[y]) ** 2 + (
                                self.Rpoint[i, 2] - U[z]) ** 2)
                        Rii = sqrt(Ri)
                        self.R = vstack((self.R, Rii))

                    self.Center = mean(self.center, axis=0)
                    Centerlblvalue = around(self.Center.astype(double), decimals=3)
                    self.Centerlbl.setText(str(Centerlblvalue))
                    self.Radius = mean(self.R)
                    Radiouslblvalue = around(self.Radius.astype(double), decimals=self.Digit)
                    self.Radiouslbl.setText(str(Radiouslblvalue))
                    NormalVectorlblvalue = around(self.Nv.astype(double), decimals=3)
                    self.NormalVectorlbl.setText(str(NormalVectorlblvalue))

                else:
                    self.Rpoint = empty((0, 3), int)
                    self.Centerlbl.setText(str(''))
                    self.Radiouslbl.setText(str(''))
                    self.NormalVectorlbl.setText(str(''))
                    self.ERtable.Clearcontents()
                    self.ERtable.setRowCount(0)

        def ComputeNormal(self, PointCloud):

            V = empty((0, 3), int)
            Vu = empty((0, 3), int)
            Nu = empty((0, 3), int)
            N = empty((0, 3), int)

            for i in range(0, len(PointCloud) - 1):
                Vi = array(PointCloud[i + 1] - PointCloud[i])
                V = vstack((V, Vi))  # Vector between points

                if linalg.norm(Vi) != 0:
                    Vui = Vi / linalg.norm(Vi)
                    Vu = vstack((Vu, Vui))  # Unit Vector

            for i in range(0, len(Vu) - 1):
                Ni = cross(Vu[i + 1], Vu[i])

                if linalg.norm(Ni) != 0:
                    Nui = Ni / linalg.norm(Ni)
                    Nu = vstack((Nu, Nui))  # Unit Vector

                N = vstack((N, Nu))

            n = mean(N, axis=0)
            return n

        def EnableScanPlanes(self):

            if size(self.EndPoint_SP) == 3 and self.partitions != 0 and self.ScanPlanesBool is False:
                self.ScanPlanesBool = True
                self.StartStopBtn_SP.setText('Pause/Stop scan')

            else:
                self.ScanPlanesBool = False
                self.StartStopBtn_SP.setText('Start scan')

        def CapturePlane(self):

            self.ScanPlanesData = vstack((array(self.ScanPlanesData), self.coordinatesO))  # Save data from pedal
            rowPosition = self.Captureddatatable.rowCount()

            self.ScanPlanesTable.insertRow(rowPosition)
            #  display captured data
            self.ScanPlanesTable.setItem(rowPosition, 0,
                                         QtWidgets.QTableWidgetItem(str(self.coordinatesO[0])))
            self.ScanPlanesTable.setItem(rowPosition, 1,
                                         QtWidgets.QTableWidgetItem(str(self.coordinatesO[1])))
            self.ScanPlanesTable.setItem(rowPosition, 2,
                                         QtWidgets.QTableWidgetItem(str(self.coordinatesO[2])))

        def ProjectData(self):

            self.TwoDdatatable.clearContents()
            self.TwoDdatatable.setRowCount(0)
            Pin = self.Planepoint[0]  # Point in the plane.
            self.d = -Pin.dot(self.Nu)
            self.Pfi = empty((0, 3), int)  # Final point.

            for indx, point in enumerate(self.Doutplane):
                self.Pfi = point + dot((Pin - point), self.Nu) * self.Nu  # Final point
                self.Pfi = around(self.Pfi, decimals=self.Digit)

                self.Dinplane = vstack((self.Dinplane, self.Pfi))

                if len(self.Pfi) == 3:
                    rowPosition = self.TwoDdatatable.rowCount()
                    self.TwoDdatatable.insertRow(rowPosition)
                    #  display captured data
                    self.TwoDdatatable.setItem(rowPosition, 0,
                                               QtWidgets.QTableWidgetItem(str(self.Pfi[0])))
                    self.TwoDdatatable.setItem(rowPosition, 1,
                                               QtWidgets.QTableWidgetItem(str(self.Pfi[1])))
                    self.TwoDdatatable.setItem(rowPosition, 2,
                                               QtWidgets.QTableWidgetItem(str(self.Pfi[2])))

        def ERinstructions(self):  # Estimate radius instructions

            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Estimate radius instructions")
            msg.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
            msg.setBaseSize(QtCore.QSize(650, 300))
            msg.setText("Digitize at least 3 points along the curvature trying to stay in the same plane in which"
                        " curvature is.")
            msg.setInformativeText("Digitize data only in one direction (Clockwise or anticlockwise)")
            msg.exec_()

        def SPinstructions(self):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Scan instructions")
            msg.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
            msg.setBaseSize(QtCore.QSize(650, 300))
            msg.setText(
                "Digitize 3 points to generate the base plane, and then digitize the end point (With the left pedal).")

            msg.setInformativeText("After that, Press the Start/Stop button and move the tip "
                                   "SLOWLY in order to capture data in each plane.")
            msg.exec_()

        def DIPinstructions(self):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Data in plane instructions")
            msg.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
            msg.setBaseSize(QtCore.QSize(650, 300))
            msg.setText(
                "Digitize at least 3 points (With the left pedal) along the plane in which data will be projected.")

            msg.setInformativeText("Digitize Data (With the Right pedal) in the space to project into the plane")
            msg.exec_()

        def MdataLtableSelect(self):
            self.actualtable = self.MdataLtable
            self.SelectedDatainActualTable()

        def MdataRtableSelect(self):
            self.actualtable = self.MdataRtable
            self.SelectedDatainActualTable()

        def SelectedCaptureddatatable(self):
            self.actualtable = self.Captureddatatable
            self.SelectedDatainActualTable()

        def SelectedTwoDdatatable(self):
            self.actualtable = self.TwoDdatatable
            self.SelectedDatainActualTable()

        def SelectedPlaneAngle1Table(self):
            self.actualtable = self.PlaneAngle1Table
            self.SelectedDatainActualTable()

        def SelectedPlaneAngle2Table(self):
            self.actualtable = self.PlaneAngle2Table
            self.SelectedDatainActualTable()

        def SelectedDatainActualTable(self):

            row = self.actualtable.currentRow()
            rows = [idx.row() for idx in self.actualtable.selectionModel().selectedIndexes()]  # Number of rows
            rows = list(set(rows))

            if self.actualtable.rowCount() != 0:

                if rows == [] and row != -1:
                    rows = [row]

                if self.actualtable.rowCount() == 0 or row == -1:
                    rows = []

                if rows != []:
                    if rows[0] == row or rows[-1] == row:
                        rows = rows
                    else:
                        rows = [row]

            if len(rows) > self.actualtable.rowCount():
                rows = [row]

            if rows != []:
                s = ''
                self.selectedData = empty((0, 3), int)
                for r in rows:
                    s = [float(self.actualtable.item(r, 0).text()), float(self.actualtable.item(r, 1).text()),
                         float(self.actualtable.item(r, 2).text())]
                    self.selectedData = vstack((self.selectedData, s))

            # self.updatePlot()
            self.Plot_Selected()

        def Plot_Selected(self):

            self.canvas.plotpointGreen(x=self.selectedData[:, 0],
                                       y=self.selectedData[:, 1],
                                       z=self.selectedData[:, 2],
                                       lbl='Selected data')  # Call green plot

        def Del_Plot_Selected(self):
            self.selectedData = empty((0, 3), int)
            self.updatePlot()
            self.Plot_Selected()

        def On_deleteLeft(self):
            self.MdataLP = empty((0, 3), int)
            self.MdataLtable.clearContents()
            self.MdataLtable.setRowCount(0)
            self.Del_Plot_Selected()

        def On_deleteRight(self):
            self.MdataRP = empty((0, 3), int)
            self.MdataRtable.clearContents()
            self.MdataRtable.setRowCount(0)
            self.Del_Plot_Selected()

        def On_DeleteAutoData(self):
            self.Adata = empty((0, 3), int)
            self.Adatatable.clearContents()
            self.Adatatable.setRowCount(0)
            self.Del_Plot_Selected()

        def On_DeleteDataRadius(self):
            self.Rpoint = empty((0, 3), int)
            self.ERtable.clearContents()
            self.ERtable.setRowCount(0)
            self.Rpoint = empty((0, 3), int)
            self.Centerlbl.setText(str(''))
            self.Radiouslbl.setText(str(''))
            self.NormalVectorlbl.setText(str(''))
            self.Del_Plot_Selected()

        def On_DeleteSP(self):
            self.Ppoint_SP = empty((0, 3), int)
            self.Ppoint_SPR = empty((0, 3), int)
            self.EndPoint_SP = empty((0, 3), int)
            self.ScanPlanesData = empty((0, 3), int)
            self.Normal_SP = empty((0, 3), int)
            self.PointsLbl_SP.setText(str(''))
            self.NormalLbl_SP.setText(str(''))
            self.StopPointLbl.setText(str(''))
            self.Pip_SP = 0
            self.d_toPlane_SP = 0
            self.d_toOrigin_SP = 0
            self.d_OriginToEp_SP = 0
            self.PlanesToScan_O = empty((0, 3), int)
            self.partitions = 0
            self.PlanesToScan = empty((0, 3), int)
            self.StartStopBtn_SP.setText('Start/Stop Scan')
            self.StartStopBtn_SP.setEnabled(False)
            self.ScanPlanesBool = False

            self.ScanPlanesTable.clearContents()
            self.ScanPlanesTable.setRowCount(0)
            self.TabChange()
            self.Del_Plot_Selected()

        def On_DeleteDIP(self):
            self.Planepoint = empty((0, 3), int)
            self.Nu = empty((0, 3), int)
            self.Dinplane = empty((0, 3), int)
            self.TwoDdatatable.clearContents()
            self.TwoDdatatable.setRowCount(0)
            self.Doutplane = empty((0, 3), int)
            self.Captureddatatable.clearContents()
            self.Captureddatatable.setRowCount(0)
            self.NormalLbl.setText(str(''))
            self.PointsLbl.setText(str(''))
            self.TabChange()  # Delete all in plot
            self.Del_Plot_Selected()

        def On_DeleteABP(self):

            self.Normal1_lbl.setText(str(''))
            self.Normal2_lbl.setText(str(''))
            self.AngleBplanes.setText(str(''))
            self.PlaneAngle1Table.clearContents()
            self.PlaneAngle1Table.setRowCount(0)
            self.PlaneAngle2Table.clearContents()
            self.PlaneAngle2Table.setRowCount(0)
            self.PlaneAngle1A = empty((0, 3), int)
            self.PlaneAngle2A = empty((0, 3), int)
            self.Del_Plot_Selected()
            self.TabChange()  # Delete plots

        def keyPressEvent(self, e):  # Allow copy data from QtableView

            if e.modifiers() and QtCore.Qt.ControlModifier:
                selected = self.actualtable.selectedRanges()

                if e.key() == QtCore.Qt.Key_C:  # copy
                    s = ""
                    if selected != []:
                        for r in range(selected[0].topRow(), selected[0].bottomRow() + 1):
                            for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                                try:
                                    s += str(self.actualtable.item(r, c).text()) + " "
                                except AttributeError:
                                    s += "\t"
                            s = s[:-1] + "\n"  # eliminate last '\t'
                        self.clip.setText(s)
                    else:
                        self.clip.setText(s)

            if e.key() == QtCore.Qt.Key_Delete:  # Delete
                self.on_DeleteData()

        def createFolder(self):
            try:
                if not path.exists(self.directory):
                    makedirs(self.directory)
            except OSError:
                print('Error: Creating directory. ', self.directory)

        def on_Exportplot(self):
            self.directory = './Exported data/Individually Exported plot/'
            self.createFolder()

            if path.exists(self.directory):
                pathfolder = str(self.directory + self.tabWidget.tabText(self.tabWidget.currentIndex()) + ' Plot.png')
                if path.exists(pathfolder):
                    date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')  # String with the current date and time
                    pathfolder = str(self.directory + self.tabWidget.tabText(
                        self.tabWidget.currentIndex()) + ' Plot ' + date + '.png')
                    self.canvas.fig.savefig(pathfolder, dpi=300)
                else:
                    self.canvas.fig.savefig(pathfolder, dpi=300)

                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("Figure saved")
                msg.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
                msg.setBaseSize(QtCore.QSize(650, 300))
                msg.setText("Plot correctly saved.")
                msg.setInformativeText(str("Path: " + pathfolder + '.'))

                msg.exec_()

            else:
                print('Error saving data')

        def on_ExportData(self):
            date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')  # String with the current date and time.
            self.directory = str('./Exported data/Actual data/ ' + date + '/')
            self.createFolder()

            if path.exists(self.directory):

                pathfolder = str(self.directory)
                pathfolderimg = pathfolder + ' plot.png'
                self.canvas.fig.savefig(pathfolderimg, dpi=300)

                if self.tabWidget.currentIndex() == 0:  # Take data manually
                    savetxt(pathfolder + ' Right data.csv', self.MdataRP, delimiter=' ', fmt='%s')
                    savetxt(pathfolder + ' Left data.csv', self.MdataLP, delimiter=' ', fmt='%s')

                elif self.tabWidget.currentIndex() == 1:  # Take data automatically.
                    savetxt(pathfolder + ' Automatic Data.csv', self.Adata, delimiter=' ', fmt='%s')

                elif self.tabWidget.currentIndex() == 2:  # Measure length.
                    MeasurelengthD = array([[self.X1, self.Y1, self.Z1], [self.X2, self.Y2, self.Z2]])
                    savetxt(pathfolder + ' Measure length Data.csv', MeasurelengthD, delimiter=' ', fmt='%s')

                elif self.tabWidget.currentIndex() == 3:  # Estimate radius.
                    savetxt(pathfolder + ' Estimate radius Data.csv', self.Rpoint, delimiter=' ', fmt='%s')
                    REstimatedData = [self.center, self.Radius, self.Nv]
                    savetxt(pathfolder + ' Estimate radius Estimated Data.csv', REstimatedData, delimiter=' ', fmt='%s')

                elif self.tabWidget.currentIndex() == 4:  # Scan Planes.
                    savetxt(pathfolder + ' Scan Planes Data.csv', self.ScanPlanesData, delimiter=' ', fmt='%s')

                elif self.tabWidget.currentIndex() == 5:  # Data in plane.
                    savetxt(pathfolder + ' Data in plane.csv', self.Dinplane, delimiter=' ', fmt='%s')
                    savetxt(pathfolder + ' Data out the plane.csv', self.Doutplane, delimiter=' ', fmt='%s')

                elif self.tabWidget.currentIndex() == 6:  # Angle between planes.
                    savetxt(pathfolder + ' Angle between planes Plane1.csv', self.PlaneAngle1A, delimiter=' ', fmt='%s')
                    savetxt(pathfolder + ' Angle between planes Plane2.csv', self.PlaneAngle2A, delimiter=' ', fmt='%s')

                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("Data saved")
                msg.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
                msg.setBaseSize(QtCore.QSize(650, 300))
                msg.setText("Correctly saved.")
                msg.setInformativeText(str("Path: " + pathfolder + '.'))
                msg.exec_()

            else:
                print('Error saving data')

        def on_ExportAllData(self):

            date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')  # String with the current date and time.
            self.directory = str('./Exported data/All data/ ' + date + '/')
            self.createFolder()

            if path.exists(self.directory):

                crrntIndx = self.tabWidget.currentIndex()
                for i in range(0, self.tabWidget.count()):
                    self.tabWidget.setCurrentIndex(i)
                    page = self.tabWidget.tabText(i)
                    iterpath = self.directory + str(page)
                    try:
                        if not path.exists(iterpath):
                            makedirs(iterpath)
                    except OSError:
                        print('Error: Creating directory. ', iterpath)
                        break

                    if path.exists(iterpath):
                        pathfolderimg = iterpath + '/ plot.png'
                        self.canvas.fig.savefig(pathfolderimg, dpi=300)

                    if self.tabWidget.currentIndex() == 0:  # Take data manually
                        savetxt(iterpath + '/ Right data.csv', self.MdataRP, delimiter=' ', fmt='%s')
                        savetxt(iterpath + '/ Left data.csv', self.MdataLP, delimiter=' ', fmt='%s')

                    elif self.tabWidget.currentIndex() == 1:  # Take data automatically.
                        savetxt(iterpath + '/ Automatic Data.csv', self.Adata, delimiter=' ', fmt='%s')

                    elif self.tabWidget.currentIndex() == 2:  # Measure length.
                        MeasurelengthD = array([ [self.X1, self.Y1, self.Z1], [self.X2, self.Y2, self.Z2] ])
                        savetxt(iterpath + '/ Measure length Data.csv', MeasurelengthD, delimiter=' ', fmt='%s')


                    elif self.tabWidget.currentIndex() == 3:  # Estimate radius.
                        savetxt(iterpath + '/ Estimate radius Data.csv', self.Rpoint, delimiter=' ', fmt='%s')
                        REstimatedData = [self.center, self.Radius, self.Nv]
                        savetxt(iterpath + '/ Estimate radius Estimated Data.csv', REstimatedData, delimiter=' ', fmt='%s')

                    elif self.tabWidget.currentIndex() == 4:  # Scan Planes.
                        savetxt(iterpath + '/ Scan Planes Data.csv', self.ScanPlanesData, delimiter=' ', fmt='%s')

                    elif self.tabWidget.currentIndex() == 5:  # Data in plane.
                        savetxt(iterpath + '/ Data in plane.csv', self.Dinplane, delimiter=' ', fmt='%s')
                        savetxt(iterpath + '/ Data out the plane.csv', self.Doutplane, delimiter=' ', fmt='%s')

                    elif self.tabWidget.currentIndex() == 6:  # Angle between planes.
                        savetxt(iterpath + '/ Angle between planes Plane1.csv', self.PlaneAngle1A, delimiter=' ',
                                fmt='%s')
                        savetxt(iterpath + '/ Angle between planes Plane2.csv', self.PlaneAngle2A, delimiter=' ',
                                fmt='%s')

                self.tabWidget.setCurrentIndex(crrntIndx)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle("All data saved")
                msg.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation')))
                msg.setBaseSize(QtCore.QSize(650, 300))
                msg.setText("All data correctly saved.")
                msg.setInformativeText(str("Path: " + self.directory + '.'))
                msg.exec_()
            else:
                print('Error saving data')

        def on_DeleteData(self):
            selected = self.actualtable.selectedRanges()

            self.AllArrays = [self.MdataLP, self.MdataRP, self.Adata, self.Rpoint,
                              self.ScanPlanesData, self.Dinplane, self.Doutplane,
                              self.PlaneAngle1A, self.PlaneAngle2A]

            if selected != []:
                for r in range(selected[0].bottomRow() + 1, selected[0].topRow(), -1):
                    # for c in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                    target = [float(self.actualtable.item(r - 1, 0).text()),
                              float(self.actualtable.item(r - 1, 1).text()),
                              float(self.actualtable.item(r - 1, 2).text())]

                    for index in range(0, len(self.AllArrays)):
                        subArray = self.AllArrays[index]

                        if all(isin(target, subArray)):
                            i, j = where(subArray == target)
                            i = list(i)
                            rowindex = max(set(i), key=i.count)  # find the most repeated value.
                            subArray_i = delete(subArray, rowindex, axis=0)

                            if array_equal(subArray_i, array([])):
                                subArray_i = empty((0, 3), int)
                            self.AllArrays[index] = subArray_i

                            break

                    self.MdataLP = self.AllArrays[0]
                    self.MdataRP = self.AllArrays[1]
                    self.Adata = self.AllArrays[2]
                    self.Rpoint = self.AllArrays[3]
                    self.ScanPlanesData = self.AllArrays[4]
                    # self.Dinplane = self.AllArrays[5]
                    self.Doutplane = self.AllArrays[6]
                    self.PlaneAngle1A = self.AllArrays[7]
                    self.PlaneAngle2A = self.AllArrays[8]

                    self.actualtable.removeRow(r - 1)

                if self.tabWidget.currentIndex() == 5 and linalg.norm(self.Nu) != 0:
                    self.Dinplane = empty((0, 3), int)

                    self.ProjectData()

            self.Del_Plot_Selected()

        def on_EndButton(self):
            self.close()
            self.Doloop = False

        def endcommunication(self):
            self.threadCoordinates.terminate()  # Terminate thread
            # - Flush and clear the port
            TxRx.flush()
            TxRx.write(b'END')
            TxRx.close()
            print('Correct close')

        def closeEvent(self, event):
            self.endcommunication()


    class ThreeDplot(FigureCanvas):  # Class for 3D window
        def __init__(self, parent=None, width=5.45, height=3.65, dpi=100):  # Dimentions by default
            self.fig = plt.figure(figsize=(width, height), dpi=dpi)
            plt.rc('font', size=6)  # Set Fontsize for texts in the plot
            plt.rc('lines', linewidth=0.8)


            FigureCanvas.__init__(self, self.fig)  # creating FigureCanvas
            self.setParent(parent)
            self.axes = self.fig.gca(projection='3d')  # generates 3D Axes object
            self.axes.set_title('Captured points and Stylus')


            self.axes.set_autoscale_on(False_)
            self.axes.set_xlim([-700, 700])
            self.axes.set_ylim([-700, 700])
            self.axes.set_zlim([-300, 900])

            """
            self.axes.w_xaxis.gridlines.set_lw(1.0)
            self.axes.w_yaxis.gridlines.set_lw(1.0)
            self.axes.w_zaxis.gridlines.set_lw(1.0)
            """

            self.initVariablesPlot()

        def initVariablesPlot(self):
            # - Initialize plot objects.
            self.Stylus_plot = None
            self.PointL_plot = None
            self.PointR_plot = None
            self.PointG_plot = None
            self.PointO_plot = None
            self.Vector_plot = None
            self.PlanePlot = None
            self.PlanePlot2 = None

            # - Initialize Plot arrays
            self.pointLArray = zeros(3)
            self.pointLArray_i = zeros(3)
            self.pointRArray = zeros(3)
            self.pointRArray_i = zeros(3)
            self.pointOArray = zeros(3)
            self.pointOArray_i = zeros(3)
            self.pointGArray = zeros(3)
            self.pointGArray_i = zeros(3)
            self.plotVectorArray = zeros(6)
            self.plotVectorArray_i = zeros(6)
            self.plotPlaneArray = zeros(3)
            self.plotPlaneArray_i = zeros(3)
            self.plotPlaneArray2 = zeros(3)
            self.plotPlaneArray_i2 = zeros(3)

        def DeletePlotInCanvas(self, FigName):

            if self.axes.collections != []:

                if FigName in self.axes.collections:
                    idx = self.axes.collections.index(FigName)
                    self.axes.collections.pop(idx)

        def Stylus(self, x, y, z, Nx, Ny, Nz):

            self.DeletePlotInCanvas(self.Stylus_plot)  # Clear the last figure generated of this object

            if mmBtnChecked:  # Adjust plot size according the units.
                self.Stylus_plot = self.axes.quiver(x, y, z, Nx, Ny, Nz, pivot='tip', length=100,
                                                    normalize=True, color='k', label='Stylus')

                self.axes.set_xlim([-700, 700])
                self.axes.set_ylim([-700, 700])
                self.axes.set_zlim([-300, 900])

            else:
                self.Stylus_plot = self.axes.quiver(x, y, z, Nx, Ny, Nz, pivot='tip', length=4,
                                 normalize=True, color='k', label='Stylus')

                self.axes.set_xlim([-28, 28])
                self.axes.set_ylim([-28, 28])
                self.axes.set_zlim([-12, 35])

            self.axes.set_autoscale_on(False_)
            # self.axes2.set_title('Captured points and Stylus', fontsize=20)
            self.axes.set_xlabel('X axis')
            self.axes.set_ylabel('Y axis')
            self.axes.set_zlabel('Z axis')
            self.axes.legend()  # Required to display plot label
            self.draw()

        def plotpointL(self, x, y, z, lbl='Left pedal data'):

            self.pointLArray = array([x, y, z])
            if not array_equal(self.pointLArray, self.pointLArray_i):
                self.DeletePlotInCanvas(self.PointL_plot)  # Clear the last figure generated of this object

                self.PointL_plot = self.axes.scatter(x, y, z, c='b', alpha=0.5,
                                                     marker='.', label=lbl)
                self.axes.legend()  # Required to display plot label
                self.draw()  # Update plot

            self.pointLArray_i = self.pointLArray

        def plotpointR(self, x, y, z, lbl='Right pedal data'):

            self.pointRArray = array([x, y, z])
            if not array_equal(self.pointRArray, self.pointRArray_i):
                self.DeletePlotInCanvas(self.PointR_plot)  # Clear the last figure generated of this object

                self.PointR_plot = self.axes.scatter(x, y, z, c='r', alpha=0.5,
                                                     marker='.', label=lbl)
                self.axes.legend()  # Required to display plot label
                self.draw()  # Update plot

            self.pointRArray_i = self.pointRArray

        def plotpointGreen(self, x, y, z, lbl='Selected Data'):

            self.pointGArray = array([x, y, z])

            if not array_equal(self.pointGArray, self.pointGArray_i):
                self.DeletePlotInCanvas(self.PointG_plot)

                self.PointG_plot = self.axes.scatter(x, y, z, c='darkgreen', alpha=1,
                                                     marker='*', label=lbl)
                self.axes.legend()  # Required to display plot label
                self.draw()  # Update plot

            self.pointGArray_i = self.pointGArray

        def plotpointOlive(self, x, y, z, lbl='Selected Data'):

            self.pointOArray = array([x, y, z])

            if not array_equal(self.pointOArray, self.pointOArray_i):
                self.DeletePlotInCanvas(self.PointO_plot)

                self.PointO_plot = self.axes.scatter(x, y, z, c='olive', alpha=0.5, marker='.', label=lbl)
                self.axes.legend()  # Required to display plot label
                self.draw()  # Update plot

            self.pointOArray_i = self.pointOArray

        def plotVector(self, x, y, z, Nx, Ny, Nz, distance):

            self.plotVectorArray = array([x, y, z, Nx, Ny, Nz])

            if not array_equal(self.plotVectorArray, self.plotVectorArray_i):
                self.DeletePlotInCanvas(self.Vector_plot)

                self.Vector_plot = self.axes.quiver(x, y, z, Nx, Ny, Nz, pivot='tip',
                                                    length=distance, color='g', label='Vector')
                self.axes.legend()  # Required to display plot label
                self.draw()

            self.plotVectorArray_i = self.plotVectorArray

        def plotPlane(self, P, Nu, d, lbl='Plane'):

            self.plotPlaneArray = array(P)

            if not array_equal(self.plotPlaneArray, self.plotPlaneArray_i) and size(P) >= 3:
                self.DeletePlotInCanvas(self.PlanePlot)

                [X, Y, Z] = [0, 0, 0]

                x_max, y_max, z_max = amax(P, axis=0)
                x_min, y_min, z_min = amin(P, axis=0)
                step = 4

                if not type(d).__name__ == 'ndarray':
                    d = asarray([d])  # Convert into an array to iterate.

                for indx, dist in enumerate(d):  # Plot plane for each partition.

                    if Nu[0] != 0:
                        y = linspace(y_min, y_max, step)
                        z = linspace(z_min, z_max, step)
                        Y, Z = meshgrid(y, z)
                        X = (-Nu[1] * Y - Nu[2] * Z - dist) * 1. / Nu[0]

                    elif Nu[1] != 0:
                        x = linspace(x_min, x_max, step)
                        z = linspace(z_min, z_max, step)
                        X, Z = meshgrid(x, z)
                        Y = (-Nu[0] * X - Nu[2] * Z - dist) * 1. / Nu[1]

                    elif Nu[2] != 0:
                        x = linspace(x_min, x_max, step)
                        y = linspace(y_min, y_max, step)
                        X, Y = meshgrid(x, y)
                        Z = (-Nu[0] * X - Nu[1] * Y - dist) * 1. / Nu[2]

                    self.PlanePlot = self.axes.plot_surface(X, Y, Z, color='b', alpha=0.3,
                                                            label=lbl, antialiased=False)
                    self.draw()

            self.plotPlaneArray_i = self.plotPlaneArray

        def plotPlane2(self, P, Nu, d, lbl='Plane 2'):

            self.plotPlaneArray2 = array(P)

            if not array_equal(self.plotPlaneArray2, self.plotPlaneArray_i2) and size(P) >= 3:
                self.DeletePlotInCanvas(self.PlanePlot2)

                [X, Y, Z] = [0, 0, 0]

                x_max, y_max, z_max = amax(P, axis=0)
                x_min, y_min, z_min = amin(P, axis=0)
                step = 4

                if not type(d).__name__ == 'ndarray':
                    d = asarray([d])  # Convert into an array to iterate.

                for indx, dist in enumerate(d):  # Plot plane for each partition.

                    if Nu[0] != 0:
                        y = linspace(y_min, y_max, step)
                        z = linspace(z_min, z_max, step)
                        Y, Z = meshgrid(y, z)
                        X = (-Nu[1] * Y - Nu[2] * Z - dist) * 1. / Nu[0]

                    elif Nu[1] != 0:
                        x = linspace(x_min, x_max, step)
                        z = linspace(z_min, z_max, step)
                        X, Z = meshgrid(x, z)
                        Y = (-Nu[0] * X - Nu[2] * Z - dist) * 1. / Nu[1]

                    elif Nu[2] != 0:
                        x = linspace(x_min, x_max, step)
                        y = linspace(y_min, y_max, step)
                        X, Y = meshgrid(x, y)
                        Z = (-Nu[0] * X - Nu[1] * Y - dist) * 1. / Nu[2]

                    self.PlanePlot2 = self.axes.plot_surface(X, Y, Z, color='r', alpha=0.3,
                                                            label=lbl, antialiased=False)
                    self.draw()

            self.plotPlaneArray_i2 = self.plotPlaneArray2


    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)

        dim = app.desktop().screenGeometry()
        print("The screen resolution is ({} X {}):".format(dim.width(), dim.height()))
        print("logicalDpiX ", app.desktop().logicalDpiX())
        print("physicalDpiX ", app.desktop().physicalDpiX())

        window = MSGUI()
        window.show()
        sys.exit(app.exec_())

except SystemExit:
    print('Window Closed')
