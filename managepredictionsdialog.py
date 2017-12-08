from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from managepredictions_auto import Ui_PredictionsDialog
from warninglistdialog import WarningListDialog
from datetime import date
from predicted import Prediction, Cycle

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

            strings = [pred.name, pred.cat, pred.trig, pred.over, pred.get_typestr(), pred.get_cyclestr(), pred.get_datestr(), pred.comment]
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

class ManagePredictionsDialog(QDialog, Ui_PredictionsDialog):
    
    def __init__(self, db):
        super(ManagePredictionsDialog, self).__init__()
        self.db = db
        
        self.setupUi(self)

        # add all the ui init
        list_data = sorted(self.db.get_all_predictions(), key=lambda pred: pred.name)
        self.set_list_model(list_data)

        # Setup sort combos#oid,name,cat,trig,over,cat_id,trig_id,over_id,p_type,cycle,pdate,comment
        self.sortName.activated.connect(lambda: self.new_name_filter())
        ascendDescendList = ['Ascend', 'Descend']
        self.sortName.addItems(ascendDescendList)

        self.sortCategory.activated.connect(lambda: self.new_category_filter())
        self.sortCategory.addItems(ascendDescendList)
        for cat in sorted(self.db.cat_to_oid.keys()):
            self.sortCategory.addItem(cat)
            self.comboCat.addItem(cat)

        self.sortTrigger.activated.connect(lambda: self.new_trigger_filter())
        self.sortTrigger.addItems(ascendDescendList)

        self.sortOverride.activated.connect(lambda: self.new_override_filter())
        self.sortOverride.addItems(ascendDescendList)

        self.sortType.activated.connect(lambda: self.new_type_filter())
        self.sortType.addItems(ascendDescendList)
        typeList = ['Bill', 'Prediction', 'Subscription', 'Monthly', 'Elective']
        self.sortType.addItems(typeList)
        self.comboType.addItems(typeList)
            
        self.sortCycle.activated.connect(lambda: self.new_cycle_filter())
        self.comboCycle.activated.connect(lambda: self.set_date_items())
        self.sortCycle.addItems(ascendDescendList)
        self.cycleList = ['Monthly', 'Weekly', 'Quarterly', 'Annual', 'Bi-weekly', 'Adhoc']
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
        
        # setup the mapper
        self.mapper = QDataWidgetMapper(self)

        self.mapper.addMapping(self.editName, 0)
        self.mapper.addMapping(self.comboCat, 1)
        self.mapper.addMapping(self.editTrig, 2)
        self.mapper.addMapping(self.editOver, 3)
        self.mapper.addMapping(self.comboType, 4)
        self.mapper.addMapping(self.comboCycle, 5)
        self.mapper.addMapping(self.editDate, 6)
        self.mapper.addMapping(self.editComment, 7)
        self.exec_()
        
    def new_category_filter(self):
        cat = self.sortCategory.currentText()
        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_predictions(), key=lambda ent: ent.get_category())
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_predictions(), key=lambda ent: ent.get_category(), reverse=True)
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
        
    def new_name_filter(self):
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
            day_list = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
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
    def add_prediction(self):
        name = self.editName.text()
        cat = self.comboCat.currentText()
        trig = self.editTrig.text()
        over = self.editOver.text()
        ptypestr = self.comboType.currentText()
        cyclestr = self.comboCycle.currentText()
        qdate = self.editDate.date()
        ddate = date(qdate.year(), qdate.month(), qdate.day())
        vdate = self.comboDate.currentText()
        desc = self.editComment.text()
        pred = Prediction(self.db)
        ptype = pred.get_ptype_from_str(ptypestr)
        cycle = pred.get_cycle_from_str(cyclestr)
        if cycle in [Cycle.]
        pred.set_without_ids(name, cat, trig, over, ptype, cycle, ddate, vdate, desc)

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
        pass
    def delete_prediction(self):
        pass
    def clear_edit_fields(self):
        pass
    