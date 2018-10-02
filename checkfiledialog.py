from PyQt5.QtWidgets import (QDialog, QMessageBox, QFileDialog, QMenu, QAction, QListWidgetItem)
import PyQt5.QtGui
from readcheckfile_auto import Ui_ReadCheckFileDialog
from managecategoriesdialog import ManageCategoriesDialog
import database
import accounts
import trigger
#from category import Category
import override
import check_file   #defines and handles files from the bank
import entry

class CheckFileDialog(QDialog, Ui_ReadCheckFileDialog):
    """CheckFileDialog -- This class provides the UI and code for reading .csv files from the
    bank. It provides automatic categorization and has facilities for defining new trigger strings
    and their associated categories.
    Member variables:
    db -- a reference to a single instance of the Database class, which provides all to our stored data.
    cf -- File. This is a file opened on the .csv file that is being imported.
    btnReadCheckFile -- Action button that triggers the file open dialog.
    listCategorized -- A list that contains entries that we found trigger strings in and
                       therefore set their categories.
    listUnCategorized -- A list that contains those entries that we recognized 
                        no trigger strings in and therefore could not categorize.
    edtSelectTrigger -- A text edit box, provides for selection of the string that will
                        became the trigger for the next created category.
    btnSetTrigger -- Action button that creates a new trigger, using the selected trigger string
                     and the selected category.
    btnSetCat -- Sets category of selected entry in uncategorized list to the category that is
                 selected in the category list. This is a manual category set. Most entries are
                 automatically categorized when the file is first read.
    edtNewCat -- An edit box for entry of new category names.
    btnAddCat -- Action button adds the current content of edtNewCat as a new catergory to the
                 category list and table.
    btnUnCat  -- Marks category of selected entry in the categorized list to 'None'. Repaints both
                 the categorized and uncategorized lists to show the move.
    btnAccept -- Merges the current state of the entries in the categorized list into the database
                 and clears the categorized list.
    btnCancel -- Closes this dialog without saving any of the new entries that were categorized. It
                 be the same as if you hadn't read this checkfile. It does not remove entries that have
                 already been accepted.
    btnManageCats -- Opens the Manage Categories dialog for modifying, deleting or creating new categories.
    Methods:
    setupUi
    """
    
    def __init__(self, db):
        super(CheckFileDialog, self).__init__()
        
        #self.db = accounts.Account('checking', db)
        #self.db.load()
        self.db = db
        self.db.clear_ncf_entries()
        self.cf = check_file.CheckFile(self.db)
        
        # Set up the user interface from QTDesigner.
        self.setupUi(self)

        # Setup button actions
        self.btnReadCheckFile.clicked.connect(lambda: self.ReadFileClickHndlr())
        self.listUnCategorized.clicked.connect(lambda: self.UnCategorizedClickHndlr())
        self.edtSelectTrigger.selectionChanged.connect(lambda: self.TriggerSelectedHndlr())
        self.btnSetTrigger.clicked.connect(lambda: self.SetTriggerHndlr())
        self.btnSetCat.clicked.connect(lambda: self.SetCatHndlr())
        self.edtNewCat.selectionChanged.connect(lambda: self.GetNewCatStrHndlr())
        self.btnUnCat.clicked.connect(lambda: self.UnCatHndlr())
        self.btnAddCat.clicked.connect(lambda: self.AddCategoryHndlr())
        self.listCategorized.customContextMenuRequested.connect(lambda: self.CategorizedPopUpHndlr(self, self.listCategorized))
        self.listUnCategorized.customContextMenuRequested.connect(lambda: self.CategorizedPopUpHndlr(self, self.listUnCategorized))
        self.btnAccept.clicked.connect(lambda: self.AcceptChanges())
        self.btnCancel.clicked.connect(lambda: self.RejectChanges())
        self.btnManageCats.clicked.connect(lambda: self.OpenManageCats())
        
        # Fill the categories list
        for cat, category in self.db.get_all_cats().items():
            self.listCategories.addItem(cat)

        # Retrieve any entries from th database that have not been categorized yet and add them to
        # the uncategorized list so will be considered for categorization with the new entries fromDesc
        # the checkfile that haven't been categorized yet.
        self.db.set_ncf_entries(self.db.get_all_entries_with_cat('All', 'None'))
        for ent in self.db.get_ncf_entries():
            self.listUnCategorized.addItem(ent.asNotCatStr())
        # Setup popup menu actions
        self.CreatePopupActions()
        
        #Setup varibles for dialog
        self.selectedTriggerStr = ''
        self.exec_()
        
        
    #---------- Event handlers ---------------------------
    def AcceptChanges(self):
        """Merges the current state of the entries in the categorized list into the database
           and clears the categorized list."""
        #print('Accepted')
        self.db.merge_ncf_entries()
        if len(self.db.ncf_entries) > 0:
            self.listCategorized.clear()
            return
        self.close()
        
        
    def AddCategoryHndlr(self):
        """The Add Cat button was pushed. If a string was entered, make a new
        category and update the category list."""
        catStr = self.edtNewCat.text()
        if self.db.add_cat(catStr):
            i = QListWidgetItem(catStr)
            self.listCategories.addItem(i)
            self.listCategories.setCurrentItem(i)
        else:
            self.edtNewCat.setText('')

    def CategorizedPopUpHndlr(self, event, whichList):
        """A right mouse click has happened in one of the Categorized list. If a Category
        has been selected in the Category list, then find the entry that was clicked on,
        set it's category to the selected one and then resort all the entries in the two
        Categorized list. The list where the click happened is passed in as whichList.
        This allows this code to function in either list with no list specific code."""
        menu = QMenu(self)
        newCatList = self.listCategories.selectedItems()
        if len(newCatList) == 0:
            str = 'None'
        else:
            str = newCatList[0].text()
        
        self.NewCatAct.setText(str)
        menu.addAction(self.NewCatAct)
        menu.addAction(self.NoneCatAct)
        if whichList.currentItem() == None:
            return
        selectedEntryStr = whichList.currentItem().text()
        self.newCatStr = str
        self.selectedEntry = self.cf.find(selectedEntryStr)
        #menu.addAction(copyAct)
        #menu.addAction(pasteAct)
        menu.show()
        what = menu.exec_(PyQt5.QtGui.QCursor.pos())
        if (what):
            what.trigger()
        pass
    
    def GetNewCatStrHndlr(self):
        """A new category string has been entered in the new category edit field.
        Get it and save in a dialog instance variable."""
        self.newCatStr = self.edtNewCat.selectedText()

    def OpenManageCats(self):
        """Open the Manage Categories dialog"""
        mc = ManageCategoriesDialog(self.db)
        self.ResortList()
        
    def ReadFileClickHndlr(self):
        """Opens the FileOpen dialog for file selection. Sets the fileName
           edit line to display the selected file. CCall the checkfile instance
           cf to read in the entries. The resulting Entry list is then sorted
           into the Categorized and UnCategorized lists"""
        fileName = QFileDialog.getOpenFileName(self,
                    'Check File', '.', 'Check file (*.csv)');
        self.filePathEdit.setText(fileName[0])
        self.show()
        
        self.cf.open(fileName[0])
        #iterate check file, disposing of dupes
        current = set(self.db.entries)
        new_checks = []
        dupes = []
        new_sorted = sorted(self.db.get_ncf_entries(), key=lambda ent: ent.date.isoformat())
        for check in new_sorted:
            print(check.asNotCatStr())
            if check in current:
                dupes.append(check)
            else:
                new_checks.append(check)
            
        self.db.set_ncf_entries(new_checks)
        #iterate remaining checks and load list widgets here
        for check in self.db.get_ncf_entries():
            if check.cat_id == 0 and check.category == 'None':
                self.listUnCategorized.addItem('\t'+check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())

    def RejectChanges(self):
        """Close the dialog and discard all changes. If the Accept button was pushed prior to this
        acction, then those entries that were in the ctegorized list have been saved."""
        print('Rejected')
        self.close()
        
    def SetCatHndlr(self):
        """The Set Cat button has been pushed. Set the Category of the
        entry that is the current selection in the UnCategorized list.
        No new trigger will be defined and therefore no new entries like
        this one will be recognized in the future. This is a manual
        category set for entries that do not contain repeating trigger
        strings."""
        #trgStr = self.selectedTriggerStr
        #if trgStr == '':
        #    raise EOFError
        selectedCat = self.listCategories.currentItem()  #.text()
        if selectedCat == None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Can't do it!")
            msgBox.setText('Please select a category!')
            msgBox.exec_()            
            return            
        selectedCatStr = selectedCat.text()    
        #if self.db.add_trigger(trgStr, selectedCatStr) == False:
        #    raise EOFError
        selectedEntryStr =  self.listUnCategorized.currentItem().text()

        selectedEntry = self.cf.find(selectedEntryStr)
        selectedEntry.category = selectedCatStr
        # clear the list
        self.listCategorized.clear()
        self.listUnCategorized.clear()
        
        # repopulate
        for check in self.db.get_ncf_entries():
            if check.category == 'None':
                cat_tuple = self.db.cat_from_desc(check.desc)
                check.category = cat_tuple[0]
                check.cat_id = cat_tuple[1]
                check.trig_id = cat_tuple[2]
                check.over_id = cat_tuple[3]
                self.listUnCategorized.addItem('\t'+check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
        self.listCategorized.repaint()
        self.listUnCategorized.repaint()
        
    def SetTriggerHndlr(self):
        """The Set Trigger button has been pushed. If a new trigger string
        has been saved in the dialog, then get the selected string and the
        selected category from the category list and make a new Trigger."""
        trgStr = self.selectedTriggerStr
        if trgStr == '':
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Can't do it!")
            msgBox.setText('Please select a trigger string!')
            msgBox.exec_()            
            return
        selectedItems = self.listCategories.selectedItems()
        if len(selectedItems) == 0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Can't do it!")
            msgBox.setText('Please select a category!')
            msgBox.exec_()            
            return            
        selectedCatStr = selectedItems[0].text()
        if self.db.add_trigger(trgStr, selectedCatStr) == False:
            raise EOFError
        # clear the list
        self.listCategorized.clear()
        self.listUnCategorized.clear()
        # repopulate
        for check in self.db.get_ncf_entries():
            if check.category == 'None':
                cat_tuple = self.db.cat_from_desc(check.desc)
                check.category = cat_tuple[0]
                check.cat_id = cat_tuple[1]
                check.trig_id = cat_tuple[2]
                check.over_id = cat_tuple[3]
                
            if check.category == 'None':
                self.listUnCategorized.addItem('/t'+check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
        self.listCategorized.repaint()
        self.listUnCategorized.repaint()
        
    def TriggerSelectedHndlr(self):
        """A new trigger string has been selected in the trigger edit line.
           Grab the selected string and save it in the dialog's instance
           variables."""
        trgStr = self.edtSelectTrigger.selectedText()
        if len(trgStr) > 0:
            self.selectedTriggerStr = trgStr
        print('>'+self.selectedTriggerStr+'<')
        
    def UnCategorizedClickHndlr(self):
        """Copy the selected entry from the UnCategorized list to the
           trigger string select edit line."""
        some = self.listUnCategorized.selectedItems()
        if len(some) == 1:
            self.edtSelectTrigger.setText(some[0].text())

    def UnCatHndlr(self):
        selection = self.listCategorized.currentItem().text()
        selectedEntry = self.cf.find(selection)
        selectedEntry.category = None
        
        # clear the list
        self.listCategorized.clear()
        self.listUnCategorized.clear()
        
        for check in self.db.get_ncf_entries():
            if check.category == None:
                cat_tuple = self.db.cat_from_desc(check.desc)
                check.category = cat_tuple[0]
                check.cat_id = cat_tuple[1]
                check.trig_id = cat_tuple[2]
                check.over_id = cat_tuple[3]
                self.listUnCategorized.addItem('/t'+check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
        self.listCategorized.repaint()
        self.listUnCategorized.repaint()
        
    #------------ End of Event Handlers ----------------

    #------------ Popup Menu Functions -----------------
    def CreatePopupActions(self):
        self.NewCatAct = QAction("New&Cat")
        self.NoneCatAct = QAction("&None")
        #newAct->setShortcuts(QKeySequence::New);
        self.NewCatAct.setStatusTip("Set entry's to this category");
        self.NoneCatAct.setStatusTip("Set entry's category to None")
        self.NewCatAct.triggered.connect(self.NewCatActionFunc)
        self.NoneCatAct.triggered.connect(self.NoneCatActionFunc)
        
    def NewCatActionFunc(self):
        """Set the current selected entries category wiyh the category that was previously
        selected in the category list."""
        self.selectedEntry.category = self.newCatStr
        self.ResortList()
        
    def NoneCatActionFunc(self):
        """Set the current selected entry's category to None"""
        self.selectedEntry.category = None
        self.ResortList()
        
    def ResortList(self):
        """Used mostly to move newly categorized entries to their place in the categorized list."""
        self.listCategorized.clear()
        self.listUnCategorized.clear()
        # repopulate
        for check in self.db.entries:
            #check.category = Trigger.fromDesc(check.desc)
            if check.category == 'None':
                self.listUnCategorized.addItem(check.asCategorizedStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
        self.listCategorized.repaint()
        self.listUnCategorized.repaint()

    #------------ End of Popup Menu Functions -----------------

    
    
        
        
        
        
