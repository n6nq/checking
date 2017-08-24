#imports
import sys
import os
# get the Qt files
import PyQt5
from PyQt5.QtWidgets import *
import database
import datetime
from enum import Enum

# get the window
import mainwindow_auto
from checkfiledialog import CheckFileDialog
import readcheckfile_auto

# create class for Raspberry Pi GUI (currently Windows PC only)
########################################################################
class DateState(Enum):
    START = 0
    GOT_FIRST = 1
    GOT_SECOND = 2

class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    """"""

    # Date filter dictionary
    dateFilterMap = {'Ascend': 'A', 'Descend': 'D', 'Find': 'F', 'Range': 'R','Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, \
                     'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12, \
                     'ThisY': 'T', 'LastY': 'L'}


    # access variables inside the UI's file
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        # Setup calenders
        self.calendar1.hide()
        self.calendar2.hide()
        self.calendar1.clicked.connect(lambda: self.select_first_date())
        self.calendar2.clicked.connect(lambda: self.select_second_date())
        self.date_in_state = DateState.START
        self.got_first_date = False
        self.got_second_date = False
        
        # Setup the database
        curr = os.getcwd()
        self.db = database.Database(curr+'\\checking')

        # Setup the buttons
        self.btnOn.clicked.connect(lambda: self.pressedOnButton())
        self.btnReadFile.clicked.connect(lambda: self.pressedReadCheckFileButton())
        
        # Setup the entry list
        self.search_filter = 'All'        
        for ent in sorted(self.db.get_all_entries(self.search_filter), key=lambda ent: ent.asCategorizedStr()):
            self.listEntries.addItem(ent.asCategorizedStr())
            
        # Setup the Category combobox
        self.cbCategory.activated.connect(lambda: self.new_category_filter())
        self.cbCategory.addItems(['Ascend', 'Descend'])
        for cat in sorted(self.db.categories):
            self.cbCategory.addItem(cat)
        
        # Setup the Date combobox
        self.cbDate.activated.connect(lambda: self.new_date_filter())
        for filtStr in self.dateFilterMap.keys():
            self.cbDate.addItem(filtStr)

        # Setup search scope combobox
        self.cbSearchIn.activated.connect(lambda: self.new_search_filter())
        self.cbSearchIn.addItems(('All', 'Results'))

    def new_calender_filter(self):
        self.calendar1.hide()
        self.calendar2.hide()
        self.listEntries.clear()

        filtered = sorted(self.db.get_all_entries_with_date_range(self.search_filter, self.first_date, 
                          self.second_date), key=lambda ent: ent.asCategorizedStr())
            
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())

        self.got_first_date = self.got_second_date = False
        
    def new_category_filter(self):
        cat = self.cbCategory.currentText()
        self.listEntries.clear()

        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_filter), key=lambda ent: ent.get_category())
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_filter), key=lambda ent: ent.get_category(), reverse=True)
        else:
            filtered = sorted(self.db.get_all_entries_with_cat(self.search_filter, cat), key=lambda ent: ent.asCategorizedStr())
            
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())

    def new_date_filter(self):
        self.date_choice = self.cbDate.currentText()
        
        if self.date_choice == 'Find':
            self.calendar1.show()
            return
        elif self.date_choice == 'Range':
            self.calendar1.show()
            self.calendar2.show()
            return
        elif self.date_choice == 'Ascend':
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_filter, self.first_date, 
                            self.second_date), key=lambda ent: ent.asCategorizedStr())
        elif self.date_choice == 'Descend':
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_filter, self.first_date, 
                            self.second_date), key=lambda ent: ent.asCategorizedStr())
        else:
            if self.date_choice in self.dateFilterMap:
                month = self.dateFilterMap[self.date_choice]
                today = datetime.date.today()
                if month > today.month:
                    today.year -= 1
                self.first_date = datetime.date(today.year, month, 1)
                self.second_date = datetime.date(today.year, month+1, 1) - datetime.timedelta(days=1)
                filtered = sorted(self.db.get_all_entries_with_date_range(self.search_filter, self.first_date, 
                                    self.second_date), key=lambda ent: ent.asCategorizedStr())

            for ent in filtered:
                self.listEntries.addItem(ent.asCategorizedStr())
                
    def new_search_filter(self):
        self.search_filter = self.cbSearchIn.currentText()
        
    def pressedOnButton(self):
        print ("Pressed On!")
        for i in range(1, 11):
            self.listCategorized.addItem("Number %d" % i)
        
    def pressedReadCheckFileButton(self):
        print ("Pressed ReadCheckFile")
        
        readIt = CheckFileDialog(self.db)
        print(readIt.cf)
        
    def select_first_date(self):
        qdate = self.calendar1.selectedDate()
        self.first_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.got_first_date = True
        if self.date_choice == 'Find':
            self.got_second_date = True
            self.second_date = self.first_date
            self.new_calender_filter()
        if self.date_choice == 'Range' and self.got_second_date:
            self.new_calender_filter()
                
    def select_second_date(self):
        qdate = self.calendar2.selectedDate()
        self.second_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.got_second_date = True
        if self.got_first_date and self.date_choice == 'Range':
            self.new_calender_filter()
            
        
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
        
        
        
    
    