from PyQt5.QtCore import pyqtSignal, QLineF, QSize, QRectF, QPointF, Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QGraphicsScene, QGraphicsItem  #(QDialog, QFileDialog, QMenu, QAction, QListWidgetItem, QGraphicsTextItem)
from PyQt5.QtGui import QPen, QFont
from datetime import date
from warninglistdialog import WarningListDialog
from predicted import Prediction
from pcycle import PCycle, Cycles, DaysOfWeek
from what_if_auto import Ui_MainWindow
from money import Money

""" NOTES:
    DONE: Remove type from predictions and UI
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

        self.scene = ChartScene(self)
        self.myresize.connect(self.resizeGraph)
        self.buttonAdd.clicked.connect(self.addPrediction)
        self.buttonUpdate.clicked.connect(self.updatePrediction)
        self.buttonDelete.clicked.connect(self.deletePrediction)
        self.buttonClear.clicked.connect(self.clearPrediction)
        self.comboCat.currentIndexChanged.connect(self.catChanged)
        self.listWidget.currentRowChanged.connect(self.listSelectionChanged)
        
        self.selectedIdx = -1        # only setSelectionAt sets this to real value, avoids loops I think
        self.lastSelected = -1  #what
        
        #min_bal = 9999.99
        #max_bal = -9999.99
        self.today = date.today()
        
        astr = 'Please import bank data up to today, {} and then enter the current balance.\nBalance:'.format(self.today.isoformat())
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
        past = False        #someday
        
        if past:
            self.get_past_data(self.today, self.starting_balance)
            
        self.get_future_data(self.today, self.starting_balance)
        if (len(self.futures) <= 0):
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Can't do it!")
            msgBox.setText('You can\'t display predicted transactions until you have defined some predictions!\nPlease try the "Manage Predictions" button.')
            msgBox.exec_()            
            return  
            
        
        self.refresh(True)

    def list_from_fields(self, oid):
        mny = Money.from_str(self.editAmount.text())
        income = self.chkboxIncome.checkState()
        amount = mny.value
        if income and amount < 0:
            amount = abs(amount)
        elif not income and amount > 0:
            amount = 0 - amount
        cat = self.comboCat.currentText()
        cat_id = self.db.cat_to_oid[cat]
        trig = self.comboTrig.currentText()
        trig_id = self.db.oid_for_trig(trig)
        over = self.comboOver.currentText()
        over_id = self.db.oid_for_over(over)
        #ptypestr = self.comboType.currentText()
        #ptype = Prediction.get_ptype_from_str(ptypestr)
        #ptype = 5
        cyclestr = self.comboCycle.currentText()
        cycle = PCycle.get_cycle_from_str(cyclestr)
        qdate = self.editDate.date()
        ddate = date(qdate.year(), qdate.month(), qdate.day())
        vdatestr = self.comboDate.currentText()
        vdate = PCycle.get_vdate_from_str(cycle, vdatestr)
        desc = self.editComment.text()
        return [oid, amount, income, cat, trig, over, cat_id, trig_id, over_id, cycle, ddate, vdatestr, desc]
        #return [oid, amount, income, cat, trig, over, cat_id, trig_id, over_id, ptype, cyclestr, ddate, vdatestr, desc]

    def addPrediction(self):
        aList = self.list_from_fields(0)
        pred = Prediction(self.db)
        pred.set_with_list(aList)
        self.db.add_prediction(pred)
        self.futures = self.db.get_next_three_months(self.today)
        self.doBalances(self.starting_balance)
        self.refresh(False)
    
    def catChanged(self):
        cat = self.comboCat.currentText()
        triggers = self.db.triggers_for_cat(cat)
        self.comboTrig.clear()
        for trig in triggers:
            self.comboTrig.addItem(trig.trig)
        
    def clearPrediction(self):
        self.editAmount.clear()
        self.chkboxIncome.setChecked(False)
        self.comboCat.clear()
        self.comboTrig.clear()
        self.comboCycle.clear()
        self.comboDate.clear()
        self.editDate.clear()
        self.editComment.clear()
        for cat in sorted(self.db.cat_to_oid.keys()):
            self.comboCat.addItem(cat)
            
        for trig in sorted(self.db.trig_to_oid.keys()):
            self.comboTrig.addItem(trig)
        
        self.cycleList = PCycle.get_cycle_list()
        self.comboCycle.addItems(self.cycleList)
    
    def deletePrediction(self):
        pent = self.futures[self.lastSelected]
        print(pent.asCategorizedStr(''))
        del self.futures[self.lastSelected]
        self.doBalances(self.starting_bal)
        self.refresh(False)
        

    def doBalances(self, starting_bal):
        self.balances = []
        self.starting_bal = starting_bal
        running = starting_bal
        self.balances.append(starting_bal)  #we should only do this if not showing past
        for ent in self.futures:
            running += ent.amount.value
            self.balances.append(running)
        

    def get_future_data(self, today, starting_bal):
        """This function used the predictions to produce three months of predicted future
           entries. today is the starting day or the period and starting_bal is the account
           balance as of today. """
        self.futures = self.db.get_next_three_months(today)
        
        self.doBalances(starting_bal)
            
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
        
            ctype = pred.cycle.ctype
            cstr = Cycles.inv[pred.cycle.ctype]
            self.comboCycle.setCurrentText(cstr) 
            #set comboCycle with the cycle type
            self.editDate.hide()
            self.comboDate.hide()
            if cstr == 'Monthly':
                dom = []
                for d in range(1, 31):
                    dom.append(str(d))
                self.comboDate.show()
                self.comboDate.addItems(dom)
                self.comboDate.setCurrentText(str(pred.cycle.vdate))
    
            elif cstr == 'Weekly':
                self.comboDate.addItems(DaysOfWeek.keys())
                self.comboDate.show()
                self.comboDate.setCurrentText(DaysOfWeek.inv[pred.cycle.vdate])
            elif cstr == 'Quarterly' or cstr == 'Annual' or cstr == 'BiWeekly' or cstr == 'Adhoc':
                self.editDate.setDate(pent.date)
                self.editDate.show()
            
            self.editComment.setText(pred.desc)
        
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
        

    def refresh(self, first_time):
        self.scene.clear()
        self.all_items = self.entries + self.futures
        self.nItems = len(self.all_items)

        max_bal = max(self.balances)  #dependant on doBalances
        min_bal = min(self.balances)

        self.showRects(1)
        scenewidth = (len(self.entries) + len(self.futures)) * XINC  #TODO with only a few predictions, this makes a narrow graph.
        sceneYmax = round((max_bal/100), -2)
        sceneYmin = round((min_bal/100), -2)
        self.showRects(2)
        viewrect = self.graphicsView.rect()
        
        pen = QPen(Qt.black)
        pen.setWidth(0)
        
        font = QFont()
        font.setPixelSize(16)
        
        i = j = 0
        self.listWidget.clear()
        
        for i in range(0, len(self.entries)-1):
            self.scene.addLine( QLineF( i * XINC, self.balances[i]/100, (i+1) * XINC, self.balances[i+1]/100), pen)
            self.listWidget.addItem(self.entries[i].asCategorizedStr(''))
            
        pen.setColor(Qt.red)

        for j in range(0, len(self.futures)-1):
            self.scene.addLine( QLineF( (i+j) * XINC, self.balances[i+j]/100, (i+j+1) * XINC, self.balances[i+j+1]/100), pen)
            self.listWidget.addItem(self.futures[i+j].asCategorizedStr(''))
            
        pen.setColor(Qt.black)
        
        for liney in range(int(sceneYmin), int(sceneYmax+100), 200):
            self.scene.addLine(QLineF(0.0, liney, scenewidth, liney), pen)
            myText = self.scene.addText(str(liney), font)
            myText.moveBy(20, liney+100)
            myText.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        
        
        self.showRects(4)
        if first_time:
            self.graphicsView.scale(1.57, -.081) 
        
        self.scene.setSceneRect(QRectF(QPointF(0, sceneYmin), QPointF(scenewidth, sceneYmax)))
        self.graphicsView.setScene(self.scene)
        self.setSelectionAt(0)      
        self.show()
        self.showRects(5)
        
    def resizeGraph(self, size):
        width = size.width()
        height = size.height()
        self.graphicsView.resize(QSize(width-40, height-40))
        self.showRects(6)
        
#        rect = QRectF(0, 0, width, height)
        self.graphicsView.fitInView(self.scene.sceneRect())
        self.showRects(7)

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

    def updatePrediction(self):
        #TODO Do I want this to update the original prediction record 
        # or just this projected entry.
        aList = self.list_from_fields(0)
        pent = self.futures[self.lastSelected]
        pent.amount = Money.from_str(self.editAmount.text())
        pred = Prediction(self.db)
        pred.set_with_list(aList)
        self.db.update_prediction(aList)
        self.futures = self.db.get_next_three_months(self.today)
        self.doBalances(self.starting_bal)
        self.refresh(False)
    
        #pred = Prediction(self.db)
        #pred.set_with_list(aList)
        #self.db.add_prediction(pred)
        #self.futures = self.db.get_next_three_months(self.today)
        #self.doBalances(self.starting_balance)
        #self.refresh(False)    

#Deprecated below this line ====================================
    def displayRangeAt(self, selected, before, after):  #deprecated
        assert(False)
        if index < 0 or index >= (len(self.entries) + len(self.futures)):
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
            self.listWidget.addItem(pent.asCategorizedStr(''))
          
        self.listWidget.setCurrentRow(10)
        
    def get_past_data(self, today, starting_balance):  # deprecated
        assert(False)
        self.entries = self.db.get_last_three_months(today)
        reversed_entries = sorted(self.entries, key=lambda ent: ent.date.isoformat(), reverse=True)        
        self.running = starting_balance
        self.balances.append(self.running)

        for ent in reversed_entries:
            self.running -= ent.amount.value
            self.balances.append(self.running)
            
        self.balances.reverse()
        
