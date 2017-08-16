#imports
import sys
import os
# get the Qt files
import PyQt5
from PyQt5.QtWidgets import *
import database

# get the window
import mainwindow_auto
from checkfiledialog import CheckFileDialog
import readcheckfile_auto

# create class for Raspberry Pi GUI
########################################################################
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    """"""

    # access variables inside the UI's file
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.btnOn.clicked.connect(lambda: self.pressedOnButton())
        self.btnReadFile.clicked.connect(lambda: self.pressedReadCheckFileButton())
        
        curr = os.getcwd()
        self.db = database.Database(curr+'\\checking')


        for ent in sorted(self.db.get_all_entries(), key=lambda ent: ent.asCategorizedStr()):
            self.listEntries.addItem(ent.asCategorizedStr())
            
        self.cbCategory.addItems(['Ascend', 'Descend'])
        for cat in sorted(self.db.categories):
            self.cbCategory.addItem(cat)
        
        self.cbCategory.currentTextChanged.connect(lambda: self.newCategoryFilter())
        
    def newCategoryFilter(self):
        cat = self.cbCategory.currentText()
        self.listEntries.clear()

        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_entries(), key=lambda ent: ent.get_category())
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_entries(), key=lambda ent: ent.get_category(), reverse=True)
        else:
            filtered = sorted(self.db.get_all_entries_with_cat(cat), key=lambda ent: ent.asCategorizedStr())
            
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())

    def pressedOnButton(self):
        print ("Pressed On!")
        for i in range(1, 11):
            self.listCategorized.addItem("Number %d" % i)
        
    def pressedReadCheckFileButton(self):
        print ("Pressed ReadCheckFile")
        
        readIt = CheckFileDialog(self.db)
        print(readIt.cf)
        
        
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
        
        
        
    
    