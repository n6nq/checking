
from PyQt5.QtWidgets import (QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsScene)
from PyQt5.QtCore import (QLineF, QSize, QRectF)

from chart_test_auto import Ui_predictions

class ChartTestDialog(QDialog, Ui_predictions):
    
    def __init__(self):
        super(ChartTestDialog, self).__init__()
        
        self.setupUi(self)
        
        self.scene = QGraphicsScene()
        self.graph.setScene(self.scene)
        self.graph.scale(1, -1)
        #self.resizeEvent.connect(self.resizeGraph())
        self.scene.addLine( QLineF( 0, 0, 300, 300 ))
        
        self.exec_()
    
    def resizeEvent(self, evt):
        self.resizeGraph(evt.size())
        
    def resizeGraph(self, size):
        width = size.width()
        height = size.height()
        self.graph.resize(QSize(height-80, width-80))
        rect = QRectF(0, 0, width, height)
        self.graph.fitInView(rect)
