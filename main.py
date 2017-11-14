#imports
import sys
import os
# get the Qt files
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


import database
import datetime
from enum import Enum
# get the window
import mainwindow_auto
import chart_test_auto
from checkfiledialog import CheckFileDialog
from charttestdialog import ChartTestDialog

import readcheckfile_auto
from entry import Entry
from money import Money

# create class for Raspberry Pi GUI (currently Windows PC only)
########################################################################
class DateState(Enum):
    START = 0
    GOT_FIRST = 1
    GOT_SECOND = 2

class MyListModel(QAbstractListModel): 
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QAbstractListModel.__init__(self, parent, *args) 
        self.listdata = datain
 
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid() and role == Qt.DisplayRole:
            return QVariant(self.listdata[index.row()])
        else: 
            return QVariant()


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
        list_data = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.asCategorizedStr())
        self.set_list_model(list_data)
        self.listEntries.customContextMenuRequested.connect(lambda: self.entryPopUpMenuHndlr(self.listEntries))
        
        self.createPopUpActions()
        
        # Setup the Category combobox
        self.cbCategory.activated.connect(lambda: self.new_category_filter())
        self.cbCategory.addItems(['Ascend', 'Descend'])
        for cat in sorted(self.db.cat_to_oid.keys()):
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

    def entryPopUpMenuHndlr(self, entryList):
        menu = QMenu(self)

        selectedIndex = entryList.currentIndex().row()
        #self.list_data
        #if len(newCatList) == 0:
        #    str = 'None'
        #else:
        #    str = newCatList[0].text()
        
        #self.NewCatAct.setText(str)
        cat_menu = menu.addMenu('NewCat')
        cat_menu.addAction(self.NewCatAction)
        menu.addAction(self.NoneCatAct)
        selectedEntryStr = whichList.currentItem().text()
        self.newCatStr = str
        self.selectedEntry = self.cf.find(selectedEntryStr)
        #menu.addAction(copyAct)
        #menu.addAction(pasteAct)
        menu.show()
        what = menu.exec_(PyQt5.QtGui.QCursor.pos())
        if (what):
            what.trigger()
    
    def createPopUpActions(self):
        pass
    
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

        self.set_list_model(filtered)
        #self.listEntries.clear()
        #for ent in filtered:
            #self.listEntries.addItem(ent.asCategorizedStr())
        
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
        self.set_list_model(filtered)
        #self.listEntries.clear()
        #for ent in filtered:
            #self.listEntries.addItem(ent.asCategorizedStr())

    def new_calender_filter(self):
        self.calendar1.hide()
        self.calendar2.hide()
        #TODO: This sorted by date rather than by asStr of the ent.
        filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                          self.second_date), key=lambda ent: ent.asCategorizedStr())
        
        self.set_list_model(filtered)
        #self.listEntries.clear()
        #for ent in filtered:
            #self.listEntries.addItem(ent.asCategorizedStr())

        self.got_first_date = self.got_second_date = False
        
    def new_category_filter(self):
        cat = self.cbCategory.currentText()

        if cat == 'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.get_category())
        elif cat == 'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.get_category(), reverse=True)
            #filtered = sorted(filtered, key=lambda ent: ent.get_category())
        else:
            filtered = sorted(self.db.get_all_entries_with_cat(self.search_choice, cat), key=lambda ent: ent.asCategorizedStr())
            
        #self.listEntries.clear()
        #for ent in filtered:
        #    self.listEntries.addItem(ent.asCategorizedStr())
        self.set_list_model(filtered)
        #list_data = []
        #for ent in filtered:
            #list_data.append(ent.asCategorizedStr())
        #lm = MyListModel(list_data, self.listEntries)
        #self.listEntries.setModel(lm)        
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
        self.set_list_model(filtered)
        #self.listEntries.clear()
        #for ent in filtered:
            #self.listEntries.addItem(ent.asCategorizedStr())
                

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

        self.set_list_model(filtered)        
        #self.listEntries.clear()
        #for ent in filtered:
            #self.listEntries.addItem(ent.asCategorizedStr())
        
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
        for i in range(len(filtered)):
            row = filtered[i]
            value = Money.from_number(row[2])
            filtered[i] = (row[0], row[1], value.as_str())
        self.set_list_model(filtered)        
        
    def new_search_filter(self):
        self.search_choice = self.cbSearchIn.currentText()
        
    def pressedOnButton(self):
        print ("Pressed On!")
        ChartTestDialog(self.db)
        
    def pressedReadCheckFileButton(self):
        print ("Pressed ReadCheckFile")
        
        readIt = CheckFileDialog(self.db)
        # refresh the lists
        self.cbCategory.setCurrentText('Ascend')
        self.new_category_filter()
        
        #print(readIt.cf)
        
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
            
    def set_list_model(self, listOfEnts):
        list_data = []
        for ent in listOfEnts:
            if type(ent) is Entry:
                list_data.append(ent.asCategorizedStr())
            elif type(ent) is tuple:
                list_data.append(ent[0]+'\t'+ent[1]+'\t'+str(ent[2]))
        lm = MyListModel(list_data, self.listEntries)
        self.listEntries.setModel(lm)        
    def NewCatAction(self):
        self.selectedEntry.category = self.newCatStr
        self.ResortList()
        
    def NoneCatAction(self):
        self.selectedEntry.category = None
        self.ResortList()
        
       
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
        
        
        
    
    