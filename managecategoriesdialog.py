"""ManageCategoriesDialog provides ui for manipulating overrides, categories
   and trigger strings"""

from PyQt5.QtWidgets import (QDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
import PyQt5.QtGui
from categories_auto import Ui_ManageCategoriesDialog
from warninglistdlg_auto import Ui_warninglistdlg
from warninglistdialog import WarningListDialog
import database
import accounts
import category
import trigger
import override

class ManageCategoriesDialog(QDialog, Ui_ManageCategoriesDialog):
    
    def __init__(self, db):
        super(ManageCategoriesDialog, self).__init__()
        self.db = db
        
        self.setupUi(self)
        
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
            
        for cat in self.db.categories:
            self.listCategories.addItem(cat)
        
        self.listCategories.setCurrentRow(0)
        selectedStr = self.listCategories.selectedItems()[0].text()

        self.trigs = self.db.triggers_for_cat(selectedStr)
        for trig in self.trigs:
            self.listTriggers.addItem(trig)
        self.listTriggers.setCurrentRow(0)
        
        self.overs = self.db.overs_for_cat(selectedStr)
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
        print('Burp!')      #todo change accept/reject buttons to a done button
    
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
        self.trigs = self.db.triggers_for_cat(selected_str)
        self.overs = self.db.overs_for_cat(selected_str)
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
        
        self.db.add_override(self.override_str, cat_list[0].text())
        i = QListWidgetItem(self.override_str)
        self.listOverrides.addItem(i)
        self.listOverrides.setCurrentItem(i)
        #out = self.listOverrides.find(over_str, Qt.MatchExactly)
        pass
    
    def make_new_category(self):
        self.category_str = self.edtCategory.text()
        #cat_list = self.listCategories.selectedItems()
    
        self.db.add_cat(self.category_str)
        #self.db.overrides.add_over(self.override_str, cat_list[0].text())
        i = QListWidgetItem(self.category_str)
        self.listCategories.addItem(i)
        self.listCategories.setCurrentItem(i)
        #out = self.listCategories.find(over_str, Qt.MatchExactly)
        pass
    
    def make_new_trigger(self):
        self.trigger_str = self.edtTrigger.text()
        cat_list = self.listCategories.selectedItems()

        self.db.add_trigger(self.trigger_str, cat_list[0].text())
        i = QListWidgetItem(self.trigger_str)
        self.listTriggers.addItem(i)
        self.listTriggers.setCurrentItem(i)
        #out = self.listOverrides.find(over_str, Qt.MatchExactly)
        pass
    
    def rename_override(self):
        row = self.listOverrides.currentRow()
        current_str = self.listOverrides.currentItem().text()
        newStr = self.edtOverride.text()
        find_all_related_to_over
        warn
        db.rename_override
        self.listOverrides.takeItem(row)
        over = self.db.overrides[current_str]
        del self.db.overrides[current_str]
        self.override_str = newStr
        self.db.overrides[newStr] = over
        i = QListWidgetItem(newStr)
        self.listOverrides.addItem(i)
        self.listOverrides.setCurrentItem(i)        pass
    
    def rename_category(self):
        current_cat = self.listCategories.currentItem().text()
        new_cat = self.edtCategory.text()
        row = self.listCategories.currentRow()
        affected_list = self.db.find_all_related_to_cat(current_cat)
        dl = WarningListDialog(
            "All triggers, overrides and entries listed below are relatd to the category'"+current_cat+"'.\n" + \
            "They will have their categories change to the new category '"+new_cat+"'.\n", 
            affected_list)

        if dl.reply == True:
            print('KaBoom')
            self.db.rename_category(current_cat, new_cat)

        self.listCategories.takeItem(row)
        #cat = Category[current_cat]
        self.category_str = new_cat
        i = QListWidgetItem(new_cat)
        self.listCategories.addItem(i)
        self.listCategories.setCurrentItem(i)
    
    def rename_trigger(self):
        row = self.listTriggers.currentRow()
        current_str = self.listTriggers.currentItem().text()
        new_str = self.edtTrigger.text()

        affected_list = self.db.find_all_related_to_trig(current_str)
        dl = WarningListDialog(
            "All entries listed below are categorized by trigger string '"+current_str+"'.\n" + \
            "If they have the new trigger string '"+new_str+"', they will keep their current category.\n"+ \
            "If they do not contain the new trigger string, their category will be set to None.", 
            affected_list)
        
        self.db.rename_trigger(current_str, new_str)
        self.listTriggers.takeItem(row)
        #trig = self.db.triggers[current_str]
        #del self.db.triggers[current_str]
        self.trigger_str = new_str
        #self.db.triggers[new_str] = trig
        i = QListWidgetItem(new_str)
        self.listTriggers.addItem(i)
        self.listTriggers.setCurrentItem(i)
    
    def delete_override(self):
        if self.override_str == '' or self.override_str == None:
            return False
        current = self.listOverrides.currentRow()
        db.find_all_related_to_over
        WarningListDialog
        db.remove_override
        del self.db.overrides[self.override_str]
        self.listOverrides.takeItem(current)
        if current > 0:
            current -= 1
        self.listOverrides.setCurrentRow(current)
        self.list_overrides_select_changed()
        pass
    
    def delete_category(self):
        current_row = self.listCategories.currentRow()
        selected_cat = self.listCategories.selectedItems()[0].text()
        affected_list = self.db.find_all_related_to_cat(selected_cat)

        dl = WarningListDialog(
            'The Overrides and Triggers in the list below will be deleted!\n' + \
            'All Entries will have their category changed to None.', \
            affected_list)
        if dl.reply == True:
            print('KaBoom')
            self.db.remove_category(selected_cat)
        else:
            print('KaBlam')
            return
        #todo all entries with this category will be changed messageBox
        self.listCategories.takeItem(current_row)
        #delete member of set
        #self.db.categories.removeCat(current_str)
        #del Category[self.category_str]
        if current_row > 0:
            current_row -= 1
        self.listCategories.setCurrentRow(current_row)
        self.list_categories_select_changed()
        pass
    
    def delete_trigger(self):
        #if self.trigger_str == '' or
        if self.trigger_str == None:
            return False
        current = self.listTriggers.currentRow()
        db.find_all_related_to_trigger
        warn
        db.remove_trigger
        del self.db.triggers[self.trigger_str]
        self.listTriggers.takeItem(current)
        if current > 0:
            current -= 1
        self.listTriggers.setCurrentRow(current)
        self.edtTrigger.clear()
        self.list_triggers_select_changed()
        pass
