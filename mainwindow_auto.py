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
        MainWindow.resize(635, 342)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.btnOn = QtWidgets.QPushButton(self.centralWidget)
        self.btnOn.setObjectName("btnOn")
        self.gridLayout.addWidget(self.btnOn, 0, 0, 1, 1)
        self.btnReadFile = QtWidgets.QPushButton(self.centralWidget)
        self.btnReadFile.setObjectName("btnReadFile")
        self.gridLayout.addWidget(self.btnReadFile, 0, 1, 1, 1)
        self.listCategorized = QtWidgets.QListWidget(self.centralWidget)
        self.listCategorized.setAlternatingRowColors(True)
        self.listCategorized.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listCategorized.setObjectName("listCategorized")
        self.gridLayout.addWidget(self.listCategorized, 1, 0, 1, 2)
        self.listUnCategorized = QtWidgets.QListWidget(self.centralWidget)
        self.listUnCategorized.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.listUnCategorized.setObjectName("listUnCategorized")
        self.gridLayout.addWidget(self.listUnCategorized, 2, 0, 1, 2)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 635, 21))
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

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnOn.setText(_translate("MainWindow", "ON"))
        self.btnReadFile.setText(_translate("MainWindow", "Read Check File"))
        self.listCategorized.setWhatsThis(_translate("MainWindow", "lstCategorized"))

