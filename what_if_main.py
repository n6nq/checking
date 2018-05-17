from PyQt5.QtCore import pyqtSignal, QLineF, QSize, QRectF, QPointF, Qt
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QGraphicsScene, QGraphicsItem  #(QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsTextItem)
from PyQt5.QtGui import QPen, QFont
import datetime

from warninglistdialog import WarningListDialog
from predicted import Prediction
from pcycle import PCycle
from what_if_auto import Ui_MainWindow

""" NOTES:
    TODOS: Remove type from predictions and UI
    You can't change predictions into entries. Duh!
    There is no holder for cycle. Remove entries from what_if.
"""

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
        
        self.selectedIdx = -1        # only setSelectionAt sets this to real value, avoids loops I think
        self.lastSelected = -1  #what
        
        min_bal = 9999.99
        max_bal = -9999.99
        today = datetime.date.today()
        
        astr = 'Please import bank data up to today, {} and then enter the current balance.\nBalance:'.format(today.isoformat())
        values = QInputDialog.getText(self, 'Balance?', astr)
        if values[1] == False:
            return
        
        self.starting_balance = int(float(values[0]) * 100)
        
        for cat in sorted(self.db.cat_to_oid.keys()):
            self.comboCat.addItem(cat)
            
        for trig in sorted(self.db.trig_to_oid.keys()):
            self.comboTrig.addItem(trig)
        
        self.cycleList = PCycle.get_cycle_list()
        self.comboCycle.addItems(self.cycleList)

        self.entries = []
        self.futures = []
        self.balances = []
        self.nEntries = 0
        self.nFutures = 0
        past = False        #someday
        
        if past:
            self.get_past_data(today, self.starting_balance)
            
        self.get_future_data(today, self.starting_balance)
        
        self.all_items = self.entries + self.futures
        self.nItems = len(self.all_items)

        max_bal = max(self.balances)
        min_bal = min(self.balances)
        
        self.scene = ChartScene(self)
        self.showRects(1)
        scenewidth = (self.nEntries + self.nFutures) * XINC
        sceneYmax = round((max_bal/100), -2)
        sceneYmin = round((min_bal/100), -2)
        self.showRects(2)
        viewrect = self.graphicsView.rect()
        
        pen = QPen(Qt.black)
        pen.setWidth(0)
        
        font = QFont()
        font.setPixelSize(16)
        
        i = j = 0
        
        for i in range(0, self.nEntries-1):
            self.scene.addLine( QLineF( i * XINC, self.balances[i]/100, (i+1) * XINC, self.balances[i+1]/100), pen)
            self.listWidget.addItem(self.entries[i].asCategorizedStr())
            
        pen.setColor(Qt.red)

        for j in range(0, self.nFutures-1):
            self.scene.addLine( QLineF( (i+j) * XINC, self.balances[i+j]/100, (i+j+1) * XINC, self.balances[i+j+1]/100), pen)
            self.listWidget.addItem(self.futures[i+j].asCategorizedStr())
            
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
        self.setSelectionAt(0)      
        self.show()
    
    def set_fields(self, index):
        length = len(self.all_items)
        if index >= length:
            index = length - 1
        pent = self.all_items[index]
        self.selected_oid = pent.oid
        pred_oid = int(pent.oid /65336)
        pred = self.db.find_pred_by_oid(pred_oid)
        if pred is None:
            self.editAmount.setText("None")
            self.comboCat.setCurrentText("None")
            self.comboTrig.setCurrentText("None")
            self.comboOver.setCurrentText("None")
            self.comboCycle.setCurrentText("None")
        else:
            self.editAmount.setText(pred.amount.as_str())
            self.chkboxIncome.setChecked(pred.amount.value > 0)
            self.comboCat.setCurrentText(pred.cat)
        
            triggers = self.db.triggers_for_cat(pred.cat)
            self.comboTrig.clear()
            for trig in sorted(triggers, key=lambda trig: trig.trig): 
                self.comboTrig.addItem(trig.trig)
            if pred.trig_id >= 0:
                self.comboTrig.setCurrentText(self.db.trig_for_oid(pred.trig_id))

            overrides = sorted(self.db.overs_for_cat(pred.cat))
            self.comboOver.clear()
            for over in overrides:
                self.comboOver.addItem(over.over)
            if pred.over_id >= 0:
                self.comboOver.setCurrentText(self.db.over_for_oid(pred.over_id))
        
            #self.comboType.setCurrentText(pred.t) #entry doesn't have a type, get rid of type
        
            self.comboCycle.setCurrentText(pred.cycle.get_date_str())  #
            set comboCycle with the cycle type
            set editDate and comboDate
        
        #self.income = income
        #self.cat = cat
        #self.trig = trig
        #self.over = over
        #self.cat_id = cat_id
        #self.trig_id = trig_id
        #self.over_id = over_id
        #comboType        self.p_type = p_type
        #comboCycle        self.cycle = PCycle(cycle, ddate, vdate)
        #editDate
        #comboDate
        #buttonAdd
        #buttonUpdate
        #chkboxIncome
        #buttonDelete
        #buttonClear
        #editComment
        #self.desc = desc
        
    def setSelectionAt(self, index):
        if index != self.selectedIdx:
            self.set_fields(index)
            pen = QPen()
            if self.lastSelected >= 0:
                pen.setWidthF(4.0)
                pen.setColor(Qt.white)
                lselected = self.lastSelected
                self.scene.addLine( QLineF( lselected * XINC, self.balances[lselected]/100, (lselected+1) * XINC, self.balances[lselected+1]/100), pen)
                pen.setWidth(0)
                pen.setColor(Qt.red)
                self.scene.addLine( QLineF( lselected * XINC, self.balances[lselected]/100, (lselected+1) * XINC, self.balances[lselected+1]/100), pen)
            
            pen.setColor(Qt.blue)
            pen.setWidthF(4.0)
            x1 = index
            if (x1 >= len(self.balances) - 1):
                x1 = len(self.balances) - 2
            x2 = x1 + 1
            self.scene.addLine( QLineF( x1 * XINC, self.balances[x1]/100, x2 * XINC, self.balances[x2]/100), pen)
            self.lastSelected = x1
            self.listWidget.setCurrentRow(x1)
        
    
    def listSelectionChanged(self, currentRow):
        if currentRow != self.lastSelected:
            self.setSelectionAt(currentRow)
#            pen = QPen()
#            if self.lastSelected >= 0:
#                pen.setWidthF(4.0)
#                pen.setColor(Qt.white)
#                selected = self.lastSelected
#                self.scene.addLine( QLineF( selected * XINC, self.balances[selected]/100, (selected+1) * XINC, self.balances[selected+1]/100), pen)
#                pen.setWidth(0)
#                pen.setColor(Qt.red)
#                self.scene.addLine( QLineF( selected * XINC, self.balances[selected]/100, (selected+1) * XINC, self.balances[selected+1]/100), pen)
#            
#            self.lastSelected = index
#            pen.setColor(Qt.blue)
#            pen.setWidthF(4.0)
#            self.scene.addLine( QLineF( index * XINC, self.balances[index]/100, (selected+1) * XINC, self.balances[selected+1]/100), pen)
        

    def resizeGraph(self, size):
        width = size.width()
        height = size.height()
        self.graphicsView.resize(QSize(width-40, height-40))
        self.showRects(6)
        
#        rect = QRectF(0, 0, width, height)
        self.graphicsView.fitInView(self.scene.sceneRect())
        self.showRects(7)

    def get_past_data(self, today, starting_balance):
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
        self.balances.append(starting_bal)  #we should only do this if not showing past
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
        selected = int(round(x / XINC))
        self.setSelectionAt(selected)
#        self.displayRangeAt(selected, 10, 10)
#        self.showRects(7)
        #QGraphicsScene.mousePressEvent(self, mouseEvent)

    def displayRangeAt(self, selected, before, after):
        if index < 0 or index >= (self.nEntries + self.nFutures):
            return
        
        self.index = index
  #fix      self.before = before
  #fix      self.after = after
        
        rlist = self.entries + self.futures
 #fix       selected = rlist[(index-before):(index+after)]
 #fix       selected = rlist[max((index-before), 0):(index+after)]
        showList = []
        self.listWidget.clear()
        
        for pent in selected:
            self.listWidget.addItem(pent.asCategorizedStr())
          
        self.listWidget.setCurrentRow(10)
