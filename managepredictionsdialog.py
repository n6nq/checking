from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from managepredictions_auto import Ui_PredictionsDialog

class MyTableModel(QAbstractTableModel):
    
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QAbstractTableModel.__init__(self, parent) 
        self.listdata = datain
        self.db = args[0]
        self.headers = ['Name', 'Category', 'Trigger', 'Override', 'Type', 'Cycle', 'Date', 'Comment']
        
    def columnCount(self, arg0=None):
        return self.db.get_predictions_column_count()
        
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata) 
    
    def data(self, modelindex, role): 
        if modelindex.isValid() and role == Qt.DisplayRole:
            ent = self.listdata[modelindex.row()]
            if type(ent) is Entry:
                return QVariant(ent.asCategorizedStr())
            elif type(ent) is tuple:
                return QVariant(ent[0]+'\t'+ent[1]+'\t'+str(ent[2]))
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
        list_data = sorted(self.db.get_all_predictions_no_ids(), key=lambda pred: pred.name)
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
        cycle_choice = self.comboCycle.currentText()
        if cycle_choice == 'Monthly':
            day_list = [x for x in range(1, 32)]
        elif cycle_choice == 'Weekly':
            pass
        elif cycle_choice == 'Quarterly':
            pass
        elif cycle_choice == 'Annual':
            pass
        elif cycle_choice == 'Bi-weekly':
            pass
        elif cycle_choice == 'Adhoc':
            pass
        else:
            pass
            # do something bad choice
        
    def set_list_model(self, listOfPredictions):
        self.table_model = MyTableModel(listOfPredictions, self.predictionsView, self.db)
        self.predictionsView.setModel(self.table_model)
    