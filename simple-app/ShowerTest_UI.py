# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ShowerTest_UIeFeMmU.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,QIcon,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(796, 592)
        # Add icon to the application window
        icon = QIcon()
        icon.addFile(u"AGC_Logo.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_2 = QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_CAM1 = QPushButton(self.tab)
        self.pushButton_CAM1.setObjectName(u"pushButton_CAM1")

        self.gridLayout.addWidget(self.pushButton_CAM1, 0, 0, 1, 1)

        self.pushButton_CAM3 = QPushButton(self.tab)
        self.pushButton_CAM3.setObjectName(u"pushButton_CAM3")

        self.gridLayout.addWidget(self.pushButton_CAM3, 3, 0, 1, 1)

        self.groupBox_CAM1 = QGroupBox(self.tab)
        self.groupBox_CAM1.setObjectName(u"groupBox_CAM1")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_CAM1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_CAM1_VideoLabel = QLabel(self.groupBox_CAM1)
        self.label_CAM1_VideoLabel.setObjectName(u"label_CAM1_VideoLabel")
        self.label_CAM1_VideoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_CAM1_VideoLabel)

        self.verticalLayout_3.addLayout(self.verticalLayout_2)


        self.gridLayout.addWidget(self.groupBox_CAM1, 1, 0, 1, 1)

        self.groupBox_CAM3 = QGroupBox(self.tab)
        self.groupBox_CAM3.setObjectName(u"groupBox_CAM3")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_CAM3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_CAM3_VideoLabel = QLabel(self.groupBox_CAM3)
        self.label_CAM3_VideoLabel.setObjectName(u"label_CAM3_VideoLabel")
        self.label_CAM3_VideoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.label_CAM3_VideoLabel)


        self.verticalLayout_7.addLayout(self.verticalLayout_6)


        self.gridLayout.addWidget(self.groupBox_CAM3, 2, 0, 1, 1)

        self.pushButton_CAM2 = QPushButton(self.tab)
        self.pushButton_CAM2.setObjectName(u"pushButton_CAM2")

        self.gridLayout.addWidget(self.pushButton_CAM2, 0, 2, 1, 1)

        self.groupBox_CAM4 = QGroupBox(self.tab)
        self.groupBox_CAM4.setObjectName(u"groupBox_CAM4")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_CAM4)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_CAM4_VideoLabel = QLabel(self.groupBox_CAM4)
        self.label_CAM4_VideoLabel.setObjectName(u"label_CAM4_VideoLabel")
        self.label_CAM4_VideoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_CAM4_VideoLabel)


        self.verticalLayout_9.addLayout(self.verticalLayout_8)


        self.gridLayout.addWidget(self.groupBox_CAM4, 2, 2, 1, 1)

        self.groupBox_CAM2 = QGroupBox(self.tab)
        self.groupBox_CAM2.setObjectName(u"groupBox_CAM2")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_CAM2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_CAM2_VideoLabel = QLabel(self.groupBox_CAM2)
        self.label_CAM2_VideoLabel.setObjectName(u"label_CAM2_VideoLabel")
        self.label_CAM2_VideoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_CAM2_VideoLabel)


        self.verticalLayout_5.addLayout(self.verticalLayout_4)


        self.gridLayout.addWidget(self.groupBox_CAM2, 1, 2, 1, 1)

        self.pushButton_CAM4 = QPushButton(self.tab)
        self.pushButton_CAM4.setObjectName(u"pushButton_CAM4")

        self.gridLayout.addWidget(self.pushButton_CAM4, 3, 2, 1, 1)

        self.line = QFrame(self.tab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 1, 1, 1, 1)

        self.line_2 = QFrame(self.tab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 2, 1, 1, 1)


        self.verticalLayout_11.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_Logo = QLabel(self.tab)
        self.label_Logo.setObjectName(u"label_Logo")

        self.horizontalLayout.addWidget(self.label_Logo)

        self.buttonBox_Ok_Retry_Cancel = QDialogButtonBox(self.tab)
        self.buttonBox_Ok_Retry_Cancel.setObjectName(u"buttonBox_Ok_Retry_Cancel")
        self.buttonBox_Ok_Retry_Cancel.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Retry)

        self.horizontalLayout.addWidget(self.buttonBox_Ok_Retry_Cancel)


        self.verticalLayout_11.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_11)

        self.tabWidget.addTab(self.tab, "")
        self.tab_setting = QWidget()
        self.tab_setting.setObjectName(u"tab_setting")
        self.horizontalLayout_5 = QHBoxLayout(self.tab_setting)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.groupBox_Camera = QGroupBox(self.tab_setting)
        self.groupBox_Camera.setObjectName(u"groupBox_Camera")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_Camera)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableWidget_TableCamera = QTableWidget(self.groupBox_Camera)
        if (self.tableWidget_TableCamera.columnCount() < 1):
            self.tableWidget_TableCamera.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_TableCamera.setHorizontalHeaderItem(0, __qtablewidgetitem)
        if (self.tableWidget_TableCamera.rowCount() < 4):
            self.tableWidget_TableCamera.setRowCount(4)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_TableCamera.setVerticalHeaderItem(0, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_TableCamera.setVerticalHeaderItem(1, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_TableCamera.setVerticalHeaderItem(2, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_TableCamera.setVerticalHeaderItem(3, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_TableCamera.setItem(0, 0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_TableCamera.setItem(1, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_TableCamera.setItem(2, 0, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_TableCamera.setItem(3, 0, __qtablewidgetitem8)
        self.tableWidget_TableCamera.setObjectName(u"tableWidget_TableCamera")
        self.tableWidget_TableCamera.horizontalHeader().setDefaultSectionSize(150)
        self.tableWidget_TableCamera.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.tableWidget_TableCamera)

        self.buttonBox_Save_cancel_Camera_Input_Device = QDialogButtonBox(self.groupBox_Camera)
        self.buttonBox_Save_cancel_Camera_Input_Device.setObjectName(u"buttonBox_Save_cancel_Camera_Input_Device")
        self.buttonBox_Save_cancel_Camera_Input_Device.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout.addWidget(self.buttonBox_Save_cancel_Camera_Input_Device)


        self.verticalLayout_10.addLayout(self.verticalLayout)


        self.horizontalLayout_5.addWidget(self.groupBox_Camera)

        self.groupBox_2 = QGroupBox(self.tab_setting)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.tableWidget_ProgramAlgorithm = QTableWidget(self.groupBox_2)
        if (self.tableWidget_ProgramAlgorithm.columnCount() < 1):
            self.tableWidget_ProgramAlgorithm.setColumnCount(1)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        if (self.tableWidget_ProgramAlgorithm.rowCount() < 11):
            self.tableWidget_ProgramAlgorithm.setRowCount(11)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(0, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(1, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(2, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(3, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(4, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(5, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(6, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(7, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(8, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(9, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setVerticalHeaderItem(10, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setItem(0, 0, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setItem(1, 0, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setItem(3, 0, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setItem(5, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.tableWidget_ProgramAlgorithm.setItem(6, 0, __qtablewidgetitem25)
        self.tableWidget_ProgramAlgorithm.setObjectName(u"tableWidget_ProgramAlgorithm")
        self.tableWidget_ProgramAlgorithm.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget_ProgramAlgorithm.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_12.addWidget(self.tableWidget_ProgramAlgorithm)

        self.buttonBox_Save_cancel_Program = QDialogButtonBox(self.groupBox_2)
        self.buttonBox_Save_cancel_Program.setObjectName(u"buttonBox_Save_cancel_Program")
        self.buttonBox_Save_cancel_Program.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout_12.addWidget(self.buttonBox_Save_cancel_Program)


        self.verticalLayout_13.addLayout(self.verticalLayout_12)


        self.horizontalLayout_5.addWidget(self.groupBox_2)

        self.tabWidget.addTab(self.tab_setting, "")

        self.horizontalLayout_4.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 796, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Leakage Inspection x 4 camera", None))
        self.pushButton_CAM1.setText(QCoreApplication.translate("MainWindow", u"CAM1 Status", None))
        self.pushButton_CAM3.setText(QCoreApplication.translate("MainWindow", u"CAM3 Status", None))
        self.groupBox_CAM1.setTitle(QCoreApplication.translate("MainWindow", u"CAM1", None))
        self.label_CAM1_VideoLabel.setText(QCoreApplication.translate("MainWindow", u"CAM1 Video Label", None))
        self.groupBox_CAM3.setTitle(QCoreApplication.translate("MainWindow", u"CAM3", None))
        self.label_CAM3_VideoLabel.setText(QCoreApplication.translate("MainWindow", u"CAM3 Video Label", None))
        self.pushButton_CAM2.setText(QCoreApplication.translate("MainWindow", u"CAM2 Status", None))
        self.groupBox_CAM4.setTitle(QCoreApplication.translate("MainWindow", u"CAM4", None))
        self.label_CAM4_VideoLabel.setText(QCoreApplication.translate("MainWindow", u"CAM4 Video Label", None))
        self.groupBox_CAM2.setTitle(QCoreApplication.translate("MainWindow", u"CAM2", None))
        self.label_CAM2_VideoLabel.setText(QCoreApplication.translate("MainWindow", u"CAM2 Video Label", None))
        self.pushButton_CAM4.setText(QCoreApplication.translate("MainWindow", u"CAM4 Status", None))
        self.label_Logo.setText(QCoreApplication.translate("MainWindow", u"[Leakage Inspection] AGC Automotive Thailand", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Monitor", None))
        self.groupBox_Camera.setTitle(QCoreApplication.translate("MainWindow", u"Camera", None))
        ___qtablewidgetitem = self.tableWidget_TableCamera.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Camera Input Device", None));
        ___qtablewidgetitem1 = self.tableWidget_TableCamera.verticalHeaderItem(0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Camera1 [LH/TOP]", None));
        ___qtablewidgetitem2 = self.tableWidget_TableCamera.verticalHeaderItem(1)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Camera2 [LH/BTM]", None));
        ___qtablewidgetitem3 = self.tableWidget_TableCamera.verticalHeaderItem(2)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Camera3 [RH/TOP]", None));
        ___qtablewidgetitem4 = self.tableWidget_TableCamera.verticalHeaderItem(3)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Camera4 [RH/BTM]", None));

        __sortingEnabled = self.tableWidget_TableCamera.isSortingEnabled()
        self.tableWidget_TableCamera.setSortingEnabled(False)
        ___qtablewidgetitem5 = self.tableWidget_TableCamera.item(0, 0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"0", None));
        ___qtablewidgetitem6 = self.tableWidget_TableCamera.item(1, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"1", None));
        ___qtablewidgetitem7 = self.tableWidget_TableCamera.item(2, 0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"2", None));
        ___qtablewidgetitem8 = self.tableWidget_TableCamera.item(3, 0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"3", None));
        self.tableWidget_TableCamera.setSortingEnabled(__sortingEnabled)

        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Program Algorithm", None))
        ___qtablewidgetitem9 = self.tableWidget_ProgramAlgorithm.horizontalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"Parameter", None));
        ___qtablewidgetitem10 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(0)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"Model Path (.pt)", None));
        ___qtablewidgetitem11 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(1)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"Cut-Off point (%)", None));
        ___qtablewidgetitem12 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(2)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"OK-Class", None));
        ___qtablewidgetitem13 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(3)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"OK-Output Pin", None));
        ___qtablewidgetitem14 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(4)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"NG-Class", None));
        ___qtablewidgetitem15 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(5)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"NG-Output Pin", None));
        ___qtablewidgetitem16 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(6)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"Trigger-Input Pin", None));
        ___qtablewidgetitem17 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(7)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"Record Image (Path)", None));
        ___qtablewidgetitem18 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(8)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"Record Image(Use/No)", None));
        ___qtablewidgetitem19 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(9)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"Sampling Image (Path)", None));
        ___qtablewidgetitem20 = self.tableWidget_ProgramAlgorithm.verticalHeaderItem(10)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"Sampling Image (Use/No)", None));

        __sortingEnabled1 = self.tableWidget_ProgramAlgorithm.isSortingEnabled()
        self.tableWidget_ProgramAlgorithm.setSortingEnabled(False)
        ___qtablewidgetitem21 = self.tableWidget_ProgramAlgorithm.item(3, 0)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"4", None));
        ___qtablewidgetitem22 = self.tableWidget_ProgramAlgorithm.item(5, 0)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"5", None));
        ___qtablewidgetitem23 = self.tableWidget_ProgramAlgorithm.item(6, 0)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"2", None));
        self.tableWidget_ProgramAlgorithm.setSortingEnabled(__sortingEnabled1)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_setting), QCoreApplication.translate("MainWindow", u"Setting", None))
    # retranslateUi

