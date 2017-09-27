
from PyQt5.QtWidgets import (QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsScene)
from PyQt5.QtCore import (QLineF, QSize, QRectF)
from database import Database
from chart_test_auto import Ui_predictions

class ChartTestDialog(QDialog, Ui_predictions):
    
    def __init__(self, db):
        super(ChartTestDialog, self).__init__()
        self.db = db
        self.setupUi(self)
        
        entries = self.db.get_last_three_months()
        nEntries = len(entries)
        entries = sorted(entries, key=lambda ent: ent.date.isoformat())        
        reversed = entries.reverse()
        balances = []
        start_balance = 80000
        balances.append
        for ent in reversed:
            
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
        self.graph.resize(QSize(width-40, height-40))
        rect = QRectF(0, 0, width, height)
        self.graph.fitInView(rect)
