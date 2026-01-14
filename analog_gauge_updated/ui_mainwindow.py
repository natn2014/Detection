# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_filevpDZml.ui'
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
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDateEdit,
    QDialogButtonBox, QFrame, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(777, 599)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_12 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_7 = QVBoxLayout(self.tab)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_Data_Monitor = QGroupBox(self.tab)
        self.groupBox_Data_Monitor.setObjectName(u"groupBox_Data_Monitor")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_Data_Monitor)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.pushButton_Select_Model = QPushButton(self.groupBox_Data_Monitor)
        self.pushButton_Select_Model.setObjectName(u"pushButton_Select_Model")

        self.verticalLayout_6.addWidget(self.pushButton_Select_Model)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_Guage_Video = QLabel(self.groupBox_Data_Monitor)
        self.label_Guage_Video.setObjectName(u"label_Guage_Video")
        self.label_Guage_Video.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_6.addWidget(self.label_Guage_Video)

        self.line_2 = QFrame(self.groupBox_Data_Monitor)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_6.addWidget(self.line_2)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_Past_Records_Graph = QLabel(self.groupBox_Data_Monitor)
        self.label_Past_Records_Graph.setObjectName(u"label_Past_Records_Graph")
        self.label_Past_Records_Graph.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_14.addWidget(self.label_Past_Records_Graph)

        self.line_7 = QFrame(self.groupBox_Data_Monitor)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_14.addWidget(self.line_7)

        self.tableWidget_Gauge_Values = QTableWidget(self.groupBox_Data_Monitor)
        self.tableWidget_Gauge_Values.setObjectName(u"tableWidget_Gauge_Values")

        self.verticalLayout_14.addWidget(self.tableWidget_Gauge_Values)


        self.horizontalLayout_6.addLayout(self.verticalLayout_14)


        self.verticalLayout_6.addLayout(self.horizontalLayout_6)

        self.line = QFrame(self.groupBox_Data_Monitor)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_6.addWidget(self.line)


        self.verticalLayout_8.addLayout(self.verticalLayout_6)


        self.verticalLayout_5.addWidget(self.groupBox_Data_Monitor)


        self.verticalLayout_7.addLayout(self.verticalLayout_5)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_2 = QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_Previous = QGroupBox(self.tab_2)
        self.groupBox_Previous.setObjectName(u"groupBox_Previous")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_Previous)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(5, 5, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_Start = QLabel(self.groupBox_Previous)
        self.label_Start.setObjectName(u"label_Start")
        self.label_Start.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_Start.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_Start)

        self.dateEdit_Start = QDateEdit(self.groupBox_Previous)
        self.dateEdit_Start.setObjectName(u"dateEdit_Start")
        self.dateEdit_Start.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit_Start)

        self.line_4 = QFrame(self.groupBox_Previous)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_4)

        self.label_End = QLabel(self.groupBox_Previous)
        self.label_End.setObjectName(u"label_End")
        self.label_End.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_End)

        self.dateEdit_End = QDateEdit(self.groupBox_Previous)
        self.dateEdit_End.setObjectName(u"dateEdit_End")
        self.dateEdit_End.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateEdit_End)

        self.line_6 = QFrame(self.groupBox_Previous)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.VLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_6)

        self.label = QLabel(self.groupBox_Previous)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.comboBox = QComboBox(self.groupBox_Previous)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_2.addWidget(self.comboBox)

        self.line_5 = QFrame(self.groupBox_Previous)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.VLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_5)

        self.pushButton_Show = QPushButton(self.groupBox_Previous)
        self.pushButton_Show.setObjectName(u"pushButton_Show")

        self.horizontalLayout_2.addWidget(self.pushButton_Show)

        self.pushButton_Export_CSV = QPushButton(self.groupBox_Previous)
        self.pushButton_Export_CSV.setObjectName(u"pushButton_Export_CSV")

        self.horizontalLayout_2.addWidget(self.pushButton_Export_CSV)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)

        self.line_3 = QFrame(self.groupBox_Previous)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_9.addWidget(self.line_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_Selected_Graph = QLabel(self.groupBox_Previous)
        self.label_Selected_Graph.setObjectName(u"label_Selected_Graph")
        self.label_Selected_Graph.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_Selected_Graph)


        self.verticalLayout_9.addLayout(self.verticalLayout_4)


        self.verticalLayout_3.addWidget(self.groupBox_Previous)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_Setting_Gauge = QGroupBox(self.tab_3)
        self.groupBox_Setting_Gauge.setObjectName(u"groupBox_Setting_Gauge")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_Setting_Gauge)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.tableWidget_Setting_Gauge = QTableWidget(self.groupBox_Setting_Gauge)
        if (self.tableWidget_Setting_Gauge.columnCount() < 2):
            self.tableWidget_Setting_Gauge.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setBackground(QColor(235, 235, 117));
        self.tableWidget_Setting_Gauge.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setBackground(QColor(158, 217, 226));
        self.tableWidget_Setting_Gauge.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.tableWidget_Setting_Gauge.rowCount() < 2):
            self.tableWidget_Setting_Gauge.setRowCount(2)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_Setting_Gauge.setVerticalHeaderItem(0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_Setting_Gauge.setVerticalHeaderItem(1, __qtablewidgetitem3)
        self.tableWidget_Setting_Gauge.setObjectName(u"tableWidget_Setting_Gauge")

        self.verticalLayout_11.addWidget(self.tableWidget_Setting_Gauge)

        self.buttonBox_Setting_Gauge_save_cancel = QDialogButtonBox(self.groupBox_Setting_Gauge)
        self.buttonBox_Setting_Gauge_save_cancel.setObjectName(u"buttonBox_Setting_Gauge_save_cancel")
        self.buttonBox_Setting_Gauge_save_cancel.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout_11.addWidget(self.buttonBox_Setting_Gauge_save_cancel)


        self.verticalLayout.addWidget(self.groupBox_Setting_Gauge)

        self.groupBox_Setting_Alarm = QGroupBox(self.tab_3)
        self.groupBox_Setting_Alarm.setObjectName(u"groupBox_Setting_Alarm")
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_Setting_Alarm)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.tableWidget_Setting_Alarm = QTableWidget(self.groupBox_Setting_Alarm)
        if (self.tableWidget_Setting_Alarm.columnCount() < 4):
            self.tableWidget_Setting_Alarm.setColumnCount(4)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setBackground(QColor(235, 235, 117));
        self.tableWidget_Setting_Alarm.setHorizontalHeaderItem(0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setBackground(QColor(158, 217, 226));
        self.tableWidget_Setting_Alarm.setHorizontalHeaderItem(1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setBackground(QColor(208, 203, 45));
        self.tableWidget_Setting_Alarm.setHorizontalHeaderItem(2, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setBackground(QColor(36, 143, 189));
        self.tableWidget_Setting_Alarm.setHorizontalHeaderItem(3, __qtablewidgetitem7)
        if (self.tableWidget_Setting_Alarm.rowCount() < 2):
            self.tableWidget_Setting_Alarm.setRowCount(2)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_Setting_Alarm.setVerticalHeaderItem(0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_Setting_Alarm.setVerticalHeaderItem(1, __qtablewidgetitem9)
        self.tableWidget_Setting_Alarm.setObjectName(u"tableWidget_Setting_Alarm")
        self.tableWidget_Setting_Alarm.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_Setting_Alarm.horizontalHeader().setMinimumSectionSize(50)
        self.tableWidget_Setting_Alarm.horizontalHeader().setDefaultSectionSize(160)
        self.tableWidget_Setting_Alarm.horizontalHeader().setProperty(u"showSortIndicator", False)
        self.tableWidget_Setting_Alarm.horizontalHeader().setStretchLastSection(False)
        self.tableWidget_Setting_Alarm.verticalHeader().setProperty(u"showSortIndicator", False)
        self.tableWidget_Setting_Alarm.verticalHeader().setStretchLastSection(False)

        self.verticalLayout_10.addWidget(self.tableWidget_Setting_Alarm)

        self.buttonBox_Setting_Alarm_save_cancel = QDialogButtonBox(self.groupBox_Setting_Alarm)
        self.buttonBox_Setting_Alarm_save_cancel.setObjectName(u"buttonBox_Setting_Alarm_save_cancel")
        self.buttonBox_Setting_Alarm_save_cancel.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout_10.addWidget(self.buttonBox_Setting_Alarm_save_cancel)


        self.verticalLayout.addWidget(self.groupBox_Setting_Alarm)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tab_4.setMaximumSize(QSize(757, 539))
        self.verticalLayout_15 = QVBoxLayout(self.tab_4)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox_Setting_Gauge_2 = QGroupBox(self.tab_4)
        self.groupBox_Setting_Gauge_2.setObjectName(u"groupBox_Setting_Gauge_2")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_Setting_Gauge_2)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.tableWidget_Setting_Gauge_2 = QTableWidget(self.groupBox_Setting_Gauge_2)
        if (self.tableWidget_Setting_Gauge_2.columnCount() < 3):
            self.tableWidget_Setting_Gauge_2.setColumnCount(3)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setBackground(QColor(171, 225, 168));
        self.tableWidget_Setting_Gauge_2.setHorizontalHeaderItem(0, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setBackground(QColor(235, 235, 117));
        self.tableWidget_Setting_Gauge_2.setHorizontalHeaderItem(1, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setBackground(QColor(158, 217, 226));
        self.tableWidget_Setting_Gauge_2.setHorizontalHeaderItem(2, __qtablewidgetitem12)
        if (self.tableWidget_Setting_Gauge_2.rowCount() < 2):
            self.tableWidget_Setting_Gauge_2.setRowCount(2)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_Setting_Gauge_2.setVerticalHeaderItem(0, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_Setting_Gauge_2.setVerticalHeaderItem(1, __qtablewidgetitem14)
        self.tableWidget_Setting_Gauge_2.setObjectName(u"tableWidget_Setting_Gauge_2")
        self.tableWidget_Setting_Gauge_2.horizontalHeader().setMinimumSectionSize(100)
        self.tableWidget_Setting_Gauge_2.horizontalHeader().setDefaultSectionSize(150)

        self.verticalLayout_13.addWidget(self.tableWidget_Setting_Gauge_2)

        self.buttonBox_Setting_Gauge_save_cancel_2 = QDialogButtonBox(self.groupBox_Setting_Gauge_2)
        self.buttonBox_Setting_Gauge_save_cancel_2.setObjectName(u"buttonBox_Setting_Gauge_save_cancel_2")
        self.buttonBox_Setting_Gauge_save_cancel_2.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout_13.addWidget(self.buttonBox_Setting_Gauge_save_cancel_2)


        self.horizontalLayout.addWidget(self.groupBox_Setting_Gauge_2)


        self.verticalLayout_15.addLayout(self.horizontalLayout)

        self.tabWidget.addTab(self.tab_4, "")

        self.verticalLayout_12.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_Data_Monitor.setTitle(QCoreApplication.translate("MainWindow", u"Data Monitor", None))
        self.pushButton_Select_Model.setText(QCoreApplication.translate("MainWindow", u"Select : Model", None))
        self.label_Guage_Video.setText(QCoreApplication.translate("MainWindow", u"Gauge Video Label", None))
        self.label_Past_Records_Graph.setText(QCoreApplication.translate("MainWindow", u"Past 300 Records GraphLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Monitor", None))
        self.groupBox_Previous.setTitle(QCoreApplication.translate("MainWindow", u"Previous Data", None))
        self.label_Start.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.label_End.setText(QCoreApplication.translate("MainWindow", u"End", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.pushButton_Show.setText(QCoreApplication.translate("MainWindow", u"Show", None))
        self.pushButton_Export_CSV.setText(QCoreApplication.translate("MainWindow", u"Export CSV", None))
        self.label_Selected_Graph.setText(QCoreApplication.translate("MainWindow", u"GraphLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Record", None))
        self.groupBox_Setting_Gauge.setTitle(QCoreApplication.translate("MainWindow", u"Setting Gauge", None))
        ___qtablewidgetitem = self.tableWidget_Setting_Gauge.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Gauge (%)", None));
        ___qtablewidgetitem1 = self.tableWidget_Setting_Gauge.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Gauge (MPa)", None));
        ___qtablewidgetitem2 = self.tableWidget_Setting_Gauge.verticalHeaderItem(0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Max", None));
        ___qtablewidgetitem3 = self.tableWidget_Setting_Gauge.verticalHeaderItem(1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Min", None));
        self.groupBox_Setting_Alarm.setTitle(QCoreApplication.translate("MainWindow", u"Setting Alarm", None))
        ___qtablewidgetitem4 = self.tableWidget_Setting_Alarm.horizontalHeaderItem(0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Alarm SV (%)", None));
        ___qtablewidgetitem5 = self.tableWidget_Setting_Alarm.horizontalHeaderItem(1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Alarm SV (MPa)", None));
        ___qtablewidgetitem6 = self.tableWidget_Setting_Alarm.horizontalHeaderItem(2)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Gauge PV (%)", None));
        ___qtablewidgetitem7 = self.tableWidget_Setting_Alarm.horizontalHeaderItem(3)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Gauge PV (MPa)", None));
        ___qtablewidgetitem8 = self.tableWidget_Setting_Alarm.verticalHeaderItem(0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Max", None));
        ___qtablewidgetitem9 = self.tableWidget_Setting_Alarm.verticalHeaderItem(1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"Min", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Setting", None))
        self.groupBox_Setting_Gauge_2.setTitle(QCoreApplication.translate("MainWindow", u"Setting Gauge", None))
        ___qtablewidgetitem10 = self.tableWidget_Setting_Gauge_2.horizontalHeaderItem(0)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"Model", None));
        ___qtablewidgetitem11 = self.tableWidget_Setting_Gauge_2.horizontalHeaderItem(1)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"Gauge (%)", None));
        ___qtablewidgetitem12 = self.tableWidget_Setting_Gauge_2.horizontalHeaderItem(2)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"Gauge (MPa)", None));
        ___qtablewidgetitem13 = self.tableWidget_Setting_Gauge_2.verticalHeaderItem(0)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"Min", None));
        ___qtablewidgetitem14 = self.tableWidget_Setting_Gauge_2.verticalHeaderItem(1)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"Max", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Info", None))
    # retranslateUi

