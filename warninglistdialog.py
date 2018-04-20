from PyQt5.QtWidgets import (QDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
import PyQt5.QtGui
from warninglistdlg_auto import Ui_warninglistdlg

class WarningListDialog(QDialog, Ui_warninglistdlg):
    
    def __init__(self, msg, affected_items, sort):
        super(WarningListDialog, self).__init__()
        
        if len(affected_items) == 0:
            self.reply = True
            return
        self.setupUi(self)
        self.reply = False
        self.edtWarning.setPlainText(msg)
        self.listAffected.setSortingEnabled(sort)
        for l_item in affected_items:
            self.listAffected.addItem(l_item)        

        self.btnProceed.clicked.connect(lambda: self.proceed())
        self.btnCancel.clicked.connect(lambda: self.cancel())
        
        self.exec_()
        
    def proceed(self):
        self.reply = True
        self.close()
        return True
    
    def cancel(self):
        self.reply = False
        self.close()
        return False
    