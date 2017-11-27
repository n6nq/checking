"""databsae.py --- this module provides an application specific interface
   to a sqlite3 database for storage of application records. This module is
   also responsible all table creation and maintenance."""

# tables to create
#
# accounts = id, name, current date range, bank url
# entries = id, category, date, amount, check number, cleared, description
# categories = id, name, super category
# triggers = id, trigger string, category id
# overrides = id override string, category id

import sqlite3
import accounts
import entry
from category import Category
from trigger import Trigger
from override import Override
import datetime
from bidict import bidict
from enum import Enum
from money import Money
from PyQt5.QtWidgets import QMessageBox

# storage defines
EMPTY = 0
STORE_DB = 1
STORE_PCKL = 2

class CompareOps(Enum):
    MONEY_LESS_THAN = 1
    MONEY_MORE_THAN = 2
    MONEY_EQUALS = 3
    CHECKNUM_EQUALS = 4
    SEARCH_DESC = 5
    
class Database(object):

    def __init__(self, name):
        
        self.dbname = name
        self.start_date = datetime.date(9999, 1, 1)  # these will be set by load_entries()
        self.end_date = datetime.date(1, 1, 1)
        conn = sqlite3.connect(name+'.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn = conn
        
        self.createAcctsSQL = 'create table if not exists Accounts(id integer primary key, name varchar(30) unique, start date, last date, bankurl varchar(255))'
        self.selectAllAcctsSQL = 'select oid, name, start, last, bankurl from Accounts'
        self.accounts = []
        self.load_accounts()
        
        self.createPredictionsSQL = 'create table if not exists Predictions(oid INTEGER PRIMARY KEY ASC, name varchar(20), cat varchar(20), trig varchar(30), over varchar(30), cat_id int, trig_id int, over_id int, p_type int, cycle int, pdate date, comment varchar(128))'
        self.selectAllPredictionsSQL = 'select oid, name, cat, trig, over, cat_id, trig_id, over_id, p_type, cycle, pdate, comment from Predictions'
        
        self.createEntriesSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), cat_id int, trig_id int, over_id int, sdate date, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.migrateEntriesTableSQL = 'create table if not exists NewEntries(oid INTEGER PRIMARY KEY ASC, category varchar(20), cat_id int, trig_id int, over_id int, sdate date, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.selectAllEntriesSQL = 'select oid, category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc from Entries'
        self.insertEntrySQL = 'insert into Entries(category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.insertMigratedEntrySQL = 'insert into NewEntries(category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?)' 
        self.findCatInEntriesSQL = 'select * from Entries where cat_id = ?'

        self.updateEntryCatSQL = 'update Entries set cat_id = ?, category = ? where cat_id = ?'
        self.updateEntryCatSQLOld = 'update Entries set category = ? where category = ?'
        self.updateEntryCatByOidSQL = 'update Entries set category = ?, cat_id = ? where oid = ?'
        self.updateEntryCatForOverSQL = 'update Entries set cat_id = ?, over_id = ?, category = ? where cat_id = ? and over_id = ?'
        self.updateEntryCatForOverSQLOld = 'update Entries set category = ? where category = ? and desc LIKE ?'
        
        self.updateEntryCatForTrigSQL = 'update Entries set cat_id = ?, trig_id = ?, category = ? where cat_id = ? and trig_id = ?'
        self.updateEntryCatForTrigSQLOld = 'update Entries set category = ? where category = ? and desc LIKE ?'

        self.findEntryCatForTrigSQL = 'select * from Entries where cat_id = ? and trig_id = ?'
        self.findEntryCatForTrigSQLOld = 'select * from Entries where category = ? and desc LIKE ?'

        self.updateEntryCatByOverOnlySQL = 'update Entries set cat_id = ?, trig_id = ?, category = ? where trig_id = ?'
        self.updateEntryCatByOverOnlySQL = 'update Entries set category = ? where desc LIKE ?'

        self.updateEntryCatByTrigOnlySQL = 'update Entries set cat_id = ?, trig_id = ?, category = ? where trig_id = ?'
        self.updateEntryCatByTrigOnlySQL = 'update Entries set category = ? where desc LIKE ?'

        self.get_yrmo_groups_by_monSQL = 'select yrmo(sdate) ym, category, sum(amount) from Entries group by ym, category order by ym, category'

        self.get_yrmo_groups_by_catSQL = 'select yrmo(sdate) ym, category, sum(amount) from Entries group by ym, category order by category, ym'
        
        self.createCatsSQL = 'create table if not exists Categories(oid INTEGER PRIMARY KEY ASC, name varchar(20) unique, super varchar(20))'
        self.selectAllCatsSQL = 'select oid, name, super from Categories'
        self.insertCatSQL = 'insert into Categories(name, super) VALUES (?,?)'
        self.insertNoneCatSQL = 'insert or ignore into Categories(name, super) values (?, ?)'
        self.deleteCatSQL = 'delete from Categories where name = ?'
        
        self.createTrigsSQL = 'create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(30) unique, category varchar(20))'
        self.selectAllTrigsSQL = 'select oid, trigger, category from Triggers'
        self.insertTrigsSQL = 'insert into Triggers(trigger, category) values(?, ?)'
        self.findCatInTriggersSQL = 'select oid, trigger, category from Triggers where category = ?'
        self.updateTriggersCatSQL = 'update Triggers set category = ? where category = ?'
        self.deleteTrigSQL = 'delete from Triggers where oid = ?'
                
        self.createOversSQL = 'create table if not exists Overrides(oid INTEGER PRIMARY KEY ASC, override varchar(30) unique, category varchar(20))'
        self.selectAllOversSQL = 'select oid, override, category from Overrides'
        self.insertOverrideSQL = 'insert into Overrides(override, category) values(?, ?)'
        self.findCatInOverridesSQL = 'select oid, override, category from Overrides where override = ? and category = ?'
        self.updateOverridesCatSQL = 'update Overrides set category = ? where category = ?'
        self.deleteOverSQL = 'delete from Overrides where oid = ?'

        self.categories = {}
        self.cat_to_oid = bidict()

        self.overrides = {}
        self.over_to_oid = bidict()
        
        self.triggers = {}
        self.trig_to_oid = bidict()

        self.filtered_entries = []
        self.ncf_entries = []
        self.entries = []

        self.predictions = []
        
        self.migrate_database()
        
        self.conn.create_function('yrmo', 1, self.yrmo)
        self.num_entries = 0
        self.load_entries()
        self.load_categories()
        self.load_triggers()
        self.load_overrides()
        self.load_predictions()
        
        self.sanity_check_db()  # todo remove after dev is done
        
    def add_account(self, name):
        try:
            self.conn.execute(self.insertAccountSQL, (name, today, today, ''))
            self.commit()
            self.accounts.append(name)
            return True
        except sqlite3.Error as e:
            self.error('Could not create new Account record:\n', e.args[0])
            return False
        
    def add_cat(self, catStr):
        try:
            if catStr in self.cat_to_oid:
                self.error("Failed to add Category '{0}'".format(catStr), 'It already exists.')
                return False
            else:
                cur = self.conn.execute(self.insertCatSQL, (catStr, None))
                self.commit()
                last_id = cur.lastrowid
                self.categories[catStr] = Category((last_id, catStr, None ))
                self.cat_to_oid[catStr] = last_id                     
                return True
        except sqlite3.Error as e:
            self.error('Could not save category in Category table:\n', e.args[0])
            return False
            
        
    def add_entry(self, ent):
        try:
            self.conn.execute(self.insertEntrySQL, (ent.category, ent.cat_id, ent.trig_id, ent.over_id, ent.date, ent.amount.value, ent.checknum, ent.cleared, ent.desc))
            self.commit()
            self.entries.append(ent)
            return True
        except sqlite3.Error as e:
            self.error('Could not save entries in Entries table:\n', e.args[0])
            return False
       
    #def add_entry_list(self, entryList):
    #    try:
    #        for entry in self.entrylist:
    #            cur = self.db.conn.cursor()
    #            cur.execute(self.insertEntrySQL, (entry.category, entry.date, entry.amount.value, entry.checknum, entry.cleared, entry.desc))
    #    except sqlite3.Error as e:
    #        self.error('Could not save entries in EntryList table:\n', e.args[0])
            
    def add_override(self, over, cat):
        try:
            if over in self.over_to_oid:
                self.error("Failed to add Override '{0}'".format(over), 'It already exists.')
                return False
            else:
                cur = self.conn.execute(self.insertOverrideSQL, (over, cat))
                self.commit()
                last_id = cur.lastrowid
                self.overrides[over] = Override((last_id, over, cat))
                self.over_to_oid[over] = last_id
                return True
        except sqlite3.Error as e:
            self.error('Could save overrides in Overrides table:\n', e.args[0])
            return False
            
    def add_filtered_entry(self, ent):
        self.filtered_entries.append(ent)
    
    def add_ncf_entry(self, ent):
        self.ncf_entries.append(ent)
        
    def add_trigger(self, trig, cat):
        try:
            if trig in self.trig_to_oid:
                self.error("Failed to add Trigger '{0}'".format(catStr), 'It already exists.')                
                return False
            cur = self.conn.execute(self.insertTrigsSQL, (trig, cat))
            self.commit()
            last_id = cur.lastrowid
            self.triggers[trig] = Trigger((last_id, trig, cat))
            self.trig_to_oid[trig] = last_id
            return True
        except sqlite3.Error as e:
            self.error('Could not save triggers in Triggers table:\n', e.args[0])
            return False
            
        
    def backup(self, name):  #deprecated
        self.dbname = name
        #todo: develop strategy for managing backup and restore naming
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self, STORE_DB)
        self.accts.save(STORE_PCKL)
        self.entries = entry.EntryList(self, STORE_DB)
        self.entries.save(STORE_PCKL)
        self.categories = Category(self, STORE_DB)
        self.categories.save(STORE_PCKL)
        self.triggers = trigger.Trigger(self, STORE_DB)
        self.triggers.save(STORE_PCKL)
        self.overrides = override.Override(self, STORE_DB)
        self.overrides.save(STORE_PCKL)

    def cat_from_desc(self, desc):
        for over, override in self.overrides.items():
            if over in desc:
                return (override.cat, self.cat_to_oid[override.cat], 0, self.over_to_oid[override.over])
            
        for trig, trigger in self.triggers.items():
            if trig in desc:
                return (trigger.cat, self.cat_to_oid[trigger.cat], self.trig_to_oid[trigger.trig], 0)
        
        return ('None', 0, 0, 0)
    
    #def change_cat_of_entries(self, current, new):
        #db_affected = self.update_entries_cats(current, new)

        #list_affected = 0
        #for entry in self.entries:
            #if entry.category == current:
                #entry.category = new
                #list_affected += 1
        
        #if db_affected != list_affected:
            #self.error('Update error. {} rows affected in database, but {} affected entries in the list.\n'.format(db_affected, list_affected))

    #def change_cat_of_temp_entries(self, current, new):
        #for entry in self.temp_entries:
            #if entry.category == current:
                #entry.category = new
                #list_affected += 1
    #def change_cat_for_trigs(self, current_cat, new_cat):
        #newd = {}
        #for trig, cat in self.triggers.items():
            #if cat == current_cat:
                #newd[trig] = new_cat
            #else:
                #newd[trig] = cat
        #self.triggers = newd
        
    #def change_overs_for_cat(self, current_cat, new_cat):
        #newd = {}
        #for over, cat in self.overrides.items():
            #if cat == current_cat:
                #newd[over] = new_cat
            #else:
                #newd[over] = cat
                
        #self.overrides = newd

    def clear_fltered(self):
        self.filtered_entries = []
        
    
    def clear_ncf_entries(self):
        self.ncf_entries = []
        
    def commit(self):
        self.conn.commit()
        
    #def convert_pickles_to_DB(self):  #deprecated
        #self.categories.load(STORE_PCKL)
        #self.categories.save(STORE_DB)
        #self.triggers.load(STORE_PCKL)
        #self.triggers.save(STORE_DB)
        #self.overrides.load(STORE_PCKL)
        #self.overrides.save(STORE_DB)
        #self.entries.load(STORE_PCKL)
        #self.entries.save(STORE_DB)

    def create_table(self, sql, tableName):  #move
        try:
            self.conn.execute(sql)
            return True
        except sqlite3.Error as e:
            self.error("An error occurred when creating the "+tableName+" table:\n", e.args[0])
            return False            
        
        
    #def createTables(self):
    #    try:
    #        self.accts.createTable()
    #        self.entries.createTable()
    #        self.categories.createTable()
    #        self.triggers.createTable()
    #        self.overrides.createTable()
    #        return True
    #    except sqlite3.Error as e:
    #        print("An error occurred:", e.args[0])
    #        return False
        
    def create_account(self, name):
        self.accts.createAccount(name)
        
    
    def delete_category_only(self, lose_cat):
        try:
            self.conn.execute(self.deleteCatSQL, (lose_cat, ))
            self.commit()
            del self.categories[lose_cat]
            return True
        except sqlite3.Error as e:
            self.error('Could not delete Category:')
            return False
    
    def delete_category_all(self, cat):
        """Change all entries and temp_entries with this cat to None. Change the Category
        of all triggers and overrides with this cat to None. Finally remove this category."""
        #update affected entries to None 
        self.update_entries_cats(cat, Category.no_category())
        #update affected triggers to None
        self.update_triggers_cats(cat, Category.no_category())
        #update affected overrides to None
        self.update_overrides_cats(cat, Category.no_category())
        #remove category
        self.delete_category_only(cat)

    def delete_trigger_all(self, trig, catstr):
        if trig not in self.triggers:
            return False
        try:
            cat_id = self.cat_to_oid[catstr]
            trigger = self.triggers[trig]
            none_id = self.cat_to_oid['None']
            trig_id = trigger.oid
            cur = self.conn.execute(self.updateEntryCatForTrigSQL, (none_id, 0, Category.no_category(), cat_id, trig_id))
            self.commit()
            rowcount = cur.rowcount
            
            for ent in self.entries:
                if ent.cat_id == cat_id and ent.trig_id == trig_id:
                    ent.category = Category.no_category()
                    ent.cat_id = none_id
                    ent.trig_id = 0
                    
            for ent in self.filtered_entries:
                if ent.category == trigup[1] and trig in ent.desc:
                    ent.category = Category.no_category()
                    ent.cat_id = none_id
                    ent.trig_id = 0
                            
            self.conn.execute(self.deleteTrigSQL, (trig_id, ))
            self.commit()
            
            del self.triggers[trig]
        except sqlite3.Error as e:
            self.error('Could not delete Trigger:')
            return False
        
    def delete_override_only(self, overstr, catstr):
        if overstr not in self.overrides:
            return False
        try:
            self.conn.execute(self.deleteOverSQL, (self.over_to_oid[overstr], self.cat_to_oid[catstr]))
            
            del self.overrides[over]
            self.commit()
        except sqlite3.Error as e:
            self.error('Could not delete Override:')
            return False

    def delete_override_all(self, over, catstr):
        if over not in self.overrides:
            return False
        try:
            cat_id = self.cat_to_oid[catstr]
            override = self.overrides[over]
            none_id = self.cat_to_oid['None']
            over_id = override.oid
            cur = self.conn.execute(self.updateEntryCatForOverSQL, (none_id, 0, Category.no_category(), cat_id, over_id))
            self.commit()
            rowcount = cur.rowcount
            
            for ent in self.entries:
                if ent.cat_id == cat_id and ent.over_id == over_id:
                    ent.category = Category.no_category()
                    ent.cat_id = none_id
                    ent.over_id = 0
                    
            for ent in self.filtered_entries:
                if ent.category == override.cat and over in ent.desc:
                    ent.category = Category.no_category()
                    ent.cat_id = none_id
                    ent.over_id = 0
                            
            self.conn.execute(self.deleteOverSQL, (over_id, ))
            self.commit()
            
            del self.overrides[over]
        except sqlite3.Error as e:
            self.error('Could not delete Override:')
            return False
        
    def delete_trigger_only(self, trig, cat):
        if trig not in self.triggers:
            return False
        try:
            self.conn.execute(self.deleteTrigSQL, (self.triggers[trig].oid, ))
            
            del self.triggers[trig]
            self.commit()
        except sqlite3.Error as e:
            self.error('Could not delete Trigger:')
            return False
            

    def entry_is_dupe(self, newEtry):
        for entry in self.entrylist:
            if entry.compare(newEtry):
                return True
        return False
    
    def error(self, msg, reason):
        msgBox = QMessageBox()
        msgBox.setWindowTitle('Error!')
        msgBox.setText(msg+'\n'+reason)
        #msgBox.setDetailedText(reason)
        #msgBox.addButton(QtGui.QPushButton('Accept'), QtGui.QMessageBox.YesRole)
        #msgBox.addButton(QtGui.QPushButton('Reject'), QtGui.QMessageBox.NoRole)
        #msgBox.addButton(QtGui.QPushButton('Cancel'), QtGui.QMessageBox.RejectRole)
        self.retval = msgBox.exec_()
        
    
    def find_all_related_to_cat(self, catstr):
        affected = []
        
        for over, override in self.overrides.items():
            if override.cat == catstr:
                affected.append('<Override>'+override.over)

        for trig, trigger in self.triggers.items():
            if trigger.cat == catstr:
                affected.append('<Trigger>'+trigger.trig)
        
        for entry in self.entries:
            if entry.category == catstr:
                affected.append('<Entry>'+entry.asCategorizedStr())
            
        return affected
    
    def find_all_related_to_trig(self, current_trig, new_trig):
        affected = []
        #Are we trying to rename an existing trigger to another trigger that exists?
        if new_trig and new_trig in self.trig_to_oid:
            affected.append("<Trigger> '"+new_trig+"' already exists. Datbase module will block this attempt.")
            
        #first, get the category for this trigger
        trigger = self.triggers[current_trig]
        trig_id = trigger.oid
        catstr = trigger.cat
        cat_id = self.cat_to_oid[catstr]
        
        for entry in self.entries:
            if entry.cat_id == cat_id and entry.trig_id == trig_id:
                affected.append('<Entry>'+entry.asCategorizedStr())

        for entry in self.ncf_entries:
            if entry.cat_id == cat_id and entry.trig_id == trig_id:
                affected.append('<NewEntry>'+entry.asCategorizedStr())

        #Are there already categorized entries that have this new trigger?
        if new_trig:
            for entry in self.entries:
                if new_trig in entry.desc:
                    affected.append('<Existing Entry> will be re-categorized: '+entry.asCategorizedStr())
 
        return affected
        
    def find_all_related_to_over(self, cur_over, new_over):
        affected = []
        #Are we trying to rename an existing override to another override that exists?
        if new_over and new_over in self.over_to_oid:
            affected.append("<Override> '"+new_over+"' already exists. Datbase module will block this attempt.")
            
        #first, get the category for this override
        override = self.overrides[cur_over]
        over_id = override.oid
        catstr = override.cat
        cat_id = self.cat_to_oid[catstr]
        
        for entry in self.entries:
            if entry.cat_id == cat_id and entry.over_id == over_id:
                affected.append('<Entry>'+entry.asCategorizedStr())

        for entry in self.ncf_entries:
            if entry.cat_id == cat_id and entry.over_id == over_id:
                affected.append('<NewEntry>'+entry.asCategorizedStr())

        #Are there already categorized entries that have this new override?
        if new_over:
            for entry in self.entries:
                if new_over in entry.desc:
                    affected.append('<Existing Entry> will be re-categorized: '+entry.asCategorizedStr())

        return affected
        
    def find_all_with_trigger(self, trig):
        affected = []
        for entry in self.entries:
            if trig in entry.desc:
                affected.append('<Entry>'+entry.asCategorizedStr())

        #for entry in self.temp_entries:
        #    if trig in entry.desc:
        #        affected.append('<NewEntry>'+entry.asCategorizedStr())

        return affected

    def get_all_accounts(self):
        acct_list = []
        try:
            for row in self.conn.execute(self.accts.selectAllSQL):
                acct_list.append(row)
        except sqlite3.Error as e:
            self.error('Error loading memory from the Accounts table:\n', e.args[0])
        return acct_list
    
    def get_all_cats(self):
        if len(self.categories) == 0:
            self.load_categories()
        return self.categories
    
    def get_all_entries(self, which):
        if which == 'All':
            self.filtered_entries = self.entries
            return self.entries
        elif which == 'Results':
            return self.filtered_entries
        
    def get_all_entries_meeting(self, which, op, value):
        requested = []
        if which == 'All':
            search_list = self.entries
        else:
            search_list = self.filtered_entries
        
        for ent in search_list:
            if op == CompareOps.MONEY_LESS_THAN:
                if ent.amount < Money.from_str(value):
                    requested.append(ent)
            elif op == CompareOps.MONEY_MORE_THAN:
                if ent.amount > Money.from_str(value):
                    requested.append(ent)
            elif op == CompareOps.MONEY_EQUALS:
                if ent.amount == Money.from_str(value):
                    requested.append(ent)
            elif op == CompareOps.CHECKNUM_EQUALS:
                if ent.checknum == value:
                    requested.append(ent)
            elif op == CompareOps.SEARCH_DESC:
                if value in ent.desc:
                    requested.append(ent)
            else:
                print('YIKES1')
        self.filtered_entries = requested
        return requested
    
    def get_all_entries_with_cat(self, which, cat):
        requested = []
        if which == 'All':
            search_list = self.entries
        else:
            search_list = self.filtered_entries
            
        for ent in search_list:
            if ent.category == cat:
                requested.append(ent)
        self.filtered_entries = requested
        return requested
    
    
    def get_all_entries_with_date_range(self, which, date1, date2):
        requested = []
        if which == 'All':
            search_list = self.entries
        else:
            search_list = self.filtered_entries
        if date1 > date2:
            temp = date1
            date1 = date2
            date2 = temp
        for ent in search_list:
            if ent.date >= date1 and ent.date <= date2:
                requested.append(ent)
        self.filtered_entries = requested
        return requested
    
    
    def get_all_predictions(self):
        return self.predictions
    
    def get_all_triggers(self):
        triggers = {}
        try:
            for row in self.conn.execute(self.triggers.selectAllTrigSQL):
                triggers[row[1]] = trigger(row[0], row[1], row[2])
        except sqlite3.Error as e:
            self.error('Error loading memory from the Triggers table:\n', e.args[0])
        return triggers
        
    def yrmo(self, d):
        return d[:7]
    
    def get_cat_by_month(self):
        """Get totals of all categories grouped by month"""
        requested = []
        for row in self.conn.execute(self.get_yrmo_groups_by_monSQL):
            requested.append(row)
        return requested
    
    def get_month_by_cat(self):
        """Get totals for all months grouped by category"""
        requested = []
        for row in self.conn.execute(self.get_yrmo_groups_by_catSQL):
            requested.append(row)
        return requested
        

    def get_ncf_entries(self):
        return self.ncf_entries

    def get_predictions_column_count(self):
        #oid,name,cat,trig,over,cat_id,trig_id,over_id,p_type,cycle,pdate,comment
        return 11
    
    def get_recent_entries(self, limit):
        if self.num_entries <= limit:
            return self.get_all_entries(which)
        today = datetime.date.today()
        trial = today - datetime.timedelta(months = 2)
        for ent in self.entries:
            if ent.date > previous:
                howmany += 1
        
    def get_last_three_months(self, today):
        entries = []
        start = today - datetime.timedelta(weeks=13)
        for ent in self.entries:
            if ent.date >= start and ent.date <= today:
                entries.append(ent)
        return entries
        
    def load_accounts(self):
        if len(self.accounts) == 0:
            try:
                self.conn.execute(self.createAcctsSQL)
                for row in self.conn.execute(self.selectAllAcctsSQL):
                    self.accounts.append(accounts.Account(row))
            except sqlite3.Error as e:
                self.error('Error loading memory from the Accounts table:\n', e.args[0])

    def load_categories(self):
        if len(self.categories) == 0:
            try:
                self.conn.execute(self.createCatsSQL)
                self.conn.execute(self.insertNoneCatSQL, ('None', 'None'))
                for row in self.conn.execute(self.selectAllCatsSQL):
                    self.categories[row[1]] = Category(row)
                    self.cat_to_oid[row[1]] = row[0]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Categries table:\n', e.args[0])
                
    def load_entries(self):
        try:
            self.conn.execute(self.createEntriesSQL)
            for row in self.conn.execute(self.selectAllEntriesSQL):
                ent = entry.Entry(self, row, entry.Entry.no_cat())
                self.entries.append(ent)
                self.num_entries += 1
                print(ent.date, self.start_date, self.end_date)
                self.start_date = min(self.start_date, ent.date)
                self.end_date = max(self.end_date, ent.date)
        except sqlite3.Error as e:
            self.error('Error loading memory from the Entries table:\n', e.args[0])
                
    def load_predictions(self):
        try:
            self.conn.execute(self.createPredictionsSQL)
            for row in self.conn.execute(self.selectAllPredictionsSQL):
                pred = Prediction(self, row)
                self.predictions.append(pred)
                self.num_predictions += 1
        except sqlite3.Error as e:
            self.error('Error loading memory from the Predictions table:\n', e.args[0])
                
    def load_overrides(self):
        if len(self.overrides) == 0:
            try:
                self.conn.execute(self.createOversSQL)
                for row in self.conn.execute(self.selectAllOversSQL):
                    self.overrides[row[1]] = Override(row)
                    self.over_to_oid[row[1]] = row[0]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Overrides table:\n', e.args[0])
                
    def load_triggers(self):
        if len(self.triggers) == 0:
            try:
                self.conn.execute(self.createTrigsSQL)
                for row in self.conn.execute(self.selectAllTrigsSQL):
                    self.triggers[row[1]] = Trigger(row)
                    self.trig_to_oid[row[1]] = row[0]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Triggers table:\n', e.args[0])
                
    def merge_ncf_entries(self):
        #As entries grows in size, make the search smarter, more code but faster
        not_cats = []
        entry_set = set(self.entries)
        self.ncf_entries.reverse()
        while len(self.ncf_entries):
            temp = self.ncf_entries.pop()
            if temp.category == None:
                not_cats.append(temp)
            else:
                if temp in entry_set:
                    self.update_entry_cat_by_oid(temp.category, temp.cat_id, temp.oid)
                else:
                    self.add_entry(temp)
                #for perm_entry in self.entries:
                    #if temp == perm_entry:
                        #continue
                #self.add_entry(temp)
        if len(not_cats) > 0:
            self.ncf_entries = not_cats
    
    def migrate_database(self):
        """Determine what version database we have, and migrate if necessary.
        Migration 1 is verison None to version"""
        try:
            version = 0
            self.conn.execute('create table if not exists Version(version_str varchar(30), version_int int)')
            for row in self.conn.execute('select * from Version'):
                version = row[1]
            if version == 0:
                self.migrate_entries(version)
            return True
        except sqlite3.Error as e:
            self.error('What? ', e.args[0])
            return False
    
    def make_cat_to_override_dict(self):
        self.cat_to_overrides = {}
        for override in self.overrides:
            #override = self.overrides[over]
            oid = override.oid
            cat = override.cat
            if cat in self.cat_to_overrides:
                self.cat_to_overrides[cat].append(override)
            else:
                self.cat_to_overrides[cat] = [override]

    def make_cat_to_trigger_dict(self):
        self.cat_to_triggers = {}
        for trigger in self.triggers:
            oid = trigger.oid
            cat = trigger.cat
            if cat in self.cat_to_triggers:
                self.cat_to_triggers[cat].append((oid, trigger.trig))
            else:
                self.cat_to_triggers[cat] = [(oid, trigger.trig)]
        
    def migrate_entries(self, old_version):
        try:
            if old_version == 0:
                self.load_categories()
                self.load_overrides()
                self.load_triggers()
                self.make_cat_to_override_dict()
                self.make_cat_to_trigger_dict()
                self.conn.execute('drop table if exists NewEntries')
                self.conn.execute(self.migrateEntriesTableSQL)
                for row in self.conn.execute(self.selectAllEntriesSQL):
                    if row[1] in self.cat_to_overrides:
                        override_list = self.cat_to_overrides[row[1]]
                        for override_tuple in override_list:
                            if override_tuple[1] in row[6]:
                                #NewEntries(category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?)
                                newRow = (row[1], self.cat_to_oid[row[1]], 0, override_tuple[0], row[2], row[3], row[4], row[5], row[6])
                                self.conn.execute(self.insertMigratedEntrySQL, newRow)
                                print (newRow)
                                break
                                
                    if row[1] in self.cat_to_triggers:
                        trigger_list = self.cat_to_triggers[row[1]]
                        for trigger_tuple in trigger_list:
                            if trigger_tuple[1] in row[6]:
                                #NewEntries(category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?)
                                newRow = (row[1], self.cat_to_oid[row[1]], trigger_tuple[0], 0, row[2], row[3], row[4], row[5], row[6])
                                self.conn.execute(self.insertMigratedEntrySQL, newRow)
                                print (newRow)
                                break
                self.conn.execute('ALTER TABLE Entries RENAME TO OldEntries')
                self.conn.execute('ALTER TABLE NewEntries RENAME TO Entries')
                self.conn.execute('INSERT OR REPLACE INTO Version(version_str, version_int) VALUES ("V0.1", 1)')
                self.commit()
                return True
        except sqlite3.Error as e:
            self.error('Migration error 1: ', e.args[0])
            return False
        
    def name(self):
        return self.dbname
    
    def open(self, name, deprecated):  #deprecated
        self.dbname = name
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self)
        self.entries = entry.EntryList(self)
        self.categories = Category(self)
        self.triggers = trigger.Trigger(self)
        self.overrides = override.Override(self)
        #self.createTables()
        self.convertPicklesToDB()
        self.conn.commit()
        
    def overs_for_cat(self, lookFor):
        overs = []
        for over, override in self.overrides.items():
            if override.cat == lookFor:
                overs.append(override)
                
        return overs

    def rename_category_all(self, current_cat, new_cat):
        if self.add_cat(new_cat) == False or \
           self.update_overrides_cats(current_cat, new_cat) == False or \
           self.update_triggers_cats(current_cat, new_cat) == False or \
           self.update_entries_cats(current_cat, new_cat) == False or \
           self.delete_category_only(current_cat) == False:
            return False
        else:
            self.commit()
            return True
        
    def rename_override_all(self, cur_over, new_over):
        #We will not rename override to another existing, too complicated, delete override
        if new_over in self.overrides:
            return False
        
        override = self.overrides[cur_over]
        over_id = override.oid
        catstr = override.cat
        cat_id = self.cat_to_oid[catstr]
        nonecat_id = self.cat_to_oid['None']
        try:
            if self.add_override(new_over, catstr) == False:
                return False
            
            for ent in self.conn.execute(self.findCatInEntriesSQL, (cat_id, )):
                if new_over not in ent[6]:
                    self.conn.execute(self.updateEntryCatSQL, (cat, cat_id, Category.no_category()))
                    self.commit()

            for ent in self.entries:
                if ent.cat_id == cat_id and ent.over_id == over_id and new_over not in ent.desc:
                    ent.category = Category.no_category()
                    ent.cat_id = nonecat_id
            for ent in self.filtered_entries:
                if ent.cat_id == cat_id and new_over not in ent.desc:
                    ent.category = Category.no_category()
                    ent.cat_id = nonecat_id
            if self.delete_override_only(cur_over, catstr) == False:
                return False
            self.commit()
            return True
        except sqlite3.Error as e:
            self.error('Error updating triggers in Entries table:\n', e.args[0])
            return False

    def rename_trigger_all(self, cur_trig, new_trig):
        #We will not rename trig to another existing, too complicated, delete trigger
        if new_trig in self.triggers:
            return False
        
        trigger = self.triggers[cur_trig]
        trig_id = trigger.oid
        catstr = trigger.cat
        cat_id = self.cat_to_oid[catstr]
        nonecat_id = self.cat_to_oid['None']
        try:
            if self.add_trigger(new_trig, catstr) == False:
                return False    #Can't add the trigger if it is already there.
            
            #All entries with old but not new trigger are set to None 
            for ent in self.conn.execute(self.findEntryCatForTrigSQL, (cat_id, trig_id)):
                if new_trig not in ent[6]:
                    #cat_id and what trig_id
                    self.conn.execute(self.updateEntryCatSQL, (cat, cat_id, Category.no_category()))
                    self.commit()
                    
            #Now get the cached entries
            for ent in self.entries:
                if ent.cat_id == cat_id and ent.trig_id == trig_id and new_trig not in ent.desc:
                    ent.category = Category.no_category()
                    ent.cat_id = nonecat_id
            for ent in self.filtered_entries:
                if ent.category == cat and new_trig not in ent.desc:
                    ent.category = Category.no_category()
                    ent.cat_id = nonecat_id
            if self.delete_trigger_only(cur_trig, catstr) == False:
                        return False
            self.commit()
            return True
        except sqlite3.Error as e:
            self.error('Error updating triggers in Entries table:\n', e.args[0])
            return False
    
    def restore(self, name):  #deprecated
        self.dbname = name
        #todo: develop strategy for managing backup and restore naming
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self, STORE_PCKL)
        self.accts.save(STORE_DB)
        self.entries = entry.EntryList(self, STORE_PCKL)
        self.entries.save(STORE_DB)
        self.categories = Category(self, STORE_PCKL)
        self.categories.save(STORE_DB)
        self.triggers = trigger.Trigger(self, STORE_PCKL)
        self.triggers.save(STORE_DB)
        self.overrides = override.Override(self, STORE_PCKL)
        self.overrides.save(STORE_DB)
        self.conn.commit()
        
    
    def save(self, storage):
        print("Database.save is OBSOLETE")
        #self.categories.save(storage)
        #self.triggers.save(storage)
        #self.overrides.save(storage)
        #self.entries.save(storage)

    def sanity_check_db(self):
        # first check that every override refers to a category that exists
        for over, override in self.overrides.items():
            if override.cat in self.cat_to_oid:
                print('Override: '+override.over+' Category: '+override.cat+' is GOOD.')
            else:
                print('Override: '+override.over+' Missing Cat: '+override.cat+' is BAD BAD.')      
                
        # check that all triggers refer to a category that exists
        for trig, trigger in self.triggers.items():
            if trigger.cat in self.cat_to_oid:
                print('Trigger: '+trigger.trig+' Category: '+trigger.cat+' is GOOD.')
            else:
                print('Trigger: '+trigger.trig+' Missing Cat: '+trigger.cat+' is BAD BAD.')      
            
        # check that all categories have a least one trigger or overrides
        for cat, category in self.categories.items():
            trig_count = 0
            over_count = 0
            for over, override in self.overrides.items():
                if category.cat == override.cat:
                    over_count += 1
                    print ("Category: "+category.cat+" has over: "+override.over+" GOOD.")
            for trig, trigger in self.triggers.items():
                if category.cat == trigger.cat:
                    trig_count += 1
                    print("Category: "+category.cat+" has trig: "+trigger.trig+" GOOD.")
            if trig_count == 0 and over_count == 0:
                print("Category: "+category.cat+" has no triggers or overrides.  BAD BAD.")
                
        # check that all entries have a category that exist and that their description contains a trigger
        # or override that belongs to that category. Remember, overrides first.
        for ent in self.entries:
            got_one = False
            if ent.category not in self.cat_to_oid:
                print("Entry: "+ent.asCategorizedStr() + " No category. BAD BAD.")
                continue
            for over, override in self.overrides.items():
                if override.over in ent.desc:
                    got_one = True
                    break
            if got_one:
                continue
            for trig, trigger in self.triggers.items():
                if trigger.trig in ent.desc:
                    got_one = True
                    break
            if got_one:
                continue
            else:
                print("Entry: "+ent.asCategorizedStr() + " No trig or over. BAD BAD.")
                
    def set_cat_for_all_with_over(self, cat, over):
        try:
            self.conn.execute(self.updateEntryCatByOverOnlySQL, (cat, over))
            self.commit()
            for entry in self.entries:
                if over in entry.desc:
                    entry.category = cat

            #for entry in self.temp_entries:
            #    if over in entry.desc:
            #        entry.category = cat
            return True
        except sqlite3.Error as e:
            self.error('Error updating categories by override in Entries table:\n', e.args[0])
            return False
        
        return affected

    def set_cat_for_all_with_trigger(self, cat, trig):
        try:
            self.conn.execute(self.updateEntryCatByTrigOnlySQL, (cat, trig))
            self.commit()
            for entry in self.entries:
                if trig in entry.desc:
                    entry.category = cat

            #for entry in self.temp_entries:
            #    if trig in entry.desc:
            #        entry.category = cat
            return True
        except sqlite3.Error as e:
            self.error('Error updating categories by trigger in Entries table:\n', e.args[0])
            return False
        
        return affected

    def set_ncf_entries(self, new_checks):
        self.ncf_entries = new_checks
        
    def triggers_for_cat(self, lookFor):
        trig_list = []
        for trig, trigger in self.triggers.items():
            if trigger.cat == lookFor:
                trig_list.append(trigger.trig)
                
        return trig_list
    
    def update_entries_cats(self, curCat, newCat):
        """Updates all entries with a specific category to a new
        a category. Changes database and memory copies of records.
        This function covers both the permanent entries and the filtered_entries."""
        try:
            new_id = self.cat_to_oid[newCat]
            cur_id = self.cat_to_oid[curCat]
            cur = self.conn.execute(self.updateEntryCatSQL, (new_id, newCat, cur_id))
            self.commit()
            for ent in self.entries:
                if ent.cat_id == cur_id:
                    ent.category = newCat
                    ent.cat_id = new_id
                    
            for ent in self.filtered_entries:
                if ent.cat_id == cur_id:
                    ent.category = new_id
            return True
        except sqlite3.Error as e:
            self.error('Error updating categories in Entries table:\n', e.args[0])
            return False
        except KeyError as e:
            self.error("Bug in update_entries_cats:\n", e.args[0])
            return False
        
    def update_entry_cat_by_oid(self, cat, cat_id, oid):
        try:
            cur = self.conn.execute(self.updateEntryCatByOidSQL, (cat, cat_id, oid))
            self.commit()
            for ent in self.entries:
                if ent.oid == oid:
                    ent.category = cat
                    ent.cat_id = cat_id
            return True
        except sqlite3.Error as e:
            self.error('Error updating category of Entry with oid: {0}'.format(oid))
            return False
        
    def update_triggers_cats(self, curCat, newCat):
        """Changes all instances of triggers of a specific category to a new category.
        Changes database and memory records."""
        try:
            self.conn.execute(self.updateTriggersCatSQL, (newCat, curCat))
            self.commit()
            for trig, trigger in self.triggers.items():
                if trigger.cat == curCat:
                    trigger.cat = newCat
                    
            return True
        except sqlite3.Error as e:
            self.error("Error while updating trigger's categories.", e.args[0])
            return False
        
    def update_overrides_cats(self, curCat, newCat):
        try:
            cur = self.conn.execute(self.updateOverridesCatSQL, (newCat, curCat))
            self.commit()
            last_id = cur.lastrowid
            for over, override in self.overrides.items():
                if override.cat == curCat:
                    override.cat = newCat
                    #self.overrides[over] = newCat
                    
            return True
        except sqlite3.Error as e:
            self.error("Error while updating override's categories.", e.args[0])
            return False
        