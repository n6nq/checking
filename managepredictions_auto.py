# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageepredictions.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PredictionsDialog(object):
    def setupUi(self, PredictionsDialog):
        PredictionsDialog.setObjectName("PredictionsDialog")
        PredictionsDialog.resize(1256, 546)
        self.buttonBox = QtWidgets.QDialogButtonBox(PredictionsDialog)
        self.buttonBox.setGeometry(QtCore.QRect(910, 510, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.predictionsView = QtWidgets.QTableView(PredictionsDialog)
        self.predictionsView.setGeometry(QtCore.QRect(10, 30, 1221, 421))
        self.predictionsView.setSortingEnabled(True)
        self.predictionsView.setObjectName("predictionsView")
        self.predictionsView.horizontalHeader().setStretchLastSection(True)
        self.editName = QtWidgets.QTextEdit(PredictionsDialog)
        self.editName.setGeometry(QtCore.QRect(10, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editName.setFont(font)
        self.editName.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editName.setObjectName("editName")
        self.labelName = QtWidgets.QLabel(PredictionsDialog)
        self.labelName.setGeometry(QtCore.QRect(10, 446, 31, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelName.setFont(font)
        self.labelName.setObjectName("labelName")
        self.labelCat = QtWidgets.QLabel(PredictionsDialog)
        self.labelCat.setGeometry(QtCore.QRect(130, 450, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelCat.setFont(font)
        self.labelCat.setObjectName("labelCat")
        self.comboCat = QtWidgets.QComboBox(PredictionsDialog)
        self.comboCat.setGeometry(QtCore.QRect(130, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboCat.setFont(font)
        self.comboCat.setObjectName("comboCat")
        self.label_Trig = QtWidgets.QLabel(PredictionsDialog)
        self.label_Trig.setGeometry(QtCore.QRect(260, 450, 21, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_Trig.setFont(font)
        self.label_Trig.setObjectName("label_Trig")
        self.editTrig = QtWidgets.QTextEdit(PredictionsDialog)
        self.editTrig.setGeometry(QtCore.QRect(250, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editTrig.setFont(font)
        self.editTrig.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editTrig.setObjectName("editTrig")
        self.labelOver = QtWidgets.QLabel(PredictionsDialog)
        self.labelOver.setGeometry(QtCore.QRect(370, 450, 31, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelOver.setFont(font)
        self.labelOver.setObjectName("labelOver")
        self.editOver = QtWidgets.QTextEdit(PredictionsDialog)
        self.editOver.setGeometry(QtCore.QRect(370, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editOver.setFont(font)
        self.editOver.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editOver.setObjectName("editOver")
        self.labelType = QtWidgets.QLabel(PredictionsDialog)
        self.labelType.setGeometry(QtCore.QRect(480, 450, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelType.setFont(font)
        self.labelType.setObjectName("labelType")
        self.comboType = QtWidgets.QComboBox(PredictionsDialog)
        self.comboType.setGeometry(QtCore.QRect(480, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboType.setFont(font)
        self.comboType.setObjectName("comboType")
        self.comboCycle = QtWidgets.QComboBox(PredictionsDialog)
        self.comboCycle.setGeometry(QtCore.QRect(590, 470, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboCycle.setFont(font)
        self.comboCycle.setObjectName("comboCycle")
        self.labelCycle = QtWidgets.QLabel(PredictionsDialog)
        self.labelCycle.setGeometry(QtCore.QRect(590, 450, 31, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelCycle.setFont(font)
        self.labelCycle.setObjectName("labelCycle")
        self.editDate = QtWidgets.QDateEdit(PredictionsDialog)
        self.editDate.setGeometry(QtCore.QRect(680, 471, 110, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editDate.setFont(font)
        self.editDate.setInputMethodHints(QtCore.Qt.ImhDate)
        self.editDate.setDate(QtCore.QDate(2017, 11, 21))
        self.editDate.setObjectName("editDate")
        self.editComment = QtWidgets.QTextEdit(PredictionsDialog)
        self.editComment.setGeometry(QtCore.QRect(800, 470, 431, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.editComment.setFont(font)
        self.editComment.setInputMethodHints(QtCore.Qt.ImhNone)
        self.editComment.setObjectName("editComment")
        self.labelComment = QtWidgets.QLabel(PredictionsDialog)
        self.labelComment.setGeometry(QtCore.QRect(800, 450, 51, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelComment.setFont(font)
        self.labelComment.setObjectName("labelComment")
        self.labelDate = QtWidgets.QLabel(PredictionsDialog)
        self.labelDate.setGeometry(QtCore.QRect(680, 450, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelDate.setFont(font)
        self.labelDate.setObjectName("labelDate")
        self.sortName = QtWidgets.QComboBox(PredictionsDialog)
        self.sortName.setGeometry(QtCore.QRect(10, 10, 91, 22))
        self.sortName.setObjectName("sortName")
        self.sortCategory = QtWidgets.QComboBox(PredictionsDialog)
        self.sortCategory.setGeometry(QtCore.QRect(120, 10, 91, 22))
        self.sortCategory.setObjectName("sortCategory")
        self.sortTrigger = QtWidgets.QComboBox(PredictionsDialog)
        self.sortTrigger.setGeometry(QtCore.QRect(240, 10, 91, 22))
        self.sortTrigger.setObjectName("sortTrigger")
        self.sortOverride = QtWidgets.QComboBox(PredictionsDialog)
        self.sortOverride.setGeometry(QtCore.QRect(350, 10, 91, 22))
        self.sortOverride.setObjectName("sortOverride")
        self.sortType = QtWidgets.QComboBox(PredictionsDialog)
        self.sortType.setGeometry(QtCore.QRect(470, 10, 91, 22))
        self.sortType.setObjectName("sortType")
        self.sortCycle = QtWidgets.QComboBox(PredictionsDialog)
        self.sortCycle.setGeometry(QtCore.QRect(580, 10, 91, 22))
        self.sortCycle.setObjectName("sortCycle")
        self.sortDate = QtWidgets.QComboBox(PredictionsDialog)
        self.sortDate.setGeometry(QtCore.QRect(680, 10, 91, 22))
        self.sortDate.setObjectName("sortDate")
        self.sortComment = QtWidgets.QComboBox(PredictionsDialog)
        self.sortComment.setGeometry(QtCore.QRect(790, 10, 91, 22))
        self.sortComment.setObjectName("sortComment")
        self.buttonAdd = QtWidgets.QPushButton(PredictionsDialog)
        self.buttonAdd.setGeometry(QtCore.QRect(20, 512, 81, 31))
        self.buttonAdd.setObjectName("buttonAdd")
        self.buttonUpdate = QtWidgets.QPushButton(PredictionsDialog)
        self.buttonUpdate.setGeometry(QtCore.QRect(140, 510, 81, 31))
        self.buttonUpdate.setObjectName("buttonUpdate")
        self.buttonDelete = QtWidgets.QPushButton(PredictionsDialog)
        self.buttonDelete.setGeometry(QtCore.QRect(250, 510, 81, 31))
        self.buttonDelete.setObjectName("buttonDelete")
        self.buttonClear = QtWidgets.QPushButton(PredictionsDialog)
        self.buttonClear.setGeometry(QtCore.QRect(360, 510, 81, 31))
        self.buttonClear.setObjectName("buttonClear")
        self.comboDate = QtWidgets.QComboBox(PredictionsDialog)
        self.comboDate.setGeometry(QtCore.QRect(680, 500, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboDate.setFont(font)
        self.comboDate.setObjectName("comboDate")

        self.retranslateUi(PredictionsDialog)
        self.buttonBox.accepted.connect(PredictionsDialog.accept)
        self.buttonBox.rejected.connect(PredictionsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PredictionsDialog)

    def retranslateUi(self, PredictionsDialog):
        _translate = QtCore.QCoreApplication.translate
        PredictionsDialog.setWindowTitle(_translate("PredictionsDialog", "Dialog"))
        self.labelName.setText(_translate("PredictionsDialog", "Name"))
        self.labelCat.setText(_translate("PredictionsDialog", "Cat"))
        self.label_Trig.setText(_translate("PredictionsDialog", "Trig"))
        self.labelOver.setText(_translate("PredictionsDialog", "Over"))
        self.labelType.setText(_translate("PredictionsDialog", "Type"))
        self.labelCycle.setText(_translate("PredictionsDialog", "Cycle"))
        self.labelComment.setText(_translate("PredictionsDialog", "Comment"))
        self.labelDate.setText(_translate("PredictionsDialog", "Date Expr"))
        self.buttonAdd.setText(_translate("PredictionsDialog", "Add"))
        self.buttonUpdate.setText(_translate("PredictionsDialog", "Update"))
        self.buttonDelete.setText(_translate("PredictionsDialog", "Delete"))
        self.buttonClear.setText(_translate("PredictionsDialog", "Clear"))

