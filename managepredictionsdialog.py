from PyQt5.QtWidgets import (QDialog, QMessageBox)
from managepredictions_auto import Ui_PredictionsDialog

class MyTableModel(QAbstractTableModel)

class ManagePredictionsDialog(QDialog, Ui_PredictionsDialog):
    
    def __init__(self, db):
        super(ManagePredictionsDialog, self).__init__()
        self.db = db
        
        self.setupUi(self)

        # add all the ui init
        list_data = sorted(self.db.get_all_predictions(), key=lambda pred: pred.name)
        self.set_list_model(list_data)
       
        self.exec_()
    
    def set_list_model(self, listOfPredictions):
        self.table_model = MyTableModel(listOfPredictions, self.predictionsView)
        self.listEntries.setModel(self.table_model)
    