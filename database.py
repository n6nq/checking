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
import category
import trigger
import override

# storage defines
EMPTY = 0
STORE_DB = 1
STORE_PCKL = 2

    
class Database(object):

    def __init__(self, name):
        
        self.dbname = name
        conn = sqlite3.connect(name+'.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn = conn
        
        self.createAcctsSQL = 'create table if not exists Accounts(id integer primary key, name varchar(30) unique, start date, last date, bankurl varchar(255))'
        self.selectAllAcctsSQL = 'select oid, name, start, last, bankurl from Accounts'
        self.accounts = []
        self.load_accounts()
        
        self.createEntriesSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), sdate date, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.selectAllEntriesSQL = 'select oid, category, sdate, amount, cleared, checknum, desc from Entries'
        self.insertEntrySQL = 'insert into Entries(category, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?)'
        self.findCatInEntriesSQL = 'select oid, category, sdate, amount, cleared, checknum, desc from Entries where category = ?'
        self.updateEntryCatSQL = 'update Entries set category = ? where category = ?'
        self.updateEntryCatForOverSQL = 'update Entries set category = ? where category = ? and desc LIKE ?'
        self.updateEntryCatForTrigSQL = 'update Entries set category = ? where category = ? and desc LIKE ?'
        self.entries = []
        self.load_entries()
        
        self.temp_entries = []
        
        self.createCatsSQL = 'create table if not exists Categories(oid INTEGER PRIMARY KEY ASC, name varchar(20) unique, super varchar(20))'
        self.selectAllCatsSQL = 'select oid, name, super from Categories'
        self.insertCatSQL = 'insert into Categories(name, super) VALUES (?,?)'
        self.insertNoneCatSQL = 'insert or ignore into Categories(name, super) values (?, ?)'
        self.deleteCatSQL = 'delete from Categories where name = ?'
        self.categories = set()
        self.load_categories()
        
        self.createTrigsSQL = 'create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(30) unique, category varchar(20))'
        self.selectAllTrigsSQL = 'select oid, trigger, category from Triggers'
        self.insertTrigsSQL = 'insert into Triggers(trigger, category) values(?, ?)'
        self.findCatInTriggersSQL = 'select oid, trigger, category from Triggers where category = ?'
        self.updateTriggersCatSQL = 'update Triggers set category = ? where category = ?'
        self.deleteTrigSQL = 'delete from Triggers where trigger = ? and category = ?'
        
        self.triggers = {}
        self.load_triggers()
        
        self.createOversSQL = 'create table if not exists Overrides(oid INTEGER PRIMARY KEY ASC, override varchar(30) unique, category varchar(20))'
        self.selectAllOversSQL = 'select oid, override, category from Overrides'
        self.insertOverrideSQL = 'insert into Overrides(override, category) values(?, ?)'
        self.findCatInOverridesSQL = 'select oid, override, category from Overrides where category = ?'
        self.updateOverridesCatSQL = 'update Overrides set category = ? where category = ?'
        self.deleteOverSQL = 'delete from Overrides where override = ? and category = ?'
        
        self.overrides = {}
        self.load_overrides()

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
            if catStr in self.categories:
                return False
            else:
                self.conn.execute(self.insertCatSQL, (catStr, None))
                self.commit()
                self.categories.add(catStr)
                return True
        except sqlite3.Error as e:
            self.error('Could not save category in Category table:\n', e.args[0])
            return False
            
        
    def add_entry(self, ent):
        try:
            self.conn.execute(self.insertEntrySQL, (ent.category, ent.date, ent.amount.value, ent.checknum, ent.cleared, ent.desc))
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
            self.conn.execute(self.insertOverrideSQL, (over, cat))
            self.commit()
            self.overrides[over] = cat
            return True
        except sqlite3.Error as e:
            self.error('Could save overrides in Overrides table:\n', e.args[0])
            return False
            
            
        
    def add_temp_entry(self, row):
        self.temp_entries.append(row)
        pass
    
    def add_trigger(self, trig, cat):
        try:
            if trig in self.triggers:
                return False
            self.conn.execute(self.insertTrigsSQL, (trig, cat))
            self.commit()
            self.triggers[trig] = cat
            return True
        except sqlite3.Error as e:
            self.error('Could not save triggers in Triggers table:\n', e.args[0])
            return False
            
        
    def backup(self, name):
        self.dbname = name
        #todo: develop strategy for managing backup and restore naming
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self, STORE_DB)
        self.accts.save(STORE_PCKL)
        self.entries = entry.EntryList(self, STORE_DB)
        self.entries.save(STORE_PCKL)
        self.categories = category.Category(self, STORE_DB)
        self.categories.save(STORE_PCKL)
        self.triggers = trigger.Trigger(self, STORE_DB)
        self.triggers.save(STORE_PCKL)
        self.overrides = override.Override(self, STORE_DB)
        self.overrides.save(STORE_PCKL)

    def cat_from_desc(self, desc):
        for over, cat in self.overrides.items():
            if over in desc:
                return cat
            
        for trig, cat in self.triggers.items():
            if trig in desc:
                return cat
        
        return None
    
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

    def commit(self):
        self.conn.commit()
        
    def convert_pickles_to_DB(self):
        self.categories.load(STORE_PCKL)
        self.categories.save(STORE_DB)
        self.triggers.load(STORE_PCKL)
        self.triggers.save(STORE_DB)
        self.overrides.load(STORE_PCKL)
        self.overrides.save(STORE_DB)
        self.entries.load(STORE_PCKL)
        self.entries.save(STORE_DB)

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
            self.categories.discard(lose_cat)
            return True
        except sqlite3.Error as e:
            self.error('Could not delete Category:')
            return False
    
    def delete_category_all(self, cat):
        """Change all entries and temp_entries with this cat to None. Change the Category
        of all triggers and overrides with this cat to None. Finally remove this category."""
        #update affected entries to None 
        self.update_entries_cats(cat, category.Category.no_category())
        #update affected triggers to None
        self.update_triggers_cats(cat, category.Category.no_category())
        #update affected overrides to None
        self.update_overrides_cats(cat, category.Category.no_category())
        #remove category
        self.delete_category_only(cat)

    def delete_trigger_all(self, trig, cat):
        if trig not in self.triggers:
            return False
        try:
            cat = self.triggers[trig]
            cur = self.conn.execute(self.updateEntryCatForTrigSQL, (category.Category.no_category(), cat, "'%"+trig+"%'"))
            rowcount = cur.rowcount
            
            for ent in self.entries:
                if ent.category == cat and trig in ent.desc:
                    ent.category = category.Category.no_category()
                    
            for ent in self.entries:
                if ent.category == cat and trig in ent.desc:
                    ent.category = category.Category.no_category()
                            
            self.conn.execute(self.deleteTrigSQL, (trig, cat))
            
            del self.triggers[trig]
            self.commit()
        except sqlite3.Error as e:
            self.error('Could not delete Override:')
            return False
    def delete_override_only(self, over, cat):
        if over not in self.overrides:
            return False
        try:
            self.conn.execute(self.deleteOverSQL, (over, cat))
            
            del self.overrides[over]
            self.commit()
        except sqlite3.Error as e:
            self.error('Could not delete Override:')
            return False

    def delete_override_all(self, over, cat):
        if over not in self.overrides:
            return False
        try:
            cat = self.overrides[over]
            cur = self.conn.execute(self.updateEntryCatForOverSQL, (category.Category.no_category(), cat, "'%"+over+"%'"))
            rowcount = cur.rowcount
            
            for ent in self.entries:
                if ent.category == cat and over in ent.desc:
                    ent.category = category.Category.no_category()
                    
            for ent in self.entries:
                if ent.category == cat and over in ent.desc:
                    ent.category = category.Category.no_category()
                            
            self.conn.execute(self.deleteOverSQL, (over, cat))
            
            del self.overrides[over]
            self.commit()
        except sqlite3.Error as e:
            self.error('Could not delete Override:')
            return False
    def delete_trigger_only(self, trig, cat):
        if trig not in self.triggers:
            return False
        try:
            self.conn.execute(self.deleteTrigSQL, (trig, cat))
            
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
        print (msg, reason)     #TODO make ui for error messages  
    
    def find_all_related_to_cat(self, catstr):
        affected = []
        
        for over, cat in self.overrides.items():
            if cat == catstr:
                affected.append('<Override>'+over)

        for trig, cat in self.triggers.items():
            if cat == catstr:
                affected.append('<Trigger>'+trig)
        
        for entry in self.entries:
            if entry.category == catstr:
                affected.append('<Entry>'+entry.asCategorizedStr())
            
        return affected
    
    def find_all_related_to_trig(self, current_str):
        affected = []
        #first, get the category for this trigger
        catstr = self.triggers[current_str]
        for entry in self.entries:
            if entry.category == catstr and current_str in entry.desc:
                affected.append('<Entry>'+entry.asCategorizedStr())

        for entry in self.temp_entries:
            if entry.category == catstr and current_str in entry.desc:
                affected.append('<NewEntry>'+entry.asCategorizedStr())

        return affected
        
    def find_all_related_to_over(self, over):
        affected = []
        #first, get the category for this trigger
        catstr = self.overrides[over]
        for entry in self.entries:
            if entry.category == catstr and over in entry.desc:
                affected.append('<Entry>'+entry.asCategorizedStr())

        for entry in self.temp_entries:
            if entry.category == catstr and over in entry.desc:
                affected.append('<NewEntry>'+entry.asCategorizedStr())

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
    
    def get_all_entries(self):
        return self.entries
#        entry_list = []
#        try:
#            for row in self.conn.execute(self.entries.selectAllSQL):
#                entry_list.append(row)
#        except sqlite3.Error as e:
#            self.error('Error loading memory from the Entries table:\n', e.args[0])
#        return entry_list

    def get_all_entries_with_cat(self, cat):
        requested = []
        for ent in self.entries:
            if ent.category == cat:
                requested.append(ent)
        return requested
    
    
    def get_all_entries_with_date_range(self, date1, date2):
        requested = []
        if date1 > date2:
            temp = date1
            date1 = date2
            date2 = temp
        for ent in self.entries:
            if ent.date >= date1 and ent.date <= date2:
                requested.append(ent)
        return requested
    
    def get_all_overrides(self):
        if self.overrides.cache_loaded():
            return self.overrides.get_cache()
        overrides = {}
        try:
            for row in self.ceonn.execute(self.overrides.selectAllSQL):
                overrides[row[1]] = row[2]
        except sqlite3.Error as e:
            self.error('Error loading memory from the Overrides table:\n', e.args[0])
        return overrides
    
    def get_all_triggers(self):
        trigs = {}
        try:
            for row in self.conn.execute(self.triggers.selectAllSQL):
                trigs[row[1]] = row[2]
        except sqlite3.Error as e:
            self.error('Error loading memory from the Triggers table:\n', e.args[0])
        return trigs
        
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
                    self.categories.add(category.Category(row).cat)
            except sqlite3.Error as e:
                self.error('Error loading memory from the Categries table:\n', e.args[0])
                
    def load_entries(self):
        if len(self.entries) == 0:
            try:
                self.conn.execute(self.createEntriesSQL)
                for row in self.conn.execute(self.selectAllEntriesSQL):
                    self.entries.append(entry.Entry(self, row, entry.Entry.no_cat()))
            except sqlite3.Error as e:
                self.error('Error loading memory from the Entries table:\n', e.args[0])
                
    def load_overrides(self):
        if len(self.overrides) == 0:
            try:
                self.conn.execute(self.createOversSQL)
                for row in self.conn.execute(self.selectAllOversSQL):
                    self.overrides[row[1]] = row[2]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Overrides table:\n', e.args[0])
                
    def load_triggers(self):
        if len(self.triggers) == 0:
            try:
                self.conn.execute(self.createTrigsSQL)
                for row in self.conn.execute(self.selectAllTrigsSQL):
                    self.triggers[row[1]] = row[2]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Triggers table:\n', e.args[0])
                
    def merge_temp_entries(self):
        #As entries grows in size, make the search smarter, more code but faster
        not_cats = []
        self.temp_entries.reverse()
        while len(self.temp_entries):
            temp = self.temp_entries.pop()
            if temp.category == None:
                not_cats.append(temp)
            else:
                if temp not in self.entries:
                    self.add_entry(temp)
                #for perm_entry in self.entries:
                    #if temp == perm_entry:
                        #continue
                #self.add_entry(temp)
        if len(not_cats) > 0:
            self.temp_entries = not_cats
    
    def name(self):
        return self.dbname
    
    def open(self, name):
        self.dbname = name
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self)
        self.entries = entry.EntryList(self)
        self.categories = category.Category(self)
        self.triggers = trigger.Trigger(self)
        self.overrides = override.Override(self)
        #self.createTables()
        self.convertPicklesToDB()
        self.conn.commit()
        
    def overs_for_cat(self, lookFor):
        overs = []
        for over, cat in self.overrides.items():
            if cat == lookFor:
                overs.append(over)
                
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
        cat = self.overrides[cur_over]
        try:
            if self.add_override(new_over, cat) == False:
                return False
            
            for ent in self.conn.execute(self.findCatInEntriesSQL, (cat, )):
                if new_over not in ent.desc:
                    self.conn.execute(self.updateEntryCatSQL, (cat, category.Category.no_category()))

            for ent in self.entries:
                if ent.category == cat and new_over not in ent.desc:
                    ent.category = category.Category.no_category()
                    
            for ent in self.temp_entries:
                if ent.category == cat and new_over not in ent.desc:
                    ent.category = category.Category.no_category()
            
            if self.delete_override_only(cur_over, cat) == False:
                return False
            self.commit()
            return True
        except sqlite3.Error as e:
            self.error('Error updating triggers in Entries table:\n', e.args[0])
            return False

    def rename_trigger_all(self, cur_trig, new_trig):
        if new_trig in self.triggers:
            return False
        cat = self.triggers[cur_trig]
        try:
            if self.add_trigger(new_trig, cat) == False:
                return False
            
            for ent in self.conn.execute(self.findCatInEntriesSQL, (cat, )):
                if new_trig not in ent.desc:
                    self.conn.execute(self.updateEntryCatSQL, (cat, category.Category.no_category()))

            for ent in self.entries:
                if ent.category == cat and new_trig not in ent.desc:
                    ent.category = category.Category.no_category()
                    
            for ent in self.temp_entries:
                if ent.category == cat and new_trig not in ent.desc:
                    ent.category = category.Category.no_category()
            
            if self.delete_trigger_only(cur_trig, cat) == False:
                        return False
            self.commit()
            return True
        except sqlite3.Error as e:
            self.error('Error updating triggers in Entries table:\n', e.args[0])
            return False
    
    def restore(self, name):
        self.dbname = name
        #todo: develop strategy for managing backup and restore naming
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self, STORE_PCKL)
        self.accts.save(STORE_DB)
        self.entries = entry.EntryList(self, STORE_PCKL)
        self.entries.save(STORE_DB)
        self.categories = category.Category(self, STORE_PCKL)
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
        for over, cat in self.overrides.items():
            if cat in self.categories:
                print('Override: '+over+' Category: '+cat+' is GOOD.')
            else:
                print('Override: '+over+' Missing Cat: '+cat+' is BAD BAD.')      
                
        # check that all triggers refer to a category that exists
        for trig, cat in self.triggers.items():
            if cat in self.categories:
                print('Trigger: '+trig+' Category: '+cat+' is GOOD.')
            else:
                print('Trigger: '+trig+' Missing Cat: '+cat+' is BAD BAD.')      
            
        # check that all categories have a least one category or overrides
        for cat in self.categories:
            trig_count = 0
            over_count = 0
            for over, ocat in self.overrides.items():
                if cat == ocat:
                    over_count += 1
                    print ("Category: "+cat+" has over: "+over+" GOOD.")
            for trig, tcat in self.triggers.items():
                if cat == tcat:
                    trig_count += 1
                    print("Category: "+cat+" has trig: "+trig+" GOOD.")
            if trig_count == 0 and over_count == 0:
                print("Category: "+cat+" has no triggers or overrides.  BAD BAD.")
                
        # check that all entries have a category that exist and that their description contains a trigger
        # or override that belongs to that category. Remember, overrides first.
        for ent in self.entries:
            got_one = False
            if ent.category not in self.categories:
                print("Entry: "+ent.asCategorizedStr() + " No category. BAD BAD.")
                continue
            for over in self.overrides:
                if over in ent.desc:
                    got_one = True
                    break
            if got_one:
                continue
            for trig in self.triggers:
                if trig in ent.desc:
                    got_one = True
                    break
            if got_one:
                continue
            else:
                print("Entry: "+ent.asCategorizedStr() + " No trig or over. BAD BAD.")
                
    def triggers_for_cat(self, lookFor):
        triggers = []
        for trig, cat in self.triggers.items():
            if cat == lookFor:
                triggers.append(trig)
                
        return triggers
    
    def update_entries_cats(self, curCat, newCat):
        """Updates all entries with a specific category to a new
        a category. Changes database and memory copies of records.
        This function covers both the permanent entries and the temp_entries."""
        try:
            cur = self.conn.execute(self.updateEntryCatSQL, (newCat, curCat))
            self.commit()
            for ent in self.entries:
                if ent.category == curCat:
                    ent.category = newCat
                    
            for ent in self.temp_entries:
                if ent.category == curCat:
                    ent.category = newCat
            return True
        except sqlite3.Error as e:
            self.error('Error updating categories in Entries table:\n', e.args[0])
            return False
    
    def update_triggers_cats(self, curCat, newCat):
        """Changes all instances of triggers of a specific category to a new category.
        Changes database and memory records."""
        try:
            self.conn.execute(self.updateTriggersCatSQL, (newCat, curCat))
            self.commit()
            for trig, cat in self.triggers.items():
                if cat == curCat:
                    self.triggers[trig] = newCat
                    
            return True
        except sqlite3.Error as e:
            self.error("Error while updating trigger's categories.", e.args[0])
            return False
        
    def update_overrides_cats(self, curCat, newCat):
        try:
            self.conn.execute(self.updateOverridesCatSQL, (newCat, curCat))
            self.commit()
            for over, cat in self.overrides.items():
                if cat == curCat:
                    self.overrides[over] = newCat
                    
            return True
        except sqlite3.Error as e:
            self.error("Error while updating override's categories.", e.args[0])
            return False
        