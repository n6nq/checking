#imports
import sys
import os
# get the Qt files
import PyQt5
from PyQt5.QtWidgets import *
import database
import datetime

# get the window
import mainwindow_auto
from checkfiledialog import CheckFileDialog
import readcheckfile_auto

# create class for Raspberry Pi GUI (currently Windows PC only)
########################################################################
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    """"""

    # Date filter dictionary
    dateFilterMap = {'Ascend': 'A', 'Descend': 'D', 'Find': 'F', 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, \
                     'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12, \
                     'ThisY': 'T', 'LastY': 'L'}
    # access variables inside the UI's file
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Setup calender
        self.calendar.hide()
        self.calendar.clicked.connect(lambda: self.new_calender_filter())
        
        # Setup the database
        curr = os.getcwd()
        self.db = database.Database(curr+'\\checking')

        # Setup the buttons
        self.btnOn.clicked.connect(lambda: self.pressedOnButton())
        self.btnReadFile.clicked.connect(lambda: self.pressedReadCheckFileButton())
        
        # Setup the entry list
        for ent in sorted(self.db.get_all_entries(), key=lambda ent: ent.asCategorizedStr()):
            self.listEntries.addItem(ent.asCategorizedStr())
            
        # Setup the Category combobox
        self.cbCategory.activated.connect(lambda: self.new_category_filter())
        self.cbCategory.addItems(['Ascend', 'Descend'])
        for cat in sorted(self.db.categories):
            self.cbCategory.addItem(cat)
        
        # Setup the Date combobox
        self.cbDate.activated.connect(lambda: self.newDateFilter())
        for filtStr in self.dateFilterMap.keys():
            self.cbDate.addItem(filtStr)
           
    def new_calender_filter(self):
        qdate = self.calendar.selectedDate()
        self.search_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.calendar.hide()
        self.listEntries.clear()

        filtered = sorted(self.db.get_all_entries_with_date(self.search_date), key=lambda ent: ent.asCategorizedStr())
            
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())
    
    def new_category_filter(self):
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

    def newDateFilter(self):
        choice = self.cbDate.currentText()
        if choice == 'Find':
            self.calendar.show()
        pass
    
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
    
        
        
        
    
    