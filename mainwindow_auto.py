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
        self.cbDate.setGeometry(QtCore.QRect(80, 0, 69, 22))
        self.cbDate.setObjectName("cbDate")
        self.cbAmount = QtWidgets.QComboBox(self.centralWidget)
        self.cbAmount.setGeometry(QtCore.QRect(150, 0, 69, 22))
        self.cbAmount.setObjectName("cbAmount")
        self.cbCheckNum = QtWidgets.QComboBox(self.centralWidget)
        self.cbCheckNum.setGeometry(QtCore.QRect(230, 0, 69, 22))
        self.cbCheckNum.setObjectName("cbCheckNum")
        self.cbDescription = QtWidgets.QComboBox(self.centralWidget)
        self.cbDescription.setGeometry(QtCore.QRect(320, 0, 69, 22))
        self.cbDescription.setObjectName("cbDescription")
        self.listEntries = QtWidgets.QListView(self.centralWidget)
        self.listEntries.setGeometry(QtCore.QRect(10, 30, 1011, 511))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(9)
        self.listEntries.setFont(font)
        self.listEntries.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listEntries.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed|QtWidgets.QAbstractItemView.SelectedClicked)
        self.listEntries.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listEntries.setResizeMode(QtWidgets.QListView.Adjust)
        self.listEntries.setLayoutMode(QtWidgets.QListView.Batched)
        self.listEntries.setObjectName("listEntries")
        self.calendar1 = QtWidgets.QCalendarWidget(self.centralWidget)
        self.calendar1.setGeometry(QtCore.QRect(80, 0, 312, 183))
        self.calendar1.setObjectName("calendar1")
        self.calendar2 = QtWidgets.QCalendarWidget(self.centralWidget)
        self.calendar2.setGeometry(QtCore.QRect(390, 0, 312, 183))
        self.calendar2.setObjectName("calendar2")
        self.cbSearchIn = QtWidgets.QComboBox(self.centralWidget)
        self.cbSearchIn.setGeometry(QtCore.QRect(480, 0, 121, 22))
        self.cbSearchIn.setObjectName("cbSearchIn")
        self.labelSearchIn = QtWidgets.QLabel(self.centralWidget)
        self.labelSearchIn.setGeometry(QtCore.QRect(400, 0, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelSearchIn.setFont(font)
        self.labelSearchIn.setObjectName("labelSearchIn")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(620, 0, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName("label")
        self.cbGroupBy = QtWidgets.QComboBox(self.centralWidget)
        self.cbGroupBy.setGeometry(QtCore.QRect(700, 0, 101, 22))
        self.cbGroupBy.setObjectName("cbGroupBy")
        self.listEntries.raise_()
        self.btnOn.raise_()
        self.btnReadFile.raise_()
        self.cbCategory.raise_()
        self.cbDate.raise_()
        self.cbAmount.raise_()
        self.cbCheckNum.raise_()
        self.cbDescription.raise_()
        self.calendar1.raise_()
        self.cbSearchIn.raise_()
        self.labelSearchIn.raise_()
        self.label.raise_()
        self.cbGroupBy.raise_()
        self.calendar2.raise_()
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
        self.labelSearchIn.setText(_translate("MainWindow", "Search In:"))
        self.label.setText(_translate("MainWindow", "Group By:"))

