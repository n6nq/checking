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
        self.headers = ['Name', 'Category', 'Trigger', 'Override', 'cat_id', 'trig_id', 'over_id', 'Type', 'Cycle', 'Date', 'Comment']
        
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
        list_data = sorted(self.db.get_all_predictions(), key=lambda pred: pred.name)
        self.set_list_model(list_data)

        # Setup sort combos#oid,name,cat,trig,over,cat_id,trig_id,over_id,p_type,cycle,pdate,comment
        self.sortName.activated.connect(lambda: self.new_name_filter())
        self.sortName.addItems(['Ascend', 'Descend'])

        self.sortCategory.activated.connect(lambda: self.new_category_filter())
        self.sortCategory.addItems(['Ascend', 'Descend'])
        for cat in sorted(self.db.cat_to_oid.keys()):
            self.sortCategory.addItem(cat)

        self.sortTrigger.activated.connect(lambda: self.new_trigger_filter())
        self.sortTrigger.addItems(['Ascend', 'Descend'])

        self.sortOverride.activated.connect(lambda: self.new_override_filter())
        self.sortOverride.addItems(['Ascend', 'Descend'])

        self.sortType.activated.connect(lambda: self.new_type_filter())
        self.sortType.addItems(['Ascend', 'Descend'])

        self.sortCycle.activated.connect(lambda: self.new_cycle_filter())
        self.sortCycle.addItems(['Ascend', 'Descend'])

        self.sortDate.activated.connect(lambda: self.new_date_filter())
        self.sortDate.addItems(['Ascend', 'Descend'])

        self.sortComment.activated.connect(lambda: self.new_comment_filter())
        self.sortComment.addItems(['Ascend', 'Descend'])

        form = QDataWidgetMapper()
        form.addMapping(self.editName, 0)
        self.exec_()
        
    def  new_category_filter(self):
        cat = self.sortCategory.currentText()
        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_predictions(), key=lambda ent: ent.get_category())
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_predictions(), key=lambda ent: ent.get_category(), reverse=True)
        else:
            filtered = sorted(self.db.get_all_predictions_with_cat(cat), key=lambda ent: ent.asCategorizedStr())
            
        self.set_list_model(filtered)
        self.show()
    
    def  new_comment_filter(self):
        pass
    
    def  new_cycle_filter(self):
        pass
    
    def  new_date_filter(self):
        pass
        
    def new_name_filter(self):
        pass
    
    def  new_override_filter(self):
        pass
    
    def  new_trigger_filter(self):
        pass
    
    def  new_type_filter(self):
        pass
    
    def set_list_model(self, listOfPredictions):
        self.table_model = MyTableModel(listOfPredictions, self.predictionsView, self.db)
        self.predictionsView.setModel(self.table_model)
    