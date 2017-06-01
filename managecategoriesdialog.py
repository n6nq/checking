"""ManageCategoriesDialog provides ui for manipulating overrides, categories
   and trigger strings"""

from PyQt5.QtWidgets import (QDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
import PyQt5.QtGui
from categories_auto import Ui_ManageCategoriesDialog
import database
import accounts
import category
import trigger
import override

class ManageCategoriesDialog(QDialog, Ui_ManageCategoriesDialog):
    
    def __init__(self, db):
        super(ManageCategoriesDialog, self).__init__()
        
        self.setupUi(self)
        
        self.db = db
        self.override_str = ''
        self.category_str = ''
        self.trigger_str = ''
        
        self.listCategories.itemSelectionChanged.connect(lambda: self.list_categories_select_changed())
        self.listTriggers.itemSelectionChanged.connect(lambda: self.list_triggers_select_changed())
        self.listOverrides.itemSelectionChanged.connect(lambda: self.list_overrides_select_changed())
        self.buttonBox.accepted.connect(lambda: self.accept_changes())
        self.buttonBox.rejected.connect(lambda: self.reject_changes())
        self.edtOverride.selectionChanged.connect(lambda: self.get_override_string_hndlr())
        self.edtCategory.selectionChanged.connect(lambda: self.get_category_string_hndlr())
        self.edtTrigger.selectionChanged.connect(lambda: self.get_trigger_string_hndlr())
        self.btnNewOverride.clicked.connect(lambda: self.make_new_override())
        self.btnNewCategory.clicked.connect(lambda: self.make_new_category())
        self.btnNewTrigger.clicked.connect(lambda: self.make_new_trigger())
        self.btnRenameOverride.clicked.connect(lambda: self.rename_override())
        self.btnRenameCategory.clicked.connect(lambda: self.rename_category())
        self.btnRenameTrigger.clicked.connect(lambda: self.rename_trigger())
        self.btnDeleteOverride.clicked.connect(lambda: self.delete_override())
        self.btnDeleteCategory.clicked.connect(lambda: self.delete_category())
        self.btnDeleteTrigger.clicked.connect(lambda: self.delete_trigger())        
            
        for cat in self.db.categories.strings:
            self.listCategories.addItem(cat)
        
        self.listCategories.setCurrentRow(0)
        selectedStr = self.listCategories.selectedItems()[0].text()

        self.trigs = self.db.triggers.triggers_for_cat(selectedStr)
        for trig in self.trigs:
            self.listTriggers.addItem(trig)
        self.listTriggers.setCurrentRow(0)
        
        self.overs = self.db.overrides.overs_for_cat(selectedStr)
        for over in self.overs:
            self.listOverrides.addItem(over)
        self.listOverrides.setCurrentRow(0)
        
        self.exec_()
        
    def accept_changes(self):
        self.db.save(database.STORE_DB)
        #Trigger.save()
        #Category.save()
        #Override.save()
    
    def reject_changes(self):
        # loads clear the current dictionaries and
        # read from original again
        self.db.load()
        #Trigger.load()
        #Category.load()
        #Override.load()
    
    def list_overrides_select_changed(self):
        selected_list = self.listOverrides.selectedItems()
        if len(selected_list) > 0:
            selected_str = selected_list[0].text()
            self.override_str = selected_str
            self.edtOverride.setText(selected_str)
    
    def list_triggers_select_changed(self):
        selected_list = self.listTriggers.selectedItems()
        if len(selected_list) > 0:
            selected_str = selected_list[0].text()
            self.trigger_str = selected_str
            self.edtTrigger.setText(selected_str)
        
    def list_categories_select_changed(self):
        self.listTriggers.clear()
        self.listOverrides.clear()
        
        selected_str = self.listCategories.selectedItems()[0].text()
        self.category_str = selected_str
        self.trigs = self.db.triggers.triggers_for_cat(selected_str)
        self.overs = self.db.overrides.overs_for_cat(selected_str)
        self.edtCategory.setText(selected_str)

        for over in self.overs:
            self.listOverrides.addItem(over)
        self.listOverrides.setCurrentRow(0)
        
        for trig in self.trigs:
            self.listTriggers.addItem(trig)
        self.listTriggers.setCurrentRow(0)
     
    def get_override_string_hndlr(self):
        self.override_str = self.edtOverride.selectedText()

    def get_category_string_hndlr(self):
        self.category_str = self.edtCategory.selectedText()
    
    def get_trigger_string_hndlr(self):
        self.trigger_str = self.edtTrigger.selectedText()
        
    def make_new_override(self):
        self.override_str = self.edtOverride.text()
        cat_list = self.listCategories.selectedItems()
        
        self.db.overrides.add_over(self.override_str, cat_list[0].text())
        i = QListWidgetItem(self.override_str)
        self.listOverrides.addItem(i)
        self.listOverrides.setCurrentItem(i)
        #out = self.listOverrides.find(over_str, Qt.MatchExactly)
        pass
    
    def make_new_category(self):
        self.category_str = self.edtCategory.text()
        #cat_list = self.listCategories.selectedItems()
    
        self.db.categories.addCat(self.category_str)
        #self.db.overrides.add_over(self.override_str, cat_list[0].text())
        i = QListWidgetItem(self.category_str)
        self.listCategories.addItem(i)
        self.listCategories.setCurrentItem(i)
        #out = self.listCategories.find(over_str, Qt.MatchExactly)
        pass
    
    def make_new_trigger(self):
        self.trigger_str = self.edtTrigger.text()
        cat_list = self.listCategories.selectedItems()

        self.db.triggers.addTrig(self.trigger_str, cat_list[0].text())
        i = QListWidgetItem(self.trigger_str)
        self.listTriggers.addItem(i)
        self.listTriggers.setCurrentItem(i)
        #out = self.listOverrides.find(over_str, Qt.MatchExactly)
        pass
    
    def rename_override(self):
        row = self.listOverrides.currentRow()
        current_str = self.listOverrides.currentItem().text()
        newStr = self.edtOverride.text()
        self.listOverrides.takeItem(row)
        over = self.db.overrides.strings[current_str]
        del self.db.overrides.strings[current_str]
        self.override_str = newStr
        self.db.overrides.strings[newStr] = over
        i = QListWidgetItem(newStr)
        self.listOverrides.addItem(i)
        self.listOverrides.setCurrentItem(i)        pass
    
    def rename_category(self):
        current_str = self.listCategories.currentItem().text()
        new_str = self.edtCategory.text()
        row = self.listCategories.currentRow()
        self.listCategories.takeItem(row)
        #cat = Category.strings[current_str]
        self.category_str = new_str
        self.db.categories.strings.add(new_str)
        self.db.triggers.change_trigs_for_cat(current_str, new_str)
        self.db.overrides.change_overs_for_cat(current_str, new_str)
        self.db.categories.strings.remove(current_str)
        i = QListWidgetItem(new_str)
        self.listCategories.addItem(i)
        self.listCategories.setCurrentItem(i)
        pass
    
    def rename_trigger(self):
        row = self.listTriggers.currentRow()
        current_str = self.listTriggers.currentItem().text()
        newStr = self.edtTrigger.text()
        self.listTriggers.takeItem(row)
        trig = self.db.triggers.strings[current_str]
        del self.db.triggers.strings[current_str]
        self.trigger_str = newStr
        self.db.triggers.strings[newStr] = trig
        i = QListWidgetItem(newStr)
        self.listTriggers.addItem(i)
        self.listTriggers.setCurrentItem(i)
        pass
    
    def delete_override(self):
        if self.override_str == '' or self.override_str == None:
            return False
        current = self.listOverrides.currentRow()
        del self.db.overrides.strings[self.override_str]
        self.listOverrides.takeItem(current)
        if current > 0:
            current -= 1
        self.listOverrides.setCurrentRow(current)
        self.list_overrides_select_changed()
        pass
    
    def delete_category(self):
        current = self.listCategories.currentRow()
        current_str = self.listCategories.selectedItems()[0].text()
        msgBox = QMessageBox()
        reply = msgBox.question(self, 'All entries with this category will become uncategorized!',
                        'Yes?', QMessageBox.Yes|QMessageBox.No)
        #msgBox.exec()
        if reply == QMessageBox.Yes:
            print('KaBoom')
            self.db.removeCategory(current_str)
        else:
            print('KaBlam')
            return
        #todo all entries with this category will be changed messageBox
        self.listCategories.takeItem(current)
        #delete member of set
        self.db.categories.removeCat(current_str)
        #del Category.strings[self.category_str]
        if current > 0:
            current -= 1
        self.listCategories.setCurrentRow(current)
        self.list_categories_select_changed()
        pass
    
    def delete_trigger(self):
        #if self.trigger_str == '' or
        if self.trigger_str == None:
            return False
        current = self.listTriggers.currentRow()
        del self.db.triggers.strings[self.trigger_str]
        self.listTriggers.takeItem(current)
        if current > 0:
            current -= 1
        self.listTriggers.setCurrentRow(current)
        self.edtTrigger.clear()
        self.list_triggers_select_changed()
        pass
