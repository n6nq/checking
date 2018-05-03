from PyQt5.QtCore import pyqtSignal, QLineF, QSize, QRectF, QPointF, Qt
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QGraphicsScene, QGraphicsItem  #(QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsTextItem)
from PyQt5.QtGui import QPen, QFont
import datetime

from warninglistdialog import WarningListDialog
from what_if_auto import Ui_MainWindow

class ChartScene(QGraphicsScene):
    
    def __init__(self, parent):
        super(ChartScene, self).__init__()
        self.parent = parent
        
    def mousePressEvent(self, mouseEvent):
        super(ChartScene, self).mousePressEvent(mouseEvent)
        x = mouseEvent.scenePos().x()
        y = mouseEvent.scenePos().y()
        print(x, y)
        self.parent.sceneMousePressEvent(mouseEvent)

XINC = 4

class WhatIfMain(QMainWindow, Ui_MainWindow):
    
    myresize = pyqtSignal('QSize')
    
    def __init__(self, db):
        super(self.__class__, self).__init__()
        self.setupUi(self)        
        self.db = db

        self.myresize.connect(self.resizeGraph)
        
        self.min_bal = 9999.99
        self.max_bal = -9999.99
        today = datetime.date.today()
        astr = 'Please import bank data up to today, {} and then enter the current balance.\nBalance:'.format(today.isoformat())
        values = QInputDialog.getText(self, 'Balance?', astr)
        if values[1] == False:
            return
        
        
        self.starting_balance = int(float(values[0]) * 100)
        self.get_chart_data(today, self.starting_balance)

        self.get_future_data(today, self.starting_balance)

        self.max_bal = max(self.balances)
        self.min_bal = min(self.balances)
        
        self.scene = ChartScene(self)
        self.showRects(1)
        scenewidth = (self.nEntries + self.nFutures) * XINC
        sceneYmax = round((self.max_bal/100), -2)
        sceneYmin = round((self.min_bal/100), -2)
        #= (self.max_bal - self.min_bal) / 100
        self.showRects(2)
        #self.graphicsView.setSceneRect(QRectF(0, 0, width, height))
        viewrect = self.graphicsView.rect()
        
        pen = QPen(Qt.black)
        pen.setWidth(0)
        
        font = QFont()
        font.setPixelSize(16)
        
    
        for i in range(0, self.nEntries-1):
            self.scene.addLine( QLineF( i * XINC, self.balances[i]/100, (i+1) * XINC, self.balances[i+1]/100), pen)

        pen.setColor(Qt.red)

        for j in range(0, self.nFutures-1):
            self.scene.addLine( QLineF( (i+j) * XINC, self.balances[i+j]/100, (i+j+1) * XINC, self.balances[i+j+1]/100), pen)
            
        pen.setColor(Qt.black)
        
        for liney in range(int(sceneYmin), int(sceneYmax+100), 200):
            self.scene.addLine(QLineF(0.0, liney, scenewidth, liney), pen)
            myText = self.scene.addText(str(liney), font)
            myText.moveBy(20, liney+100)
            myText.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        
        
        #self.resizeGraph(QSize(viewrect.width(), viewrect.height()))
        self.showRects(4)        
        #oldMatrix = self.graphicsView.transform()
        #self.graphicsView.resetTransform()
        #self.graphicsView.translate(oldMatrix.dx(), oldMatrix.dy());
        self.graphicsView.scale(.45, -.20) 
        #self.showRects(5.5)
        #self.myresize.emit(QSize(viewrect.width(), viewrect.height()))
        
        self.scene.setSceneRect(QRectF(QPointF(0, sceneYmin), QPointF(scenewidth, sceneYmax)))
        self.graphicsView.setScene(self.scene)
        self.show()
        
    def resizeGraph(self, size):
 #       width = (self.nEntries+100) * XINC
 #       height = (self.max_bal - self.min_bal)
 #       self.scene.setSceneRect(QRectF(0, 0, width, height))
 #       viewport = self.graphicsView.viewport()
 #       #self.graphicsView.setScene(self.scene)
 #       self.graphicsView.centerOn(QPointF(width/2, height/2))
 #       self.graphicsView.scale(width/viewport.width(), height/viewport.height())
        
        width = size.width()
        height = size.height()
        self.graphicsView.resize(QSize(width-40, height-40))
        self.showRects(6)
        
#        rect = QRectF(0, 0, width, height)
        self.graphicsView.fitInView(self.scene.sceneRect())
        self.showRects(7)

    def get_chart_data(self, today, starting_balance):
        self.entries = self.db.get_last_three_months(today)
        self.nEntries = len(self.entries)
        reversed_entries = sorted(self.entries, key=lambda ent: ent.date.isoformat(), reverse=True)        
        self.balances = []
        self.running = starting_balance
        self.balances.append(self.running)

        for ent in reversed_entries:
            self.running -= ent.amount.value
            self.balances.append(self.running)
            
        self.balances.reverse()
        
    def get_future_data(self, today, starting_bal):
        """This function used the predictions to produce three months of predicted future
           entries. today is the starting day or the period and starting_bal is the account
           balance as of today. """
        self.futures = self.db.get_next_three_months(today)
        self.nFutures = len(self.futures)
        
        self.running = starting_bal
        for ent in self.futures:
            self.running += ent.amount.value
            self.balances.append(self.running)
            
    def showRects(self, loc):
        sceneR = self.scene.sceneRect()
        viewR = self.graphicsView.rect()
        sstr = "{} scene: {},{},{},{}".format(loc, sceneR.left(), sceneR.bottom(), sceneR.right(), sceneR.top())
        vstr = " view: {},{},{},{}".format(viewR.left(), viewR.bottom(), viewR.right(), viewR.top())
        print(sstr, vstr)

    def sceneMousePressEvent(self, mouseEvent):

        x = mouseEvent.scenePos().x()
        y = mouseEvent.scenePos().y()
        print('P', x, y)
        index = int(round(x / XINC))
        self.displayRangeAt(index, 10, 10)
        #QGraphicsScene.mousePressEvent(self, mouseEvent)

    def displayRangeAt(self, index, before, after):
        if index < 0 or index >= (self.nEntries + self.nFutures):
            return
        
        rlist = self.entries + self.futures
        selected = rlist[(index-before):(index+after)]
        showList = []

        for pent in selected:
            showList.append(pent.asCategorizedStr())
            
        dl = WarningListDialog("Predictions", 
            "Here are the entries or predictions near your selection point.", 
            showList, False)        
        #for pent in selected:
        #    print(pent.amount.value, pent.desc)
