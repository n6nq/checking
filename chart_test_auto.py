# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chart_test.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_predictions(object):
    def setupUi(self, predictions):
        predictions.setObjectName("predictions")
        predictions.resize(569, 505)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(20)
        sizePolicy.setVerticalStretch(20)
        #sizePolicy.setHeightForWidth(predictions.sizePolicy().hasHeightForWidth())
        predictions.setSizePolicy(sizePolicy)
        self.graph = QtWidgets.QGraphicsView(predictions)
        self.graph.setGeometry(QtCore.QRect(20, 20, 521, 451))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.graph.sizePolicy().hasHeightForWidth())
        self.graph.setSizePolicy(sizePolicy)
        self.graph.setMouseTracking(True)
        self.graph.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        brush = QtGui.QBrush(QtGui.QColor(190, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.graph.setBackgroundBrush(brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        self.graph.setForegroundBrush(brush)
        self.graph.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.graph.setObjectName("graph")

        self.retranslateUi(predictions)
        QtCore.QMetaObject.connectSlotsByName(predictions)

    def retranslateUi(self, predictions):
        _translate = QtCore.QCoreApplication.translate
        predictions.setWindowTitle(_translate("predictions", "Predicted Balances"))

