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
        self.listWidget.currentRowChanged.connect(self.listSelectionChanged)
        
        self.index = 0
        self.lastSelected = -1
        self.before = 0
        self.after = 0
        
        self.min_bal = 9999.99
        self.max_bal = -9999.99
        today = datetime.date.today()
        
        astr = 'Please import bank data up to today, {} and then enter the current balance.\nBalance:'.format(today.isoformat())
        values = QInputDialog.getText(self, 'Balance?', astr)
        if values[1] == False:
            return
        
        self.starting_balance = int(float(values[0]) * 100)

        self.entries = []
        self.balances = []
        self.nEntries = 0
        self.nFutures = 0
        
        self.get_future_data(today, self.starting_balance)

        self.max_bal = max(self.balances)
        self.min_bal = min(self.balances)
        
        self.scene = ChartScene(self)
        self.showRects(1)
        scenewidth = (self.nEntries + self.nFutures) * XINC
        sceneYmax = round((self.max_bal/100), -2)
        sceneYmin = round((self.min_bal/100), -2)
        self.showRects(2)
        viewrect = self.graphicsView.rect()
        
        pen = QPen(Qt.black)
        pen.setWidth(0)
        
        font = QFont()
        font.setPixelSize(16)
        
        i = j = 0
        
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
        
        
        self.showRects(4)        
        self.graphicsView.scale(1.44, -.185) 
        
        self.scene.setSceneRect(QRectF(QPointF(0, sceneYmin), QPointF(scenewidth, sceneYmax)))
        self.graphicsView.setScene(self.scene)
        self.show()
        
    def listSelectionChanged(self, currentRow):
        if currentRow >= 0:
            pen = QPen()
            if self.lastSelected >= 0:
                pen.setWidthF(4.0)
                pen.setColor(Qt.white)
                selected = self.lastSelected
                self.scene.addLine( QLineF( selected * XINC, self.balances[selected]/100, (selected+1) * XINC, self.balances[selected+1]/100), pen)
                pen.setWidth(0)
                pen.setColor(Qt.red)
                self.scene.addLine( QLineF( selected * XINC, self.balances[selected]/100, (selected+1) * XINC, self.balances[selected+1]/100), pen)
            
            selected = (self.index - self.before) + currentRow - 1
            self.lastSelected = selected
            pen.setColor(Qt.blue)
            pen.setWidthF(4.0)
            self.scene.addLine( QLineF( selected * XINC, self.balances[selected]/100, (selected+1) * XINC, self.balances[selected+1]/100), pen)
        

    def resizeGraph(self, size):
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

        x = mouseEvent.scenePos().x() + (XINC / 2)
        y = mouseEvent.scenePos().y()
        print('P', x, y)
        index = int(round(x / XINC))
        self.displayRangeAt(index, 10, 10)
        self.showRects(7)
        #QGraphicsScene.mousePressEvent(self, mouseEvent)

    def displayRangeAt(self, index, before, after):
        if index < 0 or index >= (self.nEntries + self.nFutures):
            return
        
        self.index = index
        self.before = before
        self.after = after
        
        rlist = self.entries + self.futures
        selected = rlist[max((index-before), 0):(index+after)]
        showList = []
        self.listWidget.clear()
        
        for pent in selected:
            self.listWidget.addItem(pent.asCategorizedStr())
          
        self.listWidget.setCurrentRow(10)
