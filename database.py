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

class Database(object):
    
    def __init__(self):
        self.accts = accounts.Account(acct_str)
        pass
    
    def open(self, name):
        self.dbname = name + '.db'
        conn = sqlite3.connect(name+'.db')
        self.conn = conn
        self.accts = accounts.AccountList(self)
        self.entries = entry.EntryList(self)
        self.categories = category.Category(self)
        self.triggers = trigger.Trigger(self)
        self.overrides = override.Override(self)
        self.createTables()
        
    def createTables(self):
        try:
            self.accts.createTable()
            self.entries.createTable()
            self.categories.createTable()
            self.triggers.createTable()
            self.overrides.createTable()
            #conn.execute("create table if not exists Accounts(oid INTEGER PRIMARY KEY ASC, name varchar(30), start date, last date, bankurl varchar(255))")
            #conn.execute("create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), edate date, amount int, checknum int, cleared boolean, desc varchar(255))")
            conn.execute("create table if not exists Categories(oid INTEGER PRIMARY KEY ASC, name varchar(20), super varchar(20))")
            conn.execute("create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(30), category varchar(20))")
            conn.execute("create table if not exists Overrides(oid INTEGER PRIMARY KEY ASC, override varchar(30), category varchar(20))")
            return True
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])
            return False