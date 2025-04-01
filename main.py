#imports
import sys
import os
# get the Qt files
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import index
import database
import datetime
from enum import Enum
# get the window
import mainwindow_auto
import chart_window_auto
from what_if_main import WhatIfMain
from checkfiledialog import CheckFileDialog
#from charttestdialog import ChartTestDialog
from managepredictionsdialog import ManagePredictionsDialog

import readcheckfile_auto
from entry import Entry
from money import Money
import common_ui

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
 
    def data(self, modelindex, role): 
        if modelindex.isValid() and role == Qt.DisplayRole:
            ent = self.listdata[modelindex.row()]
            if type(ent) is Entry:
                return QVariant(ent.asCategorizedStr(''))
            elif type(ent) is tuple:
                astr = ''
                for field in ent:
                    if type(field) is str:
                        astr += field+'\t'
                    else:
                        astr += 'what\t'
                return QVariant(astr)
        else: 
            return QVariant()

    def entryAt(self, modelindex):
        return self.listdata[modelindex.row()]
    
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    """ The main window of the checking app"""

    # access variables inside the UI's file
    def __init__(self):
                
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.PredDlg = None
    
        self.dbname = '\\checking'
             
        # Setup calenders
        self.default_dates()
        self.calendar1.hide()
        self.calendar2.hide()
        self.calendar1.clicked.connect(lambda: self.select_first_date())
        self.calendar2.clicked.connect(lambda: self.select_second_date())
        self.date_in_state = DateState.START
        self.got_first_date = False     # these signify where the user is in the process of entering a date range
        self.got_second_date = False
        
        # Setup the database
        curr = os.getcwd()
        self.db = database.DB(curr+self.dbname)

        # Setup the button
        self.btnChart.clicked.connect(lambda: self.pressedChartBtn())
        self.btnReadFile.clicked.connect(lambda: self.pressedReadCheckFileButton())
        self.btnMngPredict.clicked.connect(lambda: self.pressedManagePredictionsButton())
        self.btnBackup.clicked.connect(lambda: self.pressedBackupButton())
        self.btnCleanDB.clicked.connect(lambda: self.pressedCleanDB())
        self.btnListToFile.clicked.connect(lambda: self.pressedListToFile())

        # Setup the entry list
        self.search_choice = common_ui.all_results[0]  #'All' Start with 'All' searching
        list_data = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.asCategorizedStr(''))
        self.set_list_model(list_data)
        self.listEntries.customContextMenuRequested.connect(lambda: self.entryPopUpMenuHndlr(self.listEntries))
        self.listEntries.pressed.connect(lambda index:  self.mousePressed(index))
        self.selectedEntry = None
        self.createPopUpActions()
        
        # Setup the Category combobox
        self.cbCategory.activated.connect(lambda: self.new_category_filter())
        self.cbCategory.addItems(common_ui.ascend_descend)
        for cat in sorted(self.db.cat_to_oid.keys()):
            self.cbCategory.addItem(cat)
        
        # Setup the Date combobox
        self.cbDate.activated.connect(lambda: self.new_date_filter())
        for filtStr in common_ui.dateFilterMap.keys():
            self.cbDate.addItem(filtStr)

        # Setup Amount combo
        # labels are 'Ascend', 'Descend', 'Find', '>100', '<100', 'Deposit'
        self.cbAmount.activated.connect(lambda: self.new_amount_filter())
        self.cbAmount.addItems(common_ui.amount_sort)

        # Setup check number combo box
        self.cbCheckNum.activated.connect(lambda: self.new_checknum_filter())
        self.cbCheckNum.addItems(common_ui.ascend_descend_find)
        
        # Setup description combo box
        self.cbDescription.activated.connect(lambda: self.new_description_filter())
        self.cbDescription.addItems(common_ui.ascend_descend_find)
        
        # Setup search scope combobox 
        self.cbSearchIn.activated.connect(lambda: self.new_search_filter())
        self.cbSearchIn.addItems(common_ui.all_results)

        # Setup group by combo box
        self.cbGroupBy.activated.connect(lambda: self.new_group_by_filter())
        self.cbGroupBy.addItems(common_ui.groupby_labels)
        self.show()

    def default_dates(self):
        self.second_date = datetime.date.today()
        self.first_date = self.second_date - datetime.timedelta(days=365 * 5)
        
    def mousePressed(self, modelindex):
        self.selectedRow = modelindex.row()
        self.selectedEntry = self.list_model.entryAt(modelindex)
        
    def entryPopUpMenuHndlr(self, entryList):
        menu = QMenu(self)
        cat_menu = QMenu(menu)
        cat_menu.setTitle('NewCat')
        
        selectedIndex = entryList.currentIndex().row()
        #self.list_data
        #if len(newCatList) == 0:
        #    str = 'None'
        #else:
        #    str = newCatList[0].text()
        
        #self.NewCatAct.setText(str)
        actions = []
        for cat in sorted(self.db.get_all_cats()):
            newAct = QAction(cat)
            #newAct.triggered.connect(self.NewCatActionFunc)
            actions.append(QAction(cat))
            #newAct.setShortcut()
            #newAct.setStatusTip('Change entries category to {}'.format(cat));
        
        cat_menu.addActions(actions)
        cat_menu.triggered.connect(self.NewCatActionFunc)
        menu.addAction(self.NewPredAct)
        menu.addMenu(cat_menu)
        menu.addAction(self.NoneCatAct)
        
        for modelindex in entryList.selectedIndexes():
            index = modelindex.row()
            selectedEnt = self.list_model.listdata[index]
        
        #QStringList list;
        #foreach(const QModelIndex &index, 
        #        ui->listView->selectionModel()->selectedIndexes())
        #    list.append(model->itemFromIndex(index)->text());        
        #selectedEntryStr = entryList.currentItem().text()
        #self.newCatStr = str
        #self.selectedEntry = self.cf.find(selectedEntryStr)
        #menu.addAction(copyAct)
        #menu.addAction(pasteAct)
        menu.show()
        what = menu.exec_(PyQt5.QtGui.QCursor.pos())
    
    def createPopUpActions(self):
        self.NewCatAct = QAction("New&Cat")
        self.NewPredAct = QAction("New &Pred")
        self.NoneCatAct = QAction("&None")
        #newAct->setShortcuts(QKeySequence::New);
        self.NewCatAct.setStatusTip("Set entry to this category")
        self.NewPredAct.setStatusTip("Use this entry to make a new Prediction")
        self.NoneCatAct.setStatusTip("Set entry category to None")
        self.NewCatAct.triggered.connect(lambda act: self.NewCatActionFunc(act))
        self.NewPredAct.triggered.connect(lambda: self.NewPredActionFunc())
        self.NoneCatAct.triggered.connect(lambda: self.NoneCatActionFunc())
    
    def new_amount_filter(self):
        choice = self.cbAmount.currentText()
        labels = common_ui.amount_sort
        if choice == labels[0]:     #'Ascend'
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.amount.value)
        elif choice == labels[1]:  #'Descend'
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.amount.value, reverse=True)
        elif choice == labels[2]:  #'Find'
            op = database.CompareOps.MONEY_EQUALS
            value = QInputDialog.getText(self, 'Amount to search for:', 'Amount:')
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value[0]), key=lambda ent: ent.amount.value)
        elif choice == labels[3]:  #'>100'
            op = database.CompareOps.MONEY_MORE_THAN
            value = '100.00'
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value), key=lambda ent: ent.amount.value, reverse=True)
        elif choice == labels[4]:  #'<100'
            op = database.CompareOps.MONEY_LESS_THAN
            value = '100.00'
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value), key=lambda ent: ent.amount.value, reverse=True)
        elif choice == labels[5]:  #'Deposit'
            op = database.CompareOps.MONEY_MORE_THAN
            value = 0
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, value), key=lambda ent: ent.amount.value, reverse=True)
        else:
            return

        self.set_list_model(filtered)

        
    def new_checknum_filter(self):
        choice = self.cbCheckNum.currentText()
        labels = common_ui.ascend_descend_find
        if choice == labels[0]:  #'Ascend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.checknum)
        elif choice == labels[1]:  #'Descend':
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.checknum, reverse=True)
        elif choice == labels[2]:  #'Find'
            op = database.CompareOps.CHECKNUM_EQUALS
            value = QInputDialog.getText(self, 'Check Number to search for:', 'Check Number:')
            if value[0] == '' or value[0] == None:
                return
            filtered = sorted(self.db.get_all_entries_meeting(self.search_choice, op, int(value[0])), key=lambda ent: ent.checknum)
        else:    
            return
        self.set_list_model(filtered)

    def new_calender_filter(self):
        self.calendar1.hide()
        self.calendar2.hide()
        #TODO: This sorted by date rather than by asStr of the ent.
        filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                          self.second_date), key=lambda ent: ent.date.strftime('%m-%d-%Y'))
        
        self.set_list_model(filtered)
        #self.listEntries.clear()
        #for ent in filtered:
            #self.listEntries.addItem(ent.asCategorizedStr(''))

        self.got_first_date = self.got_second_date = False
        
    def new_category_filter(self):
        cat = self.cbCategory.currentText()
        #self.set_search_filter(common_ui.all_results[0])  #'All'   TODO removed for search experiment
        labels = common_ui.ascend_descend
        if cat == labels[0]:  #'Ascend'
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.get_category())
        elif cat == labels[1]:  #'Descend'
            filtered = sorted(self.db.get_all_entries(self.search_choice), key=lambda ent: ent.get_category(), reverse=True)
        else:
            filtered = sorted(self.db.get_all_entries_with_cat(self.search_choice, cat), key=lambda ent: ent.asCategorizedStr(''))
            
        self.set_list_model(filtered)
        #self.set_search_filter(common_ui.all_results[1])  #'Results'  TODO removed for search experiment
        self.show()
        
    def new_date_filter(self):
        self.default_dates()
        today = datetime.date.today()
        self.date_choice = self.cbDate.currentText()
        labels = list(common_ui.dateFilterMap.keys())        #Ascend, Descend, Find, Range, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec, ThisY, LastY        
        if self.date_choice == labels[2]:  #'Find'
            self.calendar1.show()
            return
        elif self.date_choice == labels[3]:  #'Range'
            self.calendar1.show()
            self.calendar2.show()
            return
        elif self.date_choice == labels[0]:  #'Ascend'
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat())
        elif self.date_choice == labels[1]:  #'Descend'
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat(), reverse=True)
        elif self.date_choice == labels[16]:  #'ThisY'
            self.first_date = datetime.date(today.year, 1, 1)
            self.second_date = datetime.date(today.year, 12, 31)
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat())
        elif self.date_choice == labels[17]:  #'LastY'
            self.first_date = datetime.date(today.year - 1, 1, 1)
            self.second_date = datetime.date(today.year - 1, 12, 31)
            filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                            self.second_date), key=lambda ent: ent.date.isoformat())
        else:
            if self.date_choice in common_ui.dateFilterMap:
                days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                month = common_ui.dateFilterMap[self.date_choice]
                today = datetime.date.today()
                year = today.year
                if month > today.month:
                    year -= 1
                    
                self.first_date = datetime.date(year, month, 1)
                
                self.second_date = datetime.date(year, month, days[month])
                
                filtered = sorted(self.db.get_all_entries_with_date_range(self.search_choice, self.first_date, 
                                    self.second_date), key=lambda ent: ent.date.strftime('%m-%d-%Y'))
        self.set_list_model(filtered)

    def new_description_filter(self):
        choice = self.cbDescription.currentText()
        labels = common_ui.ascend_descend_find
        if choice == labels[0]:  #'Ascend'
            all_entries = self.db.get_all_entries(self.search_choice)
            filtered = sorted(all_entries, key=lambda ent: ent.desc)
        elif choice == labels[1]:  #'Descend'
            all_entries = self.db.get_all_entries(self.search_choice)
            #filtered = sorted(all_entries, key=lambda ent: ent.desc)
            filtered = sorted(all_entries, key=lambda ent: ent.desc, reverse=True)
        elif choice == labels[2]:  #'Find'
            op = database.CompareOps.SEARCH_DESC
            value = QInputDialog.getText(self, 'String to search for:', 'String:')
            meeting = self.db.get_all_entries_meeting(self.search_choice, op, value[0])
            filtered = sorted(meeting, key=lambda ent: ent.checknum)
        else:    
            return

        self.set_list_model(filtered)        
  
    def new_group_by_filter(self):
        """Display totals, grouping in different ways. For now we'll do:
        None = Normal check by check Display
        MonthByCat = Group by month first and then by Category
        CatByMonth = Group by Category first and then by month
        """
        choice = self.cbGroupBy.currentText()
        #'None', 'MonthByCat', 'CatByMonth'
        labels = common_ui.groupby_labels
        if choice == labels[1]:  #'MonthByCat':
            filtered = self.db.get_month_by_cat()
        elif choice == labels[2]:  #'CatByMonth'
            filtered = self.db.get_cat_by_month()
        else:
            return
        for i in range(len(filtered)):
            #"select strftime('%Y',sdate) ym, category, trig_id, over_id, sum(abs(amount*1.0))/100, count(*), (sum(abs(amount*1.0))/100)/count(*) from Entries group by ym, category, trig_id, over_id order by ym, category, trig_id, over_id"
            row = filtered[i]
            value = Money.from_number(row[4])
            filtered[i] = (row[0], row[1], row[2], row[3], str(row[4]), str(row[5]), str(row[6]))  #TODO
            #filtered[i] = (row[0], row[1], row[2], row[3], value.as_str())  #TODO
        self.set_list_model(filtered)        
        
    def new_search_filter(self):
        self.search_choice = self.cbSearchIn.currentText()

    def set_search_filter(self, choice):
        self.cbSearchIn.setCurrentText(choice)
        self.search_choice = choice

    def pressedChartBtn(self):
        WhatIfMain(self.db)
        #ChartTestDialog(self.db)
    
    def pressedBackupButton(self):
        curr = os.getcwd()
        d = datetime.date.today()
        backup_name = curr+self.dbname+str(d.year)+'{:02d}{:02d}'.format(d.month, d.day)+'.db'
        self.db.backup(backup_name)

    def pressedCleanDB(self):
        self.db.cleanup()

    def pressedListToFile(self):
        td = datetime.datetime.today()
        filename = 'list'+td.strftime('%Y%m%d_%H%M%S.txt')
        f = open(filename, 'w')
        lm = self.list_model.listdata
        for ent in lm:
            row = ent
            if type(ent) is Entry:
                astr = ent.asCategorizedStr(',')+'\n'
                print(astr)
                f.write(astr)
            elif type(ent) is tuple:
                astr = ''
                for field in ent:
                    if type(field) is str:
                        astr += field+', '
                    else:
                        astr += 'what, '
                print(astr)
                f.write(astr+'\n')
            else: 
                print('What????\n')
                f.write('What????\n')
        f.close()

    def pressedReadCheckFileButton(self):
        readIt = CheckFileDialog(self.db)
        # refresh the lists
        self.cbCategory.setCurrentText(common_ui.ascend_descend[0])  #'Ascend'
        self.new_category_filter()
        
        #print(readIt.cf)
    
    def pressedManagePredictionsButton(self):
        okay = ManagePredictionsDialog(self.db)
        
    def select_first_date(self):
        qdate = self.calendar1.selectedDate()
        self.first_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.got_first_date = True
        labels = list(common_ui.dateFilterMap.keys())
        if self.date_choice == labels[2]:  #'Find'
            self.got_second_date = True
            self.second_date = self.first_date
            self.new_calender_filter()
        if self.date_choice == labels[3] and self.got_second_date:  #'Range'
            self.new_calender_filter()
                
    def select_second_date(self):
        qdate = self.calendar2.selectedDate()
        self.second_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        self.got_second_date = True
        if self.got_first_date and self.date_choice == list(common_ui.dateFilterMap.keys())[3]:  #'Range'
            self.new_calender_filter()
            
    def set_list_model(self, listOfEnts):
        self.list_model = MyListModel(listOfEnts, self.listEntries)
        self.listEntries.setModel(self.list_model)
    
    def canChangeEntry(self):
        if self.selectedEntry.locked == True:
            msgBox = QMessageBox()
            msgBox.setText("This entry is locked!")
            msgBox.setInformativeText("Do you want to change it anyway?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            retval = msgBox.exec()
            return retval
        else:
            return QMessageBox.Yes

    def NewCatActionFunc(self, action):
        if self.canChangeEntry() == QMessageBox.Yes:
            cat = action.text()                 #TODO we might need an unlock function
            cat_id = self.db.cat_to_oid[cat]
            self.selectedEntry.category = cat
            self.selectedEntry.cat_id = cat_id  #DONE set locked to true, clear trig and over???
            self.selectedEntry.trig_id = 0
            self.selectedEntry.over_id = 0
            self.selectedEntry.locked = True
            self.db.update_entry_cat_by_oid(cat, cat_id, self.selectedEntry.oid)
    
    def NewPredActionFunc(self):
        if self.PredDlg == None:
            self.PredDlg = ManagePredictionsDialog(self.db, self.selectedEntry)
        else:
            self.PredDlg.newPred(self.db, self.selectedEntry)

    def NoneCatActionFunc(self):
        if self.canChangeEntry() == QMessageBox.Yes:
            self.selectedEntry.category = 'None'  #DONE set cat_id, set locked = 0
            self.selectedEntry.cat_id = 1
            self.selectedEntry.trig_id = 0
            self.selectedEntry.over_id = 0
            self.selectedEntry.locked = False
        
       
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
        
        
        
    
    