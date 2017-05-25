"""Accounts class holds all the data for and account, duh"""

import category
import trigger
import override
import entry
from datetime import date
import sqlite3

# storage defines
ACCT_DB = 1
ACCT_PCKL = 2

class Account(object):

    def __init__(self, name, start, last, url):
        self.name = name
        self.start = start
        self.last = last
        self.bankurl = url
        pass
    
    def convertPickleToDB(self):
        self.categories.load(ACCT_PCKL)
        self.categories.save(ACCT_DB)
        self.triggers.load(ACCT_PCKL)
        self.triggers.save(ACCT_DB)
        self.overrides.load(ACCT_PCKL)
        self.overrides.save(ACCT_DB)
        self.entries.load(ACCT_PCKL)
        self.entries.save(ACCT_DB)

    def load(self, storage):
        self.categories.load(storage)
        self.triggers.load(storage)
        self.overrides.load(storage)
        self.entries.load(storage)
        
    def save(self, storage):
        self.categories.save(storage)
        self.triggers.save(storage)
        self.overrides.save(storage)
        self.entries.save(storage)
        
    def mergeNewEntries(self, newList):
        for newEntry in newList:
            if not self.entries.isDupe(newEntry):
                self.entries.entrylist.append(newEntry)
        
    def removeCategory(catStr):
        pass
        
class AccountList(object):
    
    def __init__(self, db):
        self.acct_list = []
        self.db = db
        self.createSQL = 'create table if not exists Accounts(id integer primary key, name varchar(30), start date, last date, bankurl varchar(255))'
        self.insertSQL = 'insert into Accounts(name, start, last, bankurl) VALUES (?,?,?,?)'
        
    def createTable(self):
        try:
            self.db.conn.execute(self.createSQL)
            return True
        except sqlite3.Error as e:
            self.db.error("An error occurred when creating the AccountList table:\n", e.args[0])
            return False            
    
    def createAccount(self, name):
        today = date.today()
        self.acct_list.append(Account(name, today, today, ''))
        try:
            self.db.conn.execute(self.insertSQL, (name, today, today, ''))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            self.db.error('Could not create new Account record:\n', e.args[0])
            return False