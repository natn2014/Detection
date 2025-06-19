# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GUI_Label_Split_Train2TmzniW.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractSpinBox, QApplication, QDialogButtonBox,
    QDoubleSpinBox, QFrame, QGroupBox, QHeaderView,
    QLabel, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 721)
        MainWindow.setTabShape(QTabWidget.TabShape.Triangular)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 0, 1261, 661))
        self.tab_file = QWidget()
        self.tab_file.setObjectName(u"tab_file")
        self.groupBox_3 = QGroupBox(self.tab_file)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(50, 80, 981, 61))
        self.buttonBox_2 = QDialogButtonBox(self.groupBox_3)
        self.buttonBox_2.setObjectName(u"buttonBox_2")
        self.buttonBox_2.setGeometry(QRect(810, 20, 156, 31))
        self.buttonBox_2.setStandardButtons(QDialogButtonBox.StandardButton.Discard|QDialogButtonBox.StandardButton.Open)
        self.textEdit_2 = QTextEdit(self.groupBox_3)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(10, 20, 791, 31))
        self.groupBox_4 = QGroupBox(self.tab_file)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(50, 150, 1171, 321))
        self.tableWidget_2 = QTableWidget(self.groupBox_4)
        if (self.tableWidget_2.columnCount() < 5):
            self.tableWidget_2.setColumnCount(5)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.VideoDisplay))
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setIcon(icon);
        self.tableWidget_2.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setGeometry(QRect(20, 50, 711, 261))
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(139)
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)
        self.label = QLabel(self.groupBox_4)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(314, 22, 49, 21))
        self.doubleSpinBox_Validate = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_Validate.setObjectName(u"doubleSpinBox_Validate")
        self.doubleSpinBox_Validate.setGeometry(QRect(484, 20, 88, 23))
        self.doubleSpinBox_Validate.setDecimals(1)
        self.doubleSpinBox_Validate.setValue(25.000000000000000)
        self.label_2 = QLabel(self.groupBox_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(454, 22, 49, 21))
        self.doubleSpinBox_Test = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_Test.setObjectName(u"doubleSpinBox_Test")
        self.doubleSpinBox_Test.setGeometry(QRect(620, 20, 88, 23))
        self.doubleSpinBox_Test.setDecimals(1)
        self.doubleSpinBox_Test.setValue(5.000000000000000)
        self.label_3 = QLabel(self.groupBox_4)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(584, 22, 49, 21))
        self.doubleSpinBox_Train = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_Train.setObjectName(u"doubleSpinBox_Train")
        self.doubleSpinBox_Train.setGeometry(QRect(354, 20, 88, 23))
        self.doubleSpinBox_Train.setDecimals(1)
        self.doubleSpinBox_Train.setStepType(QAbstractSpinBox.StepType.DefaultStepType)
        self.doubleSpinBox_Train.setValue(70.000000000000000)
        self.buttonBox_3 = QDialogButtonBox(self.groupBox_4)
        self.buttonBox_3.setObjectName(u"buttonBox_3")
        self.buttonBox_3.setGeometry(QRect(1000, 280, 156, 31))
        self.buttonBox_3.setStandardButtons(QDialogButtonBox.StandardButton.Reset|QDialogButtonBox.StandardButton.Save)
        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(915, 284, 81, 20))
        self.label_4.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.frame_data_split_ratio = QFrame(self.groupBox_4)
        self.frame_data_split_ratio.setObjectName(u"frame_data_split_ratio")
        self.frame_data_split_ratio.setGeometry(QRect(750, 20, 411, 261))
        self.frame_data_split_ratio.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_data_split_ratio.setFrameShadow(QFrame.Shadow.Raised)
        self.line = QFrame(self.groupBox_4)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(730, 20, 20, 291))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.groupBox = QGroupBox(self.tab_file)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(50, 10, 981, 61))
        self.buttonBox = QDialogButtonBox(self.groupBox)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(810, 20, 156, 31))
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Open)
        self.textEdit = QTextEdit(self.groupBox)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(10, 20, 791, 31))
        self.frame_agc_logo = QFrame(self.tab_file)
        self.frame_agc_logo.setObjectName(u"frame_agc_logo")
        self.frame_agc_logo.setGeometry(QRect(1055, 20, 161, 121))
        self.frame_agc_logo.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_agc_logo.setFrameShadow(QFrame.Shadow.Raised)
        self.tabWidget.addTab(self.tab_file, "")
        self.tab_train = QWidget()
        self.tab_train.setObjectName(u"tab_train")
        self.groupBox_5 = QGroupBox(self.tab_train)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(10, 0, 621, 621))
        self.tableWidget_3 = QTableWidget(self.groupBox_5)
        if (self.tableWidget_3.columnCount() < 1):
            self.tableWidget_3.setColumnCount(1)
        font = QFont()
        font.setBold(True)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setFont(font);
        self.tableWidget_3.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        if (self.tableWidget_3.rowCount() < 17):
            self.tableWidget_3.setRowCount(17)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(3, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(4, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(5, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(6, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(7, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(8, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(9, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(10, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(11, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(12, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(13, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(14, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(15, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.tableWidget_3.setVerticalHeaderItem(16, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.tableWidget_3.setItem(0, 0, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.tableWidget_3.setItem(2, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setCheckState(Qt.Checked);
        self.tableWidget_3.setItem(7, 0, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        __qtablewidgetitem26.setCheckState(Qt.Unchecked);
        self.tableWidget_3.setItem(9, 0, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        __qtablewidgetitem27.setCheckState(Qt.Checked);
        self.tableWidget_3.setItem(12, 0, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        __qtablewidgetitem28.setCheckState(Qt.Checked);
        self.tableWidget_3.setItem(14, 0, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        __qtablewidgetitem29.setCheckState(Qt.Checked);
        self.tableWidget_3.setItem(16, 0, __qtablewidgetitem29)
        self.tableWidget_3.setObjectName(u"tableWidget_3")
        self.tableWidget_3.setGeometry(QRect(20, 30, 580, 511))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(120)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget_3.sizePolicy().hasHeightForWidth())
        self.tableWidget_3.setSizePolicy(sizePolicy)
        self.tableWidget_3.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_3.horizontalHeader().setDefaultSectionSize(290)
        self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_3.verticalHeader().setVisible(True)
        self.groupBox_7 = QGroupBox(self.groupBox_5)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setGeometry(QRect(20, 549, 191, 61))
        self.buttonBox_4 = QDialogButtonBox(self.groupBox_7)
        self.buttonBox_4.setObjectName(u"buttonBox_4")
        self.buttonBox_4.setGeometry(QRect(15, 20, 161, 31))
        self.buttonBox_4.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Reset)
        self.groupBox_8 = QGroupBox(self.groupBox_5)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.groupBox_8.setGeometry(QRect(230, 550, 371, 61))
        self.pushButton = QPushButton(self.groupBox_8)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 22, 75, 24))
        self.pushButton_2 = QPushButton(self.groupBox_8)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(100, 22, 75, 24))
        self.pushButton_3 = QPushButton(self.groupBox_8)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(190, 22, 75, 24))
        self.pushButton_4 = QPushButton(self.groupBox_8)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(280, 22, 75, 24))
        self.groupBox_6 = QGroupBox(self.tab_train)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(640, 0, 601, 621))
        self.frame_terminal = QFrame(self.groupBox_6)
        self.frame_terminal.setObjectName(u"frame_terminal")
        self.frame_terminal.setGeometry(QRect(10, 30, 581, 581))
        self.frame_terminal.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_terminal.setFrameShadow(QFrame.Shadow.Raised)
        self.tabWidget.addTab(self.tab_train, "")
        self.tab_graph = QWidget()
        self.tab_graph.setObjectName(u"tab_graph")
        self.tabWidget.addTab(self.tab_graph, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Select Outout Folder", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Select Output Location</span></p></body></html>", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Dataset Split", None))
        ___qtablewidgetitem = self.tableWidget_2.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Classes", None));
        ___qtablewidgetitem1 = self.tableWidget_2.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Total", None));
        ___qtablewidgetitem2 = self.tableWidget_2.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Train", None));
        ___qtablewidgetitem3 = self.tableWidget_2.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Validate", None));
        ___qtablewidgetitem4 = self.tableWidget_2.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Test", None));
        self.label.setText(QCoreApplication.translate("MainWindow", u"Train =", None))
        self.doubleSpinBox_Validate.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Val =", None))
        self.doubleSpinBox_Test.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Test =", None))
        self.doubleSpinBox_Train.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"File .yaml", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Browse Folder", None))
        self.textEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Select Labeled Folder</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_file), QCoreApplication.translate("MainWindow", u"File", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Model Config", None))
        ___qtablewidgetitem5 = self.tableWidget_3.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Value", None));
        ___qtablewidgetitem6 = self.tableWidget_3.verticalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"data", None));
        ___qtablewidgetitem7 = self.tableWidget_3.verticalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"pre-train", None));
        ___qtablewidgetitem8 = self.tableWidget_3.verticalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"epochs", None));
        ___qtablewidgetitem9 = self.tableWidget_3.verticalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"time", None));
        ___qtablewidgetitem10 = self.tableWidget_3.verticalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"patience", None));
        ___qtablewidgetitem11 = self.tableWidget_3.verticalHeaderItem(5)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"batch", None));
        ___qtablewidgetitem12 = self.tableWidget_3.verticalHeaderItem(6)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"imgsz", None));
        ___qtablewidgetitem13 = self.tableWidget_3.verticalHeaderItem(7)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"save", None));
        ___qtablewidgetitem14 = self.tableWidget_3.verticalHeaderItem(8)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"save_period", None));
        ___qtablewidgetitem15 = self.tableWidget_3.verticalHeaderItem(9)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"cache", None));
        ___qtablewidgetitem16 = self.tableWidget_3.verticalHeaderItem(10)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"device", None));
        ___qtablewidgetitem17 = self.tableWidget_3.verticalHeaderItem(11)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"project", None));
        ___qtablewidgetitem18 = self.tableWidget_3.verticalHeaderItem(12)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"val", None));
        ___qtablewidgetitem19 = self.tableWidget_3.verticalHeaderItem(13)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"optimizer", None));
        ___qtablewidgetitem20 = self.tableWidget_3.verticalHeaderItem(14)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"verbose", None));
        ___qtablewidgetitem21 = self.tableWidget_3.verticalHeaderItem(15)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"seed", None));
        ___qtablewidgetitem22 = self.tableWidget_3.verticalHeaderItem(16)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"resume", None));

        __sortingEnabled = self.tableWidget_3.isSortingEnabled()
        self.tableWidget_3.setSortingEnabled(False)
        self.tableWidget_3.setSortingEnabled(__sortingEnabled)

        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Setting", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"Train", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Pause", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Terminate", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"Terminal", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_train), QCoreApplication.translate("MainWindow", u"Train", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_graph), QCoreApplication.translate("MainWindow", u"Graph", None))
    # retranslateUi

