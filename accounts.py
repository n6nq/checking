"""Accounts class holds all the data for and account, duh"""

import database
import dbrow
import category
import trigger
import override
import entry
from datetime import date
import sqlite3


class Account(dbrow.DBRow):

    def __init__(self, name, start, last, url):
        self.name = name
        self.start = start
        self.last = last
        self.bankurl = url
        self.state = dbrow.DIRTY
        pass
    
#    def load(self, storage):
#        self.categories.load(storage)
#        self.triggers.load(storage)
#        self.overrides.load(storage)
#        self.entries.load(storage)
        
#    def save(self, storage):
#        self.categories.save(storage)
#        self.triggers.save(storage)
#        self.overrides.save(storage)
#        self.entries.save(storage)
        
#    def mergeNewEntries(self, newList):
#        for newEntry in newList:
#            if not self.entries.isDupe(newEntry):
#             self.entries.entrylist.append(newEntry)
        
#    def removeCategory(catStr):
#        pass
        
class Accounts(object):
    
    def __init__(self, db):
        self.cache = []
        self.db = db
        self.createSQL = 'create table if not exists Accounts(id integer primary key, name varchar(30) unique, start date, last date, bankurl varchar(255))'
        self.insertSQL = 'insert into Accounts(name, start, last, bankurl) VALUES (?,?,?,?)'
        self.selectAllSQL = 'select oid, name, start, last, bankurl from Accounts'
        db.create_table(self.createSQL, 'Account')
        #self.load(storage)
           
    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.name()+'_accounts.pckl', 'rb')
                self.cache = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No accounts.pckl file.')
        elif storage == database.STORE_DB:
            self.cache = self.db.get_all_accounts()

    def createAccount(self, name):
        today = date.today()
        self.cache.append(Account(name, today, today, ''))
        self.db.addAccount((name, today, today, ''))
