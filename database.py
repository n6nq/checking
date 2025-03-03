"""databsae.py --- this module provides an application specific interface
   to a sqlite3 database for storage of application records. This module is
   also responsible for all table creation and maintenance."""

# todo -- delvelop a backup strategy
import index
import sqlite3
import accounts
import entry
from predicted import Prediction
from category import Category
from trigger import Trigger
from override import Override
import datetime
from bidict import bidict
from enum import Enum
from money import Money
from PyQt5.QtWidgets import QMessageBox
from pcycle import PCycle, Cycles
import common_ui
from shutil import copyfile

# storage defines
#EMPTY = 0
STORE_DB = 1
#STORE_PCKL = 2


class CompareOps(Enum):
    """This class enumerates a set of ops for comparing entries."""
    MONEY_LESS_THAN = 1
    MONEY_MORE_THAN = 2
    MONEY_EQUALS = 3
    CHECKNUM_EQUALS = 4
    SEARCH_DESC = 5
    
class DB(object):
    """Database -- The Database class creates a Sqlite3 database file the first time it is instantiated,
       if such a fie does not already exist. It then creates tables for entries, triggers, categories, etc.
       if they do not exist in the file that has been opened. All of this creation should only happen once,
       when you run this application for the first time.
       Member varibles:
       dbname -- Not used at this time (8/29/18)
       start_date -- Used by load entries to determiine which entries to load.
       end_date   -- ditto
       conn -- This is our connction to the Sqlite database. It is used by all database functions that
               perform any operations on the database.
       accounts -- A list of thw accounts read from the database.
       categories -- A dictionary of category string to super category strings. Super categories has not been
                     implemented as of 8/13/18.
       cat_to_oid -- A bi-directional dictionary equting cat strings to cat numbers and vice-vrsus.
       overrides -- A dictionary of override strings that defines the category of an entry. If the overrides
                    exist in an entry, its category takes the place of any any category defined by a trigger.
       over_to_oid -- A bi-directional dictionary that equates override strings to the numbers.
       triggers -- A dictionary of trigger strings to category strings.
       trig_to_oid -- A bi-direcional dictionary of trigger strings to trigger numbers.
       filtered_entries -- A list of ntries that meet some search criteria. Typically used bby the main window
                        for doing list subsetting based on some column value.
       ncf_entries -- A list of new check file entries. They ususally come to the Database module from the CheckFileDialog
                      to be merged into the Entry database table.
       entries --  A list of all check entries that this program has received from check files from the bank.
       predictions -- A list of Predictions. A prediction is a checking account transaction that hasn't happened yet. A
                      Prediction is almost the same as an Entry except the date is a futture starting date and there
                      is an extra value to indicate the repetition rate. Predictions are used in the Predicted window to
                      plot a future balance graph.
       num_entries -- An integer indicating the number of entries read from the database. Only used by get_recent_entries().
       num_predictions -- An integer indicting the number of predictions read from the database. Not used at this time.
       xxxxSQL -- There are numerous SQL strings to supply all the required data access t the rest of
               this program. They include createAcctsSQL, selectAllAcctsSQL, createCatsSQL, createEntriesSQL,
               createOversSQL, createPredictionsSQL, createPredictions2SQL, createTrigsSQL, deleteCatSQL,
               deleteOverSQL, deletePredictionSQL, deleteTrigSQL, findCatInEntriesSQL, findCatInOverridesSQL,
               findCatInTriggersSQL, findEntryCatForTrigSQL, findEntryCatForTrigSQLOld, get_yrmo_groups_by_catSQL,
               get_yrmo_groups_by_monSQL, insertCatSQL, insertEntrySQL, insertMigratedEntrySQL, insertNoneCatSQL,
               insertOverrideSQL, insertPrediction1SQL, insertPredictionSQL, insertTrigsSQL, migrateEntriesTableSQL,
               migrate2PredictionsSQL, selectAllCatsSQL, selectAllOversSQL, selectAllEntriesSQL,
               selectAllPredictionsSQL, selectAllTrigsSQL, updateEntryCatByOverOnlySQL, updateEntryCatByOverOnlySQL,
               updateEntryCatByTrigOnlySQL, updateEntryCatByTrigOnlySQL, updateEntryCatByOidSQL,
               udateEntryCatForOverSQL, updateEntryCatForOverSQLOld, updateEntryCatForTrigSQL,
               updateEntryCatForTrigSQLOld, updateEntryCatSQL, updateEntryCatSQLOld, updateOverridesCatSQL,
               updatePredictionSQL, updateTriggersCatSQL.
    """

    # The rows come back as lists. The following defined values provide names for the columns
    # rather than using numbers. Keep the numbers matching the create statements below as the table 
    # definitions change and the accessing code won't need to change.

    def __init__(self, name):
        """A single instance of the Database class is created by the Main window. A reference is passed to all
           other parts of the program. This constructor checks o see if the database file already exist and creates
           it and all the tables if it does not."""
        self.dbname = name+'.db'
        self.start_date = datetime.date(9999, 1, 1)  # these will be set by load_entries()
        self.end_date = datetime.date(1, 1, 1)
        conn = sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn = conn
        
        # WARNING If you modify any of the column declarations in the create table statements below, then change the corresponding indexes
        # in index.py

        self.createAcctsSQL = 'create table if not exists Accounts(id integer primary key, name varchar(30) unique, start date, last date, bankurl varchar(255))'
        self.selectAllAcctsSQL = 'select oid, name, start, last, bankurl from Accounts'
        self.accounts = []
        self.load_accounts()
        
        self.createPredictionsSQL = 'create table if not exists Predictions(oid INTEGER PRIMARY KEY ASC, amount int, income int, cat varchar(20), trig varchar(30), over varchar(30), cat_id int, trig_id int, over_id int, cycle int, ddate date, vdate int, desc varchar(128))'
        self.createPredictions2SQL = 'create table if not exists Predictions2(oid INTEGER PRIMARY KEY ASC, amount int, income int, cat varchar(20), trig varchar(30), over varchar(30), cat_id int, trig_id int, over_id int, cycle int, ddate date, vdate int, desc varchar(128))'
        self.selectAllPredictionsSQL = 'select oid, amount, income, cat, trig, over, cat_id, trig_id, over_id, cycle, ddate, vdate, desc from Predictions'
        self.insertPrediction1SQL = 'insert into Predictions(amount, income, cat, trig, over, cat_id, trig_id, over_id, ptype, cycle, ddate, vdate, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.insertPredictionSQL = 'insert into Predictions(amount, income, cat, trig, over, cat_id, trig_id, over_id, cycle, ddate, vdate, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.migrate2PredictionsSQL = 'insert into Predictions2(oid, amount, income, cat, trig, over, cat_id, trig_id, over_id, cycle, ddate, vdate, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.deletePredictionSQL = 'delete from Predictions where oid = ?'
        self.updatePredictionSQL = 'update Predictions set amount = ?, income = ?, cat = ?, trig = ?, over = ?, cat_id = ?, trig_id = ?, over_id = ?, cycle = ?, ddate = ?, vdate = ?, desc = ? where oid = ?'
        
        self.createEntriesSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), cat_id int, trig_id int, over_id int, sdate date, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.migrateEntriesTableSQL = 'create table if not exists NewEntries(oid INTEGER PRIMARY KEY ASC, category varchar(20), cat_id int, trig_id int, over_id int, sdate date, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.selectAllEntriesSQL = 'select oid, category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc from Entries'
        self.insertEntrySQL = 'insert into Entries(category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?)'
        self.insertMigratedEntrySQL = 'insert into NewEntries(category, cat_id, trig_id, over_id, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?)' 
        self.findCatInEntriesSQL = 'select * from Entries where cat_id = ?'
        self.deleteOldEntriesSQL = "delete from Entries where sdate < date('now','-12 months')"

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

#        self.get_yrmo_groups_by_monSQL = 'select yrmo(sdate) ym, category, trig_id, over_id, sum(amount) from Entries group by ym, category, trig_id, over_id order by ym, category, trig_id, over_id'
        self.get_yrmo_groups_by_monSQL = "select strftime('%Y',sdate) ym, category, trig_id, over_id, sum(abs(amount*1.0))/100, count(*), (sum(abs(amount*1.0))/100)/count(*) from Entries group by ym, category, trig_id, over_id order by ym, category, trig_id, over_id"
                                          #select strftime('%Y',sdate) ym, category, trig_id, over_id, sum(abs(amount*1.0))/100, count(*), (sum(abs(amount*1.0))/100)/count(*) from Entries group by ym, category, trig_id, over_id order by ym, category, trig_id, over_id;

        self.get_yrmo_groups_by_catSQL = "select strftime('%Y',sdate) ym, category, trig_id, over_id, sum(abs(amount*1.0))/100, count(*), (sum(abs(amount*1.0))/100)/count(*) from Entries group by ym, category, trig_id, over_id order by category, ym, trig_id, over_id"
        
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
        self.conn.create_function('trigfromid', 1, self.trigfromid)
        self.conn.create_function('overfromid', 1, self.overfromid)
        self.num_entries = 0
        self.num_predictions = 0
        self.load_entries()
        self.load_categories()
        self.load_triggers()
        self.load_overrides()
        self.load_predictions()
        
        self.sanity_check_db()  # todo remove after dev is done
        
    def add_account(self, name):
        """This function add new account records. This function is not used yet. We'll see if I
           ever decide to support more that one account."""
        try:
            self.conn.execute(self.insertAccountSQL, (name, today, today, ''))
            self.commit()
            self.accounts.append(name)
            return True
        except sqlite3.Error as e:
            self.error('Could not create new Account record:\n', e.args[0])
            return False
        
    def add_cat(self, catStr):
        """Add a new category to the list of categories."""
        try:
            if catStr in self.cat_to_oid:
                self.error("Failed to add Category '{0}'".format(catStr), 'It already exists.')
                return False
            else:
                cur = self.conn.execute(self.insertCatSQL, (catStr, None))
                self.commit()
                last_id = cur.lastrowid     # use the last rowid to set entry in cat_to_oid dictionary
                self.categories[catStr] = Category((last_id, catStr, None ))
                self.cat_to_oid[catStr] = last_id                     
                return True
        except sqlite3.Error as e:
            self.error('Could not save category in Category table:\n', e.args[0])
            return False
            
        
    def add_entry(self, ent):
        """Add a new entry to the list of entries."""
        try:
            self.conn.execute(self.insertEntrySQL, (ent.category, ent.cat_id, ent.trig_id, ent.over_id, ent.date, ent.amount.value, ent.checknum, ent.cleared, ent.desc))
            self.commit()
            self.entries.append(ent)
            return True
        except sqlite3.Error as e:
            self.error('Could not save entries in Entries table:\n', e.args[0])
            return False
       
            
    def add_override(self, over, cat):
        """Add an override to the to the override list. Also add an entry for this override to the
        over_to_oid dictionary."""
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
            
    def add_prediction(self, pred):
        """Add a prediction to the predictions table and the list."""
        try:
            assert(type(pred.cycle) == PCycle)
            #row = (pred.amount.value, pred.income, pred.cat, pred.trig, pred.over, pred.cat_id, pred.trig_id, pred.over_id, pred.p_type, pred.cycle.ctype, pred.cycle.ddate, pred.cycle.vdate, pred.desc)
            row = (pred.amount.value, pred.income, pred.cat, pred.trig, pred.over, pred.cat_id, pred.trig_id, pred.over_id, pred.cycle.ctype, pred.cycle.ddate, pred.cycle.vdate, pred.desc)
            for mem in row:
                print (type(mem))
                print (mem)
            self.conn.execute(self.insertPredictionSQL, row)
            self.commit()
            self.predictions.append(pred)
            return True
        except sqlite3.Error as e:
            self.error('Could not save prediction in Predictions table:\n', e.args[0])
            return False
       
    #def add_filtered_entry(self, ent):
    #    self.filtered_entries.append(ent)
    
    def add_ncf_entry(self, ent):
        """Adds a new entry just read from a checkfile in the checkfile dialog. Entries are held in this
        'New Check File' list until accepted bythe user."""
        self.ncf_entries.append(ent)
        
    def add_trigger(self, trig, cat):
        """Add a new trigger string to the trigger list and make a new oid for it."""
        try:
            if trig in self.trig_to_oid:
                self.error("Failed to add Trigger '{0}'".format(trig), 'It already exists.')                
                return False    #TODO If we forgot to select the trigger string, don't crash
            cur = self.conn.execute(self.insertTrigsSQL, (trig, cat))
            self.commit()
            last_id = cur.lastrowid
            self.triggers[trig] = Trigger((last_id, trig, cat))
            self.trig_to_oid[trig] = last_id
            return True
        except sqlite3.Error as e:
            self.error('Could not save triggers in Triggers table:\n', e.args[0])
            return False
            
        
    def backup(self, backup_name):
        copyfile(self.dbname, backup_name)

    def cat_from_desc(self, desc):
        """Scan the overrides and the triggers to see if any of them are matched in the passed description
        string. We scan the overrides first to give them priority over ny matches from th trigger list."""
        for over, override in self.overrides.items():
            if over in desc:
                return (override.cat, self.cat_to_oid[override.cat], 0, self.over_to_oid[override.over])
            
        for trig, trigger in self.triggers.items():
            if trig in desc:
                print(trigger.cat, self.cat_to_oid[trigger.cat], self.trig_to_oid[trigger.trig], 0)
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

    #def clear_fltered(self):
    #    self.filtered_entries = []
        
    
    def clear_ncf_entries(self):
        """Remove any entries from the ncf list. Called from the checkfile dialog just
        before reading a new file."""
        self.ncf_entries = []
        
    def cleanup(self):
        try:
            self.conn.execute(self.deleteOldEntriesSQL)
            self.commit()
            return True
        except sqlite3.Error as e:
            self.error("An error occurred when deleting from "+tableName+" table:\n", e.args[0])
            return False  

    def commit(self):
        """Used by are functions that perform an operation on the SQLite database."""
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

    def create_table(self, sql, tableName):  #deprecated
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
        """Future. Not used."""
        self.accts.createAccount(name)
        
    
    def delete_category_only(self, lose_cat):
        """Remove only the requested category. Used by other fuction that chase category relationships
        as well."""
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
        """This function changes the category of all entries in db that match the passed trigger and cat string
        to 'None'. It also changes that cat_id and trig_id of all matching entries in the entries list and
        filtered entry list. Finally, it deletes the trigger from the db and the triggers list."""
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
                if ent.category == trigup[1] and trig in ent.desc:  # TODO
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
        """This function deletes an override from the override table and the override list."""
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
        """This function changes the category of all entries in db that match the passed override and cat string
        to 'None'. It also changes that cat_id and over_id of all matching entries in the entries list and
        filtered entry list. Finally, it deletes the override from the db and the override list."""
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
        """delete_trigger_only -- Deletes the passed trigger from the trigger table and trigger list."""
        if trig not in self.triggers:
            return False
        try:
            self.conn.execute(self.deleteTrigSQL, (self.triggers[trig].oid, ))
            
            del self.triggers[trig]
            self.commit()
        except sqlite3.Error as e:
            self.error('Could not delete Trigger:')
            return False
            
    def dump_predictions(self):
        """Debug function. Prints the predictions list."""
        for pred in self.predictions:
            pred.dump()

    def error(self, msg, reason):
        """error -- common error display function used by most database functions. Simply puts up
        a message box for now. Could add logging here."""
        msgBox = QMessageBox()
        msgBox.setWindowTitle('Error!')
        msgBox.setText(msg+'\n'+reason)
        #msgBox.setDetailedText(reason)
        #msgBox.addButton(QtGui.QPushButton('Accept'), QtGui.QMessageBox.YesRole)
        #msgBox.addButton(QtGui.QPushButton('Reject'), QtGui.QMessageBox.NoRole)
        #msgBox.addButton(QtGui.QPushButton('Cancel'), QtGui.QMessageBox.RejectRole)
        self.retval = msgBox.exec_()
        
    
    def find_all_related_to_cat(self, catstr):
        """Finds all overrides, triggers that define a category and all entries that have been
        set to this category. Used by the delete and change category feature of the manage
        categories dialog."""
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
        """Finds all entries that have been categorized by this trigger. Used by the change and delete
        functions of the manage categories dialog."""
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
    
    def find_pred_similar_to(self, entry):
        """Search for existing predictions that are similar to the pne we are about to create."""
        affected = []
        for pred in self.predictions:
            if pred.amount.value == entry.amount.value and pred.category == entry.category and \
               pred.trigger == entry.trigger:
                affected.append('<Prediction>'+pred.str())
        return affected
    
    def find_pred_by_oid(self, oid):
        """SEarch the predictions list for a prediction with the requested oid."""
        for pred in self.predictions:
            if pred.oid == oid:
                return pred
        return None
    
    def find_all_related_to_over(self, cur_over, new_over):
        """Find any entries that have the passed current override's id and categry. Also find any entries
        whose description contains the new override string. Also check that the new override string is
        not already defined as an override. The sum of these is to total effect of creating the new
        override."""
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
        """Returns a list of all entries that contain the passed trig string. Used in manage preditions dialog."""
        affected = []
        for entry in self.entries:
            if trig in entry.desc:
                affected.append('<Entry>'+entry.asCategorizedStr())
        return affected

    def find_all_with_trigger_or_override(self, trigger, override):
        """Returns a list of entries that contain either the passed trigger string or override string."""
        affected = []
        
        if override:
            for entry in self.entries:
                if override in entry.desc:
                    affected.append('<Entry>'+entry.asCategorizedStr())
        if trigger:
            affected.extend(self.find_all_with_trigger(trigger))
        
        return affected
        
    def get_all_accounts(self):
        """Not currently used. Perhaps accounts will become important later."""
        acct_list = []
        try:
            for row in self.conn.execute(self.accts.selectAllSQL):
                acct_list.append(row)
        except sqlite3.Error as e:
            self.error('Error loading memory from the Accounts table:\n', e.args[0])
        return acct_list
    
    def get_all_cats(self):
        """Used in the main window and the check file dialog to populate the category listboxes."""
        if len(self.categories) == 0:
            self.load_categories()
        return self.categories
    
    def get_all_entries(self, which):
        """Return either the list of all entries or the Results list, create by th last search predicate.
        The passed 'which' indicated which list to return."""
        if which == common_ui.All:
            self.filtered_entries = self.entries
            return self.entries
        elif which == common_ui.Results:
            return self.filtered_entries
        
    def get_all_entries_meeting(self, which, op, value):
        """This is the main way the Results list gets built. The op and value define the comparison
        criteria for this search. This search can be run all entries or the set of entries produced by
        the last seach. That feature is controlled by which."""
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
        """Search results list or the all entries list, returning entries having the requested cat."""
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
        """Search all entries or current result list for entries in the requested data range."""
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
        """Return all predictions in the predictions list."""
        return self.predictions
    
    def get_all_predictions_with_date_filter(self, filter_str):
        """Return a list of preditions meeting the requested date filter."""
        requested = []
        today = datetime.date.today()
        for pred in self.predictions:
            #Cycles{'None': 0, 'Monthly': 1, 'Weekly': 2, 'Quarterly': 3, 'Annual': 4, 'BiWeekly': 5, 'Adhoc': 6})
            #['DayOfWeek', 'DayOfMonth', 'Month\Day', 'NextWeek', 'NextMonth']
            ctype = pred.cycle.ctype
            if ctype == Cycles['Weekly'] and filter_str == common_ui.date_sort[0]:    #DayOfWeek
                requested.append(pred)
            elif ctype == Cycles['Monthly'] and filter_str == common_ui.date_sort[1]:    #DayOfMonth
                requested.append(pred)
            elif filter_str == common_ui.date_sort[2] and (ctype == Cycles['Quarterly'] or ctype == Cycles['Annual'] or ctype == Cycles['BiWeekly'] or ctype == Cycles['Adhoc']):
                requested.append(pred)
            elif filter_str == common_ui.date_sort[3] and pred.in_next_week(today):
                requested.append(pred)
            elif filter_str == common_ui.date_sort[4] and pred.in_next_month(today):
                requested.append(pred)
            elif filter_str == common_ui.date_sort[5] and pred.in_three_month(today):
                requested.append(pred)
        return requested
    
    def get_all_predictions_meeting(self, op, value):
        """Return a list of prdictions that the comparison predict decribed by op and value."""
        requested = []
        
        for pred in self.predictions:
            if op == CompareOps.MONEY_LESS_THAN:
                if pred.amount < Money.from_str(value):
                    requested.append(pred)
            elif op == CompareOps.MONEY_MORE_THAN:
                if pred.amount > Money.from_str(value):
                    requested.append(pred)
            elif op == CompareOps.MONEY_EQUALS:
                if pred.amount == Money.from_str(value):
                    requested.append(pred)
            elif op == CompareOps.CHECKNUM_EQUALS:
                if pred.checknum == value:
                    requested.append(pred)
            elif op == CompareOps.SEARCH_DESC:
                if value in pred.desc:
                    requested.append(pred)
            else:
                self.error('Failed to build prediction list.', '{0} is an unknown comparison operator.')
        self.filtered_entries = requested
        return requested

    def get_all_predictions_with_cat(self, cat):
        """Return a list of predictions that have the requested category."""
        requested = []
            
        for pred in self.predictions:
            if pred.cat == cat:
                requested.append(pred)
        return requested

    def get_all_predictions_with_cycle(self, cycle):
        """Return a list of predictions that hace the requested cycle value."""
        requested = []
            
        for pred in self.predictions:
            if pred.cycle.get_type_str() == cycle:
                requested.append(pred)
        return requested

    def get_all_predictions_with_over(self, over):
        """Return a list of predictions witht requested override."""
        requested = []
            
        for pred in self.predictions:
            if pred.over == over:
                requested.append(pred)
        return requested

    #def get_all_predictions_with_ptype(self, ptype):
        #requested = []
            
        #for pred in self.predictions:
            #if pred.get_typestr() == ptype:
                #requested.append(pred)
        #return requested
                
    def get_all_predictions_with_trig(self, trig):
        """Return a list of predictions with the requested trigger."""
        requested = []
            
        for pred in self.predictions:
            if pred.trig == trig:
                requested.append(pred)
        return requested
                
    def get_all_triggers(self):
        """Return a dictionary of all triggers in the database."""
        triggers = {}
        try:
            for row in self.conn.execute(self.triggers.selectAllTrigSQL):
                triggers[row[1]] = trigger(row[0], row[1], row[2])  # TODO
        except sqlite3.Error as e:
            self.error('Error loading memory from the Triggers table:\n', e.args[0])
        return triggers
        
    def yrmo(self, d):
        """Returns the year and month from the passed date string. The database init function creates a
        SQL function by this name. This function can be embedded in SQL statements. See the SQLite3 doc
        at python.org. """
        return d[:7]

    def trigfromid(self, id):
        if id in self.trig_to_oid.inv:
            return self.trig_to_oid.inv[id]
        else:
            return 'None'
    
    def overfromid(self, id):
        if id in self.over_to_oid.inv:
            return self.over_to_oid.inv[id]
        else:
            return 'None'

    def get_cat_by_month(self):
        """Get totals of all categories grouped by month"""
        requested = []
        for row in self.conn.execute(self.get_yrmo_groups_by_monSQL):
            trig = self.trigfromid(row[2])
            over = self.overfromid(row[3])
            requested.append((row[0],row[1],trig,over,row[4],row[5],row[6]))
        return requested
    
    def get_month_by_cat(self):
        """Get totals for all months grouped by category"""
        requested = []
        for row in self.conn.execute(self.get_yrmo_groups_by_catSQL):
            trig = self.trigfromid(row[2])
            over = self.overfromid(row[3])
            requested.append((row[0],row[1],trig,over,row[4],row[5],row[6]))
        return requested
        

    def get_ncf_entries(self):
        """Return the new check file entry list."""
        return self.ncf_entries

    #def get_predictions_column_count(self):
    #    """Return the number columns in a prediction. Deprecated."""
    #    #oid,name,cat,trig,over,cat_id,trig_id,over_id,p_type,cycle,pdate,comment
    #    return 8
    
    #def get_recent_entries(self, limit):
    #    assert(False)   # This funcion
    #    if self.num_entries <= limit:
    #        return self.get_all_entries(which)
    #    result = []
    #    today = datetime.date.today()
    #    trial = today - datetime.timedelta(months = 2)
    #    for ent in self.entries:
    #        if ent.date > previous:
    #            howmany += 1
        
    def get_last_three_months(self, today):
        """Returns a list of all entries with dates between today and three months ago.
        Used by the What If window."""
        entries = []
        start = today - datetime.timedelta(weeks=13)
        for ent in self.entries:
            if ent.date >= start and ent.date <= today:
                entries.append(ent)
        return entries
    
    def get_next_three_months(self, today):
        """Returns a list of the predicted entries that will occur betweeen today and three months
        from now."""
        futures = []

        end = today + datetime.timedelta(weeks=13)
        for pred in self.predictions:
            print(pred)
            cycle = pred.cycle
            pcycle = PCycle(cycle.ctype, cycle.ddate, cycle.vdate)
            next_dates = pcycle.future_dates(today, end)
            pred_instance = 0
            for dnext in next_dates:
                oid = (pred.oid * 65336) + pred_instance
                row = (oid, pred.cat, pred.cat_id, pred.trig_id, pred.over_id, dnext, pred.amount.value, '', '', pred.desc)
                pent = entry.Entry(self, row, False)    # pent = predicted entry
                futures.append(pent)
                pred_instance += 1
        futures = sorted(futures, key=lambda ent: ent.date.isoformat())
        return futures
    
    def load_accounts(self):
        """Loads the accounts list from the database. Called by the datbase init function. But there
        are no entries in the account table yet bc there is no UI to create them and no other code
        cares about accounts yet."""
        if len(self.accounts) == 0:
            try:
                self.conn.execute(self.createAcctsSQL)
                for row in self.conn.execute(self.selectAllAcctsSQL):
                    self.accounts.append(accounts.Account(row))
            except sqlite3.Error as e:
                self.error('Error loading memory from the Accounts table:\n', e.args[0])

    def load_categories(self):
        """Loads all categories from the category table into the category dicionary and the cat_to_oid
        dictionary. Called from database init, the main window if it gets going before the database class.
        Also called by the migration functions."""
        if len(self.categories) == 0:
            try:
                self.conn.execute(self.createCatsSQL)
                self.conn.execute(self.insertNoneCatSQL, ('None', 'None'))
                for row in self.conn.execute(self.selectAllCatsSQL):
                    self.categories[row[1]] = Category(row) # TODO
                    self.cat_to_oid[row[index.CAT_NAME]] = row[index.CAT_OID]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Categries table:\n', e.args[0])
                
    def load_entries(self):
        """Loads all entries from the Entries table into the Entries list. Called by the database init."""
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
        """Load all predictions from database table to predictins list."""
        try:
            self.conn.execute(self.createPredictionsSQL)  #TODO remove type
            for row in self.conn.execute(self.selectAllPredictionsSQL):  #TODO remove type
                pred = Prediction(self)
                pred.set_with_list(list(row))
                self.predictions.append(pred)
                self.num_predictions += 1
        except sqlite3.Error as e:
            self.error('Error loading memory from the Predictions table:\n', e.args[0])
                
    def load_overrides(self):
        """Load all overrides from table to ovverrides dictionary and over_to_oid bidict. Called by
        database init and migrate functions."""
        if len(self.overrides) == 0:
            try:
                self.conn.execute(self.createOversSQL)
                for row in self.conn.execute(self.selectAllOversSQL):
                    self.overrides[row[index.OVER_OVER]] = Override(row)  # TODO
                    self.over_to_oid[row[index.OVER_OVER]] = row[index.OVER_OID]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Overrides table:\n', e.args[0])
                
    def load_triggers(self):
        """Load all triggers from table to ovverrides dictionary and over_to_oid bidict. Called by
        database init and migrate functions."""
        if len(self.triggers) == 0:
            try:
                self.conn.execute(self.createTrigsSQL)
                for row in self.conn.execute(self.selectAllTrigsSQL):  # TODO
                    self.triggers[row[index.TRIG_TRIGGER]] = Trigger(row)
                    self.trig_to_oid[row[index.TRIG_TRIGGER]] = row[index.TRIG_OID]
            except sqlite3.Error as e:
                self.error('Error loading memory from the Triggers table:\n', e.args[0])
                
    def merge_ncf_entries(self):
        """Move categorized entries from the new check file list to the entries list and update the
        the database. Uncategorized entries are returned to the new check file."""
        #As entries grows in size, make the search smarter, more code but faster
        not_cats = []
        entry_set = set(self.entries)
        self.ncf_entries.reverse()
        while len(self.ncf_entries):
            temp = self.ncf_entries.pop()
            #assert(temp.oid == 0)  #TODO  doesn't allow for entries that get bc already in db and got modified
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
                version = max(row[1], version)
            if version == 1:
                self.migrate_entries(version)
            return True
        except sqlite3.Error as e:
            self.error('What? ', e.args[0])
            return False
    
    def make_cat_to_override_dict(self):
        """Return a dictionary of categories to override oids. Ued by migrate functions only."""
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
        """Retrn a dictionary of cat to triggers. Used by migrate_entries."""
        self.cat_to_triggers = {}
        for trigger in self.triggers:
            oid = trigger.oid
            cat = trigger.cat
            if cat in self.cat_to_triggers:
                self.cat_to_triggers[cat].append((oid, trigger.trig))
            else:
                self.cat_to_triggers[cat] = [(oid, trigger.trig)]
        
    def migrate_entries(self, old_version):
        """When the database is initialized, the latest version is read from the version table. If this version
        has a match in this function, then appropriate changes are ade to the database. So far, there is a
        migration from 0->1 and 1->2. 0->1 agjusts columns in tth entries tabe and 1->2 adjust columns in the
        predictions table."""
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
            elif old_version == 1:
                self.conn.execute('drop table if exists Predictions2')
                self.conn.execute(self.createPredictions2SQL)
                self.commit()
                #'insert into Predictions(2amount, income, cat, trig, over, cat_id, trig_id, over_id, cycle, ddate, vdate, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                for row in self.conn.execute(self.selectAllPredictionsSQL):
                    newrow = []
                    newrow.append(row[0])
                    newrow.append(row[1])
                    newrow.append(row[2])
                    newrow.append(row[3])
                    newrow.append(row[4])
                    newrow.append(row[5])
                    newrow.append(row[6])
                    newrow.append(row[7])
                    newrow.append(row[8])
                    if row[10] in Cycles:
                        cycleType = Cycles[row[10]]
                    else:
                        cycleType = row[10]
                    newrow.append(cycleType)
                    newrow.append(row[11])
                    newrow.append(row[12])
                    newrow.append(row[13])
                    #insert into Predictions(oid, amount, income, cat, trig, over, cat_id, trig_id, over_id, cycle, ddate, vdate, desc) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                    self.conn.execute(self.migrate2PredictionsSQL, newrow)
                    self.commit()
                #rename the tables
                self.conn.execute('ALTER TABLE Predictions RENAME TO OldPredictions')
                self.conn.execute('ALTER TABLE Predictions2 RENAME TO Predictions')
                self.conn.execute('INSERT OR REPLACE INTO Version(version_str, version_int) VALUES ("V0.2", 2)')
                self.commit()
                
        except sqlite3.Error as e:
            self.error('Migration error 1: ', e.args[0])
            return False
        
    def name(self):
        """Returns the database's name. Used to create the file name for the database."""
        return self.dbname
    
    def oid_for_over(self, over):
        """Returns an override's oid, if it is in the dictionary, else returns -1. Used for columns
        values in the main window and the what if window."""
        if over in self.over_to_oid:
            return self.over_to_oid[over]
        else:
            return -1
        
    def oid_for_trig(self, trig):
        """Returns a trigger's oid, if it is in the dictionary, else returns -1. Used for columns
        values in the main window and the what if window."""
        if trig in self.trig_to_oid:
            return self.trig_to_oid[trig]
        else:
            return -1
        
    def trig_for_oid(self, oid):
        """Given an oid, return the trigger with that oid. Used in the main window and th what if window."""
        if oid in self.trig_to_oid.inv:
            return self.trig_to_oid.inv[oid]
        else:
            assert(False)
            
    #def open(self, name, deprecated):  #deprecated
        #self.dbname = name
        #conn = sqlite3.connect(name+'.db')
        #self.conn = conn
        #self.accts = accounts.AccountList(self)
        #self.entries = entry.EntryList(self)
        #self.categories = Category(self)
        #self.triggers = trigger.Trigger(self)
        #self.overrides = override.Override(self)
        ##self.createTables()
        #self.convertPicklesToDB()
        #self.conn.commit()
        
    def overs_for_cat(self, lookFor):
        """Return a list overrides that have the requested cat. Most of the time this will be an EMPTY
        list, as there are not that many overrides."""
        overs = []
        for over, override in self.overrides.items():
            if override.cat == lookFor:
                overs.append(override)
                
        return overs

    def rename_category_all(self, current_cat, new_cat):
        """Renames an existing category in all places where categories are recorded. That includes
        overrides, triggers and entries. The new category is add to the cat table and list and the
        old name is removed."""
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
        """Rename an existing ovrride to a new string in all places it is recorded. This includes """
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
        """Change a trigger from one string to another string. This requires that entries with the
        old trigger string be checked for the new trigger string. If the entry has the new string, then its
        category remains the same. If the entry does not have the new string, then it's category is changed
        to 'None'."""
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
                if type(ent[6]) != int:
                    self.error("ent[6] is not str", ent[6])
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
    
    #def restore(self, name):  #deprecated
        #assert(False)
        #self.dbname = name
        ##todo: develop strategy for managing backup and restore naming
        #conn = sqlite3.connect(name+'.db')
        #self.conn = conn
        #self.accts = accounts.AccountList(self, STORE_PCKL)
        #self.accts.save(STORE_DB)
        #self.entries = entry.EntryList(self, STORE_PCKL)
        #self.entries.save(STORE_DB)
        #self.categories = Category(self, STORE_PCKL)
        #self.categories.save(STORE_DB)
        #self.triggers = trigger.Trigger(self, STORE_PCKL)
        #self.triggers.save(STORE_DB)
        #self.overrides = override.Override(self, STORE_PCKL)
        #self.overrides.save(STORE_DB)
        #self.conn.commit()
        
    
    def save(self, storage):  #deprecated
        assert(False)
        print("Database.save is OBSOLETE")
        #self.categories.save(storage)
        #self.triggers.save(storage)
        #self.overrides.save(storage)
        #self.entries.save(storage)

    def sanity_check_db(self):
        """When the database is initialized, this function is called. The followig hecks are made:
        1) First check that every override refers to a category that exists.
        2) Check that all triggers refer to a category that exists.
        3) Check that all categories have a least one trigger or overrides
        4) Check that all entries have a category that exist and that their description contains a trigger
           or override that belongs to that category. Remember, overrides first.
        """
        # first check that every override refers to a category that exists
        for over, override in self.overrides.items():
            if override.cat in self.cat_to_oid:
                print('Override: '+override.over+' Category: '+override.cat+' is GOOD.')
            else:
                print('Override: '+override.over+' Missing Cat: '+override.cat+' is BAD BAD.')
                assert(False)
                
        # check that all triggers refer to a category that exists
        for trig, trigger in self.triggers.items():
            if trigger.cat in self.cat_to_oid:
                print('Trigger: '+trigger.trig+' Category: '+trigger.cat+' is GOOD.')
            else:
                print('Trigger: '+trigger.trig+' Missing Cat: '+trigger.cat+' is BAD BAD.')
                assert(False)
            
        # check that all categories have a least one trigger or overrides
        for cat, category in self.categories.items():
            if cat == 'None':
                continue
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
                print("Category: "+category.cat+" has no triggers or overrides.  BAD BAD. Adding Nada trigger")
                self.add_trigger('None', cat)
                #assert(False)   #TODO  Have it put in a NADA trigger
        # check that all entries have a category that exist and that their description contains a trigger
        # or override that belongs to that category. Remember, overrides first.
        for ent in self.entries:
            got_one = False
            if ent.category not in self.cat_to_oid:
                print("Entry: "+ent.asCategorizedStr() + " No category. BAD BAD.")
                assert(False)
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
                #assert(False)

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
                trig_list.append(trigger)
                
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
                    ent.category = new_id  #TODO: looks like a type mis-match here
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
        
    def update_prediction(self, lst):
        try:
            sql_list = []
            sql_list = sql_list + lst
            oid = sql_list.pop(0)
            sql_list.append(oid)
            cur = self.conn.execute(self.updatePredictionSQL, sql_list)
            self.commit()
            for pred in self.predictions:
                if pred.oid == oid:
                    pred.update_with_list(lst)
            return True
        except sqlite3.Error as e:
            self.error("Error while updating prediction.", e.args[0])
            return False
        
    def delete_prediction(self, oid):
        try:
            self.conn.execute(self.deletePredictionSQL, (oid, ))
            self.commit()
            for i in range(len(self.predictions)):
                if self.predictions[i].oid == oid:
                    del self.predictions[i]
                    break
            return True
        except sqlite3.Error as e:
            self.error("Error while deletingprediction.", e.args[0])
            return False
            