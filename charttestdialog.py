
from PyQt5.QtWidgets import (QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsScene, QInputDialog)
from PyQt5.QtCore import (QLineF, QSize, QRectF)
from database import Database
import datetime
from chart_test_auto import Ui_predictions

class ChartTestDialog(QDialog, Ui_predictions):
    
    def __init__(self, db):
        super(ChartTestDialog, self).__init__()
        self.db = db
        self.setupUi(self)
        
        today = datetime.date.today()
        str = 'Please import bank data up to today, {} and then enter the current balance.\nBalance:'.format(today.isoformat())
        values = QInputDialog.getText(self, 'Balance?', str)
        if values[1] == False:
            return
        
        self.get_chart_data(today, values[0])
            
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 500, 400))
        self.graph.setScene(self.scene)
        self.graph.scale(1, -1)
        #self.resizeEvent.connect(self.resizeGraph())
        for i in range(0, self.nEntries-1):
            self.scene.addLine( QLineF( i * 4, self.balances[i]/400, (i+1) * 4, self.balances[i+1]/400 ))
        
        self.exec_()
    
    def resizeEvent(self, evt):
        self.resizeGraph(evt.size())
        
    def resizeGraph(self, size):
        width = size.width()
        height = size.height()
        self.graph.resize(QSize(width-40, height-40))
        rect = QRectF(0, 0, width, height)
        self.graph.fitInView(rect)

    def get_chart_data(self, today, starting_balance):
        entries = self.db.get_last_three_months(today)
        self.nEntries = len(entries)
        reversed_entries = sorted(entries, key=lambda ent: ent.date.isoformat(), reverse=True)        
        self.balances = []
        running = int(float(starting_balance) * 100)
        self.balances.append(running)

        for ent in reversed_entries:
            running -= ent.amount.value
            self.balances.append(running)
        self.balances.reverse()
        