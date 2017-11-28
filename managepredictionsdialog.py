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
        self.predictionsView
        form = QDataWidgetMapper()
        form.addMapping(self.edtName, 0)
        self.exec_()
    
    def set_list_model(self, listOfPredictions):
        self.table_model = MyTableModel(listOfPredictions, self.predictionsView, self.db)
        self.predictionsView.setModel(self.table_model)
    