# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1032, 630)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.btnOn = QtWidgets.QPushButton(self.centralWidget)
        self.btnOn.setGeometry(QtCore.QRect(100, 550, 75, 23))
        self.btnOn.setObjectName("btnOn")
        self.btnReadFile = QtWidgets.QPushButton(self.centralWidget)
        self.btnReadFile.setGeometry(QtCore.QRect(9, 550, 84, 23))
        self.btnReadFile.setObjectName("btnReadFile")
        self.cbCategory = QtWidgets.QComboBox(self.centralWidget)
        self.cbCategory.setGeometry(QtCore.QRect(10, 0, 69, 22))
        self.cbCategory.setWhatsThis("")
        self.cbCategory.setCurrentText("")
        self.cbCategory.setModelColumn(0)
        self.cbCategory.setObjectName("cbCategory")
        self.cbDate = QtWidgets.QComboBox(self.centralWidget)
        self.cbDate.setGeometry(QtCore.QRect(90, 0, 69, 22))
        self.cbDate.setObjectName("cbDate")
        self.cbAmount = QtWidgets.QComboBox(self.centralWidget)
        self.cbAmount.setGeometry(QtCore.QRect(250, 0, 69, 22))
        self.cbAmount.setObjectName("cbAmount")
        self.cbCheckNum = QtWidgets.QComboBox(self.centralWidget)
        self.cbCheckNum.setGeometry(QtCore.QRect(480, 0, 69, 22))
        self.cbCheckNum.setObjectName("cbCheckNum")
        self.cbDescription = QtWidgets.QComboBox(self.centralWidget)
        self.cbDescription.setGeometry(QtCore.QRect(600, 0, 69, 22))
        self.cbDescription.setObjectName("cbDescription")
        self.listEntries = QtWidgets.QListWidget(self.centralWidget)
        self.listEntries.setGeometry(QtCore.QRect(10, 30, 1011, 511))
        self.listEntries.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listEntries.setObjectName("listEntries")
        self.calendar = QtWidgets.QCalendarWidget(self.centralWidget)
        self.calendar.setGeometry(QtCore.QRect(80, 0, 312, 183))
        self.calendar.setObjectName("calendar")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1032, 21))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        self.cbCategory.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnOn.setText(_translate("MainWindow", "ON"))
        self.btnReadFile.setText(_translate("MainWindow", "Read Check File"))
        self.listEntries.setSortingEnabled(False)

