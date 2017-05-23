from PyQt5.QtWidgets import (QDialog, QFileDialog, QMenu, QAction)
import PyQt5.QtGui
from readcheckfile_auto import Ui_ReadCheckFileDialog
from managecategoriesdialog import ManageCategoriesDialog
import accounts
import trigger
import category
import override
import check_file
import entry

class CheckFileDialog(QDialog, Ui_ReadCheckFileDialog):

    def __init__(self, db):
        super(CheckFileDialog, self).__init__()
        
        self.acct = accounts.Account('checking', db)
        self.acct.load()
        
        self.cf = check_file.CheckFile(self.acct)
        
        # Set up the user interface from Designer.
        self.setupUi(self)

        # Setup button actions
        self.btnReadCheckFile.clicked.connect(lambda: self.ReadFileClickHndlr())
        self.listUnCategorized.clicked.connect(lambda: self.UnCategorizedClickHndlr())
        self.edtSelectTrigger.selectionChanged.connect(lambda: self.TriggerSelectedHndlr())
        self.btnSetTrigger.clicked.connect(lambda: self.SetTriggerHndlr())
        self.edtNewCat.selectionChanged.connect(lambda: self.GetNewCatStrHndlr())
        self.btnAddCat.clicked.connect(lambda: self.AddCategoryHndlr())
        self.listCategorized.customContextMenuRequested.connect(lambda: self.CategorizedPopUpHndlr(self, self.listCategorized))
        self.listUnCategorized.customContextMenuRequested.connect(lambda: self.CategorizedPopUpHndlr(self, self.listUnCategorized))     #self.connect(self.customContextMenuRequested, QtCore.SIGNAL('customContextMenuRequested(const QPoint&)'), self.CategorizedPopUp)
        self.buttonBox.accepted.connect(lambda: self.AcceptChanges())
        self.buttonBox.rejected.connect(lambda: self.RejectChanges())
        self.btnManageCats.clicked.connect(lambda: self.OpenManageCats())
        
    
        for catStr in self.acct.categories.strings:
            self.listCategories.addItem(catStr)
        # Setup popup menu actions
        self.CreatePopupActions()
        
        #Setup varibles for dialog
        self.selectedTriggerStr = ''
        self.exec_()
        
        self.acct.save()
        #Trigger.save()
        #Category.save()
        
    #---------- Event handlers ---------------------------
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
        #iterate check file and load list widgets here
        for check in self.cf.entries:
            if check.category == self.acct.categories.no_category():
                self.listUnCategorized.addItem(check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
    
    def UnCategorizedClickHndlr(self):
        """Copy the selected entry from the UnCategorized list to the
           trigger string select edit line."""
        some = self.listUnCategorized.selectedItems()
        if len(some) == 1:
            self.edtSelectTrigger.setText(some[0].text())

    def TriggerSelectedHndlr(self):
        """A new trigger string has been selected in the trigger edit line.
           Grab the selected string and save it in the dialog's instance
           variables."""
        trgStr = self.edtSelectTrigger.selectedText()
        if len(trgStr) > 0:
            self.selectedTriggerStr = trgStr
        print('>'+self.selectedTriggerStr+'<')
        
    def SetTriggerHndlr(self):
        """The Set Trigger button has been pushed. If a new trigger string
        has been save in the dialog, then get the selected string and the
        selected category from the category list and make a new Trigger."""
        trgStr = self.selectedTriggerStr
        if trgStr == '':
            raise EOFError
        selectedItems = self.listCategories.selectedItems()
        selectedCatStr = selectedItems[0].text()
        if self.acct.triggers.addTrig(trgStr, selectedCatStr) == False:
            raise EOFError
        # clear the list
        self.listCategorized.clear()
        self.listUnCategorized.clear()
        # repopulate
        for check in self.cf.entries:
            check.category = self.acct.triggers.fromDesc(check.desc)
            if check.category == self.acct.categories.no_category():
                self.listUnCategorized.addItem(check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
        self.listCategorized.repaint()
        self.listUnCategorized.repaint()
        
    def GetNewCatStrHndlr(self):
        """A new category string has been entered in the new category edit field.
        Get it and save in a dialog instance variable."""
        self.newCatStr = self.edtNewCat.selectedText()

    def AddCategoryHndlr(self):
        """The Add Cat button was pushed. If a string was entered, make a new
        category and update the category list."""
        catStr = self.edtNewCat.text()
        self.acct.categories.addCat(catStr)
        self.listCategories.addItem(catStr)

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
    
    def AcceptChanges(self):
        print('Accepted')
        self.acct.mergeNewEntries(self.cf.entries)
        self.acct.save()
        self.close()
        
        
    def RejectChanges(self):
        print('Rejected')
        self.close()
        
    def OpenManageCats(self):
        mc = ManageCategoriesDialog(self.acct)
        
    #------------ End of Event Handlers ----------------

    #------------ Popup Menu Functions -----------------
    def CreatePopupActions(self):
        self.NewCatAct = QAction("New&Cat")
        self.NoneCatAct = QAction("&None")
        #newAct->setShortcuts(QKeySequence::New);
        self.NewCatAct.setStatusTip("Set entry's to this category");
        self.NoneCatAct.setStatusTip("Set entry's category to None")
        self.NewCatAct.triggered.connect(self.NewCatAction)
        self.NoneCatAct.triggered.connect(self.NoneCatAction)
        
    def NewCatAction(self):
        self.selectedEntry.category = self.newCatStr
        self.ResortList()
        
    def NoneCatAction(self):
        self.selectedEntry.category = self.acct.categories.no_category()
        self.ResortList()
        
    def ResortList(self):    
        self.listCategorized.clear()
        self.listUnCategorized.clear()
        # repopulate
        for check in self.cf.entries:
            #check.category = Trigger.fromDesc(check.desc)
            if check.category == self.acct.categories.no_category():
                self.listUnCategorized.addItem(check.asNotCatStr())
            else:
                self.listCategorized.addItem(check.asCategorizedStr())
        self.listCategorized.repaint()
        self.listUnCategorized.repaint()

    #------------ End of Popup Menu Functions -----------------

    
    
        
        
        
        
