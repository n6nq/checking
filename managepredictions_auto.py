# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageepredictions.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1256, 546)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(910, 510, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.predictionsView = QtWidgets.QTableView(Dialog)
        self.predictionsView.setGeometry(QtCore.QRect(10, 30, 1221, 421))
        self.predictionsView.setSortingEnabled(True)
        self.predictionsView.setObjectName("predictionsView")
        self.predictionsView.horizontalHeader().setStretchLastSection(True)
        self.edtName = QtWidgets.QTextEdit(Dialog)
        self.edtName.setGeometry(QtCore.QRect(10, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.edtName.setFont(font)
        self.edtName.setInputMethodHints(QtCore.Qt.ImhNone)
        self.edtName.setObjectName("edtName")
        self.labelName = QtWidgets.QLabel(Dialog)
        self.labelName.setGeometry(QtCore.QRect(10, 446, 31, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelName.setFont(font)
        self.labelName.setObjectName("labelName")
        self.labelCat = QtWidgets.QLabel(Dialog)
        self.labelCat.setGeometry(QtCore.QRect(130, 450, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelCat.setFont(font)
        self.labelCat.setObjectName("labelCat")
        self.comboCat = QtWidgets.QComboBox(Dialog)
        self.comboCat.setGeometry(QtCore.QRect(130, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboCat.setFont(font)
        self.comboCat.setObjectName("comboCat")
        self.label_Trig = QtWidgets.QLabel(Dialog)
        self.label_Trig.setGeometry(QtCore.QRect(260, 450, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_Trig.setFont(font)
        self.label_Trig.setObjectName("label_Trig")
        self.editTrig = QtWidgets.QTextEdit(Dialog)
        self.editTrig.setGeometry(QtCore.QRect(250, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editTrig.setFont(font)
        self.editTrig.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editTrig.setObjectName("editTrig")
        self.labelOver = QtWidgets.QLabel(Dialog)
        self.labelOver.setGeometry(QtCore.QRect(370, 450, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelOver.setFont(font)
        self.labelOver.setObjectName("labelOver")
        self.editOver = QtWidgets.QTextEdit(Dialog)
        self.editOver.setGeometry(QtCore.QRect(370, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editOver.setFont(font)
        self.editOver.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editOver.setObjectName("editOver")
        self.labelType = QtWidgets.QLabel(Dialog)
        self.labelType.setGeometry(QtCore.QRect(480, 450, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelType.setFont(font)
        self.labelType.setObjectName("labelType")
        self.comboType = QtWidgets.QComboBox(Dialog)
        self.comboType.setGeometry(QtCore.QRect(480, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboType.setFont(font)
        self.comboType.setObjectName("comboType")
        self.combCyle = QtWidgets.QComboBox(Dialog)
        self.combCyle.setGeometry(QtCore.QRect(590, 470, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.combCyle.setFont(font)
        self.combCyle.setObjectName("combCyle")
        self.labelCycle = QtWidgets.QLabel(Dialog)
        self.labelCycle.setGeometry(QtCore.QRect(590, 450, 31, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelCycle.setFont(font)
        self.labelCycle.setObjectName("labelCycle")
        self.editDate = QtWidgets.QDateEdit(Dialog)
        self.editDate.setGeometry(QtCore.QRect(680, 471, 110, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editDate.setFont(font)
        self.editDate.setInputMethodHints(QtCore.Qt.ImhDate)
        self.editDate.setDate(QtCore.QDate(2017, 11, 21))
        self.editDate.setObjectName("editDate")
        self.editComment = QtWidgets.QTextEdit(Dialog)
        self.editComment.setGeometry(QtCore.QRect(800, 470, 431, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editComment.setFont(font)
        self.editComment.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editComment.setObjectName("editComment")
        self.labelComment = QtWidgets.QLabel(Dialog)
        self.labelComment.setGeometry(QtCore.QRect(800, 450, 51, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelComment.setFont(font)
        self.labelComment.setObjectName("labelComment")
        self.labelDate = QtWidgets.QLabel(Dialog)
        self.labelDate.setGeometry(QtCore.QRect(680, 450, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelDate.setFont(font)
        self.labelDate.setObjectName("labelDate")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.labelName.setText(_translate("Dialog", "Name"))
        self.labelCat.setText(_translate("Dialog", "Cat"))
        self.label_Trig.setText(_translate("Dialog", "Trig"))
        self.labelOver.setText(_translate("Dialog", "Over"))
        self.labelType.setText(_translate("Dialog", "Type"))
        self.labelCycle.setText(_translate("Dialog", "Cycle"))
        self.labelComment.setText(_translate("Dialog", "Comment"))
        self.labelDate.setText(_translate("Dialog", "Date Expr"))

