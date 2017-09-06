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
        self.second_date = datetime.date.today()
        self.first_date = self.second_date - datetime.timedelta(days=365)
        self.calendar1.hide()
        self.calendar2.hide()
        self.calendar1.clicked.connect(lambda: self.select_first_date())
        self.calendar2.clicked.connect(lambda: self.select_second_date())
        self.date_in_state = DateState.START
        self.got_first_date = False     # these signify where the user is in the process of entering a date range
        self.got_second_date = False
        
        # Setup the database
        curr = os.getcwd()
        self.db = database.Database(curr+'\\checking')

        # Setup the buttons
        self.btnOn.clicked.connect(lambda: self.pressedOnButton())
        self.btnReadFile.clicked.connect(lambda: self.pressedReadCheckFileButton())
        
        # Setup the entry list
        self.search_choice = 'All'
        listCount = 0
        showing = 750
        for ent in sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.asCategorizedStr()):
            if listCount < showing:
                self.listEntries.addItem(ent.asCategorizedStr())
            listCount += 1    
        print('listCount= ' + str(listCount) +'showing='+str(showing))
        # Setup the Category combobox
        self.cbCategory.activated.connect(lambda: self.new_category_filter())
        self.cbCategory.addItems(['Ascend', 'Descend'])
        for cat in sorted(self.db.categories):
            self.cbCategory.addItem(cat)
        
        # Setup the Date combobox
        self.cbDate.activated.connect(lambda: self.new_date_filter())
        for filtStr in self.dateFilterMap.keys():
            self.cbDate.addItem(filtStr)
            
        # Setup Amount combo
        self.cbAmount.activated.connect(lambda: self.new_amount_filter())
        self.cbAmount.addItems(['Ascend', 'Descend', 'Find', '>100', 'Deposit'])

        # Setup check number combo box
        self.cbCheckNum.activated.connect(lambda: self.new_checknum_filter())
        self.cbCheckNum.addItems(['Ascend', 'Descend', 'Find'])
        
        # Setup description combo box
        self.cbDescription.activated.connect(lambda: self.new_description_filter())
        self.cbDescription.addItems(['Ascend', 'Descend', 'Find'])
        
        # Setup search scope combobox 
        self.cbSearchIn.activated.connect(lambda: self.new_search_filter())
        self.cbSearchIn.addItems(('All', 'Results'))

        # Setup group by combo box
        self.cbGroupBy.activated.connect(lambda: self.new_group_by_filter())
        self.cbGroupBy.addItems(('None', 'MonthByCat', 'CatByMonth'))
        self.show()
        
    def new_amount_filter(self):
        choice = self.cbAmount.currentText()
        if choice == 'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.amount.value)
        elif choice == 'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.amount.value, reverse=True)
        elif choice == 'Find':
            op = database.CompareOps.MONEY_EQUALS
            value = QInputDialog.getText(self, 'Amount to search for:', 'Amount:')
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value[0]), key=lambda ent: ent.amount.value)
        elif choice == '>100':
            op = database.CompareOps.MONEY_LESS_THAN
            value = '-100'
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value), key=lambda ent: ent.amount.value, reverse=True)
        elif choice == 'Deposit':
            op = database.CompareOps.MONEY_MORE_THAN
            value = '0'
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value), key=lambda ent: ent.amount.value, reverse=True)
        else:
            return

        self.listEntries.clear()
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())
        
    def new_checknum_filter(self):
        choice = self.cbCheckNum.currentText()
        if choice == 'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.checknum)
        elif choice == 'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.checknum, reverse=True)
        elif choice == 'Find':
            op = database.CompareOps.CHECKNUM_EQUALS
            value = QInputDialog.getText(self, 'Check Number to search for:', 'Check Number:')
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, int(value[0])), key=lambda ent: ent.checknum)
        else:    
            return

        self.listEntries.clear()
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())

    def new_calender_filter(self):
        self.calendar1.hide()
        self.calendar2.hide()

        filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                          self.second_date), key=lambda ent: ent.asCategorizedStr())
            
        self.listEntries.clear()
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())

        self.got_first_date = self.got_second_date = False
        
    def new_category_filter(self):
        cat = self.cbCategory.currentText()

        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.get_category())
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.get_category(), reverse=True)
        else:
            filtered = sorted(self.db.get_all_entries_with_cat(self.search_choice, cat), key=lambda ent: ent.asCategorizedStr())
            
        self.listEntries.clear()
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())
        self.show()
        
    def new_date_filter(self):
        today = datetime.date.today()
        self.date_choice = self.cbDate.currentText()
        
        if self.date_choice == 'Find':
            self.calendar1.show()
            return
        elif self.date_choice == 'Range':
            self.calendar1.show()
            self.calendar2.show()
            return
        elif self.date_choice == 'Ascend':
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat())
        elif self.date_choice == 'Descend':
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat(), reverse=True)
        elif self.date_choice == 'ThisY':
            self.first_date = datetime.date(today.year, 1, 1)
            self.second_date = datetime.date(today.year, 12, 31)
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat())
        elif self.date_choice == 'LastY':
            self.first_date = datetime.date(today.year - 1, 1, 1)
            self.second_date = datetime.date(today.year - 1, 12, 31)
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat())
        else:
            if self.date_choice in self.dateFilterMap:
                days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                month = self.dateFilterMap[self.date_choice]
                today = datetime.date.today()
                year = today.year
                if month > today.month:
                    year -= 1
                    
                self.first_date = datetime.date(year, month, 1)
                
                self.second_date = datetime.date(year, month, days[month])
                
                filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                                    self.second_date), key=lambda ent: ent.date.isoformat())
        self.listEntries.clear()
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())
                

    def new_description_filter(self):
        choice = self.cbDescription.currentText()
        if choice == 'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.desc)
        elif choice == 'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.desc, reverse=True)
        elif choice == 'Find':
            op = database.CompareOps.SEARCH_DESC
            value = QInputDialog.getText(self, 'String to search for:', 'String:')
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value[0]), key=lambda ent: ent.checknum)
        else:    
            return

        self.listEntries.clear()
        for ent in filtered:
            self.listEntries.addItem(ent.asCategorizedStr())
        
    def new_group_by_filter(self):
        """Display totals, grouping in different ways. For now we'll do:
        None = Normal check by check Display
        MonthByCat = Group by month first and then by Category
        CatByMonth = Group by Category first and then by month
        """
        choice = self.cbGroupBy.currentText()
        if choice == 'MonthByCat':
            filtered = self.db.get_month_by_cat()
        elif choice == 'CatByMonth':
            filtered = self.db.get_cat_by_month()
        else:
            return
        self.listEntries.clear()
        for row in filtered:
            self.listEntries.addItem(row[0]+'\t\t'+row[1]+'\t\t'+str(row[2]/100.0))
        
    def new_search_filter(self):
        self.search_choice = self.cbSearchIn.currentText()
        
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
    
        
        
        
    
    