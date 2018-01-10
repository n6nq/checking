from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from managepredictions_auto import Ui_PredictionsDialog
from warninglistdialog import WarningListDialog
from datetime import date
from predicted import Prediction
from pcycle import * 
from money import Money
from enum import Enum

class MyTableModel(QAbstractTableModel):
    
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QAbstractTableModel.__init__(self, parent) 
        self.listdata = datain
        self.db = args[0]
        self.headers = Prediction.headers()
        
    def columnCount(self, arg0=None):
        return len(self.headers)
        
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata) 
    
    def data(self, modelindex, role): 
        if modelindex.isValid() and role == Qt.DisplayRole:
            pred = self.listdata[modelindex.row()]
            #amount = Money.from_number(pred.amount)
            strings = [pred.amount.as_str(), pred.cat, pred.trig, pred.over, pred.get_typestr(), pred.cycle.get_type_str(), pred.cycle.get_date_str(), pred.desc]
            index = modelindex.column()
            return strings[index]
        else: 
            return QVariant()

    def entryAt(self, modelindex):
        return self.listdata[modelindex.row()]
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section]

class Dirty(Enum):
    AMOUNT = 1
    CAT = 2
    TRIG = 3
    OVER = 4
    TYPE = 5
    CYCLE = 6
    DDATE = 7
    VDATE = 8
    COMMENT = 9
    CLEAR = 10
    
class ManagePredictionsDialog(QDialog, Ui_PredictionsDialog):
    
    def __init__(self, db):
        super(ManagePredictionsDialog, self).__init__()
        self.db = db
        
        self.setupUi(self)

        # add all the ui init
        list_data = sorted(self.db.get_all_predictions(), key=lambda pred: pred.trig)
        self.set_list_model(list_data)

        # Setup sort combos#oid,amount,cat,trig,over,cat_id,trig_id,over_id,p_type,cycle,pdate,comment
        self.sortAmount.activated.connect(lambda: self.new_amount_filter())
        ascendDescendList = ['Ascend', 'Descend']
        self.sortAmount.addItems(ascendDescendList)

        self.sortCategory.activated.connect(lambda: self.new_category_filter())
        self.sortCategory.addItems(ascendDescendList)
        for cat in sorted(self.db.cat_to_oid.keys()):
            self.sortCategory.addItem(cat)
            self.comboCat.addItem(cat)

        self.sortTrigger.activated.connect(lambda: self.new_trigger_filter())
        self.sortTrigger.addItems(ascendDescendList)
        for trig in sorted(self.db.trig_to_oid.keys()):
            self.sortTrigger.addItem(trig)
            self.comboTrig.addItem(trig)
        
        self.sortOverride.activated.connect(lambda: self.new_override_filter())
        self.sortOverride.addItems(ascendDescendList)
        self.comboOver.addItem('None')
        for over in sorted(self.db.over_to_oid.keys()):
            self.sortOverride.addItem(over)
            self.comboOver.addItem(over)

        self.sortType.activated.connect(lambda: self.new_type_filter())
        self.sortType.addItems(ascendDescendList)
        typeList = ['Bill', 'Prediction', 'Subscription', 'Monthly', 'Elective']
        self.sortType.addItems(typeList)
        self.comboType.addItems(typeList)
            
        self.sortCycle.activated.connect(lambda: self.new_cycle_filter())
        self.comboCycle.activated.connect(lambda: self.set_date_items())
        self.sortCycle.addItems(ascendDescendList)
        self.cycleList = ['Monthly', 'Weekly', 'Quarterly', 'Annual', 'BiWeekly', 'Adhoc']
        self.sortCycle.addItems(self.cycleList)
        self.comboCycle.addItems(self.cycleList)

        self.sortDate.activated.connect(lambda: self.new_date_filter())
        self.sortDate.addItems(ascendDescendList)
        #self.sortDate.addItems(['Day-of-month', 'Day-of-week', 'Day/month', 'Adhoc'])
        #self.editDate.addItems(['Day-of-month', 'Day-of-week', 'Day/month', 'Adhoc'])

        self.sortComment.activated.connect(lambda: self.new_comment_filter())
        self.sortComment.addItems(ascendDescendList)
        self.sortComment.addItem('Find')
        
        # Action button setups
        self.buttonAdd.clicked.connect(lambda: self.add_prediction())
        self.buttonUpdate.clicked.connect(lambda: self.update_prediction())
        self.buttonDelete.clicked.connect(lambda: self.delete_prediction())
        self.buttonClear.clicked.connect(lambda: self.clear_edit_fields())
        
        self.predictionsView.clicked.connect(lambda: self.select_prediction())
        
        # Get the dirty flags here
        self.editAmount.textEdited.connect(lambda: self.set_dirty(Dirty.AMOUNT))
        self.editComment.textEdited.connect(lambda: self.set_dirty(Dirty.COMMENT))
        self.editDate.dateChanged.connect(lambda: self.set_dirty(Dirty.DDATE))
        self.comboCat.currentIndexChanged.connect(lambda: self.set_dirty(Dirty.CAT))
        self.comboTrig.currentIndexChanged.connect(lambda: self.set_dirty(Dirty.TRIG))
        self.comboType.currentIndexChanged.connect(lambda: self.set_dirty(Dirty.TYPE))
        self.comboOver.currentIndexChanged.connect(lambda: self.set_dirty(Dirty.OVER))
        self.comboCycle.currentIndexChanged.connect(lambda: self.set_dirty(Dirty.CYCLE))
        self.dirty_flags = []
        self.exec_()
        
    def new_category_filter(self):
        cat = self.sortCategory.currentText()
        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_predictions(), key=lambda pred: pred.cat)
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_predictions(), key=lambda ent: pred.cat, reverse=True)
        else:
            filtered = sorted(self.db.get_all_predictions_with_cat(cat), key=lambda ent: ent.asCategorizedStr())
            
        self.set_list_model(filtered)
        self.show()
    
    def new_comment_filter(self):
        pass
    
    def new_cycle_filter(self):
        pass
    
    def new_date_filter(self):
        pass
        
    def new_amount_filter(self):
        pass
    
    def new_override_filter(self):
        pass
    
    def new_trigger_filter(self):
        pass
    
    def new_type_filter(self):
        pass
    
    def set_date_items(self):
        self.editDate.hide()
        self.editDate.setDate(date.today())
        self.comboDate.hide()
        self.comboDate.clear()
        cycle_choice = self.comboCycle.currentText()
        if cycle_choice == 'Monthly':
            day_list = [str(x) for x in range(1, 32)]
            self.comboDate.addItems(day_list)
            self.comboDate.show()
            return
        elif cycle_choice == 'Weekly':
            day_list = [DaysOfWeek.inv[1], DaysOfWeek.inv[2], DaysOfWeek.inv[3], DaysOfWeek.inv[4], DaysOfWeek.inv[5], DaysOfWeek.inv[6], DaysOfWeek.inv[7]]
            self.comboDate.addItems(day_list)
            self.comboDate.show()
            return
        elif cycle_choice == 'Quarterly':
            self.editDate.show()
            return
        elif cycle_choice == 'Annual':
            self.editDate.show()
            return
        elif cycle_choice == 'Bi-weekly':
            self.editDate.show()
            return
        elif cycle_choice == 'Adhoc':
            self.editDate.show()
            return
        else:
            print('What is '+cycle_choice+'?')
            # do something bad choice
        
    def set_list_model(self, listOfPredictions):
        self.table_model = MyTableModel(listOfPredictions, self.predictionsView, self.db)
        self.predictionsView.setModel(self.table_model)
        
    #----------------------------------------------------------------------
    def set_dirty(self, flag):
        """Set dirty flags for all add/update fields"""
        if flag == Dirty.CLEAR:
            self.dirty_flags = []
        elif flag not in self.dirty_flags:
            self.dirty_flags.append(flag)
        
    def add_prediction(self):
        amount = Money.from_str(self.editAmount.text())
        income = self.chkboxIncome.checkState()
        if income == 0:
            amount.negative()
        cat = self.comboCat.currentText()
        trig = self.comboTrig.currentText()
        over = self.comboOver.currentText()
        ptypestr = self.comboType.currentText()

        cyclestr = self.comboCycle.currentText()
        qdate = self.editDate.date()
        ddate = date(qdate.year(), qdate.month(), qdate.day())
        vdatestr = self.comboDate.currentText()
        #depr cycle = pred.get_cycle_from_str(cyclestr)
        #depr vdate = pred.get_vdate_from_str(cycle, vdatestr)
        
        desc = self.editComment.text()
        pred = Prediction(self.db)
        ptype = pred.get_ptype_from_str(ptypestr)
        pred.set_without_ids(amount, income, cat, trig, over, ptype, cyclestr, ddate, vdatestr, desc)

        # check current entries for effect of new trigger
        affected = self.db.find_all_with_trigger_or_override(trig, over)
        dl = WarningListDialog(
            "All entries listed below have the trigger string '"+trig+"' or the override string '"+over+"'.\n" + \
            "Similar entries will be potential matches to predictions when when new check files are read.", 
            affected)
        if dl.reply == True:
            self.db.add_prediction(pred)
            self.new_category_filter()
            #i = QListWidgetItem(self.trigger_str)
            #self.listTriggers.addItem(i)
            #self.listTriggers.setCurrentItem(i)
        
    def update_prediction(self):
        if len(self.dirty_flags) > 0:
            print(self.dirty_flags)
            
    def delete_prediction(self):
        pass
    
    def clear_edit_fields(self):
        self.editAmount.setText("00.00")
        self.comboCat.setEditText("")
        self.comboTrig.setEditText("")
        self.comboOver.setEditText("")
        self.comboType.setEditText("")
        self.comboCycle.setEditText("")
        self.comboDate.setEditText("")
        self.editDate.setDate(date.today())
        self.set_dirty(Dirty.CLEAR)
        self.editComment.setText("")
        self.update()

    def select_prediction(self):
        selection = self.predictionsView.selectionModel()
        indexes = selection.selectedIndexes()
        mi = indexes[0]
        self.clear_edit_fields()
        for col in range(0, self.table_model.columnCount()):
            new_mi = self.table_model.index(mi.row(), col)
            value = self.table_model.data(new_mi, Qt.DisplayRole)
            self.set_field(col, value)
        self.set_dirty(Dirty.CLEAR)
    
    def set_field(self, col, value):
        if col == 0:
            self.editAmount.setText(value)
            return
        elif col == 1:
            self.comboCat.setCurrentText(value)
            return
        elif col == 2:
            self.comboTrig.setCurrentText(value)
            return
        elif col == 3:
            self.comboOver.setCurrentText(value)
            return
        elif col == 4:
            self.comboType.setCurrentText(value)
            return
        elif col == 5:
            self.comboCycle.setCurrentText(value)
            return
        elif col == 6:
            mytype = type(value)
            if '-' in value:
                date = QDate.fromString(value, 'yyyy-M-d')
                self.editDate.setDate(date)
                self.editDate.show()
                self.comboDate.hide()
                return
            else:
                self.set_date_items()
                self.comboDate.setCurrentText(value)
                self.editDate.show()
                self.comboDate.hide()
                return
        elif col == 7:
            self.editComment.setText(value)
            return
        else:
            print('Bad column')
            return