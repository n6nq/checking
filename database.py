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
STORE_DB = 1
STORE_PCKL = 2

class Database(object):

    def __init__(self):
        pass
    
    def error(self, msg):
        print (msg)     #TODO make ui for error messages  
        
    def commit(self):
        self.conn.commit()
        
    def open(self, name):
        self.dbname = name
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self)
        self.entries = entry.EntryList(self)
        self.categories = category.Category(self)
        self.triggers = trigger.Trigger(self)
        self.overrides = override.Override(self)
        self.createTables()
        self.convertPicklesToDB()
        self.conn.commit()
        
    def createTables(self):
        try:
            self.accts.createTable()
            self.entries.createTable()
            self.categories.createTable()
            self.triggers.createTable()
            self.overrides.createTable()
            return True
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])
            return False
        
    def createAccount(self, name):
        self.accts.createAccount(name)
        
    def convertPicklesToDB(self):
        self.categories.load(STORE_PCKL)
        self.categories.save(STORE_DB)
        self.triggers.load(STORE_PCKL)
        self.triggers.save(STORE_DB)
        self.overrides.load(STORE_PCKL)
        self.overrides.save(STORE_DB)
        self.entries.load(STORE_PCKL)
        self.entries.save(STORE_DB)

    def mergeNewEntries(self, newList):
        for newEntry in newList:
            if not self.entries.isDupe(newEntry):
                self.entries.entrylist.append(newEntry)
    
    