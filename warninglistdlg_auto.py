# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'warninglistdlg.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_warninglistdlg(object):
    def setupUi(self, warninglistdlg):
        warninglistdlg.setObjectName("warninglistdlg")
        warninglistdlg.setWindowModality(QtCore.Qt.ApplicationModal)
        warninglistdlg.resize(640, 480)
        self.edtWarning = QtWidgets.QPlainTextEdit(warninglistdlg)
        self.edtWarning.setGeometry(QtCore.QRect(10, 30, 621, 71))
        self.edtWarning.setToolTipDuration(3)
        self.edtWarning.setObjectName("edtWarning")
        self.listAffected = QtWidgets.QListWidget(warninglistdlg)
        self.listAffected.setGeometry(QtCore.QRect(10, 110, 621, 321))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.listAffected.setFont(font)
        self.listAffected.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listAffected.setProperty("showDropIndicator", False)
        self.listAffected.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.listAffected.setObjectName("listAffected")
        self.btnCancel = QtWidgets.QPushButton(warninglistdlg)
        self.btnCancel.setGeometry(QtCore.QRect(550, 440, 75, 23))
        self.btnCancel.setObjectName("btnCancel")
        self.btnProceed = QtWidgets.QPushButton(warninglistdlg)
        self.btnProceed.setGeometry(QtCore.QRect(460, 440, 75, 23))
        self.btnProceed.setObjectName("btnProceed")

        self.retranslateUi(warninglistdlg)
        QtCore.QMetaObject.connectSlotsByName(warninglistdlg)

    def retranslateUi(self, warninglistdlg):
        _translate = QtCore.QCoreApplication.translate
        warninglistdlg.setWindowTitle(_translate("warninglistdlg", "Warning!"))
        self.edtWarning.setToolTip(_translate("warninglistdlg", "Warning related to proposed action."))
        self.edtWarning.setWhatsThis(_translate("warninglistdlg", "Warning related to proposed action."))
        self.edtWarning.setPlaceholderText(_translate("warninglistdlg", "Warninig missing!"))
        self.listAffected.setToolTip(_translate("warninglistdlg", "List of items that will be affected by this action."))
        self.listAffected.setWhatsThis(_translate("warninglistdlg", "List of items that will be affected by this action."))
        self.listAffected.setSortingEnabled(True)
        self.btnCancel.setText(_translate("warninglistdlg", "Cancel"))
        self.btnProceed.setText(_translate("warninglistdlg", "Proceed"))

