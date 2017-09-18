
from PyQt5.QtWidgets import (QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsScene)
from PyQt5.QtCore import QLineF

from chart_test_auto import Ui_ChartTestDialog

class ChartTestDialog(QDialog, Ui_ChartTestDialog):
    
    def __init__(self):
        super(ChartTestDialog, self).__init__()
        
        self.setupUi(self)
        
        scene = QGraphicsScene()
        scene
        self.graphicsView.setScene(scene)
        self.graphicsView.scale(1, -1)
        scene.addLine( QLineF( 0, 0, 300, 300 ))
        
        self.exec_()


