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

class Database(object):
    
    def __init__(self, name):
        
        self.dbname = name + '.db'
        self.conn = sqllite3.open(name+'.db')
        self.createTables()
        
    def createTables(self):
        try:
            conn = self.conn
            conn.execute("create table if not exists Accounts(oid INTEGER PRIMARY KEY ASC, name varchar(), start date, last date, bankurl varchar())")
            conn.execute("create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(), when date, , amount int, checknum int, cleared boolean, desc varchar())")
            conn.execute("create table if not exists Categories(oid INTEGER PRIMARY KEY ASC, name varchar(), super varchar())")
            conn.execute("create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(), category varchar())")
            conn.execute("create table if not exists Overrides(oid INTEGER PRIMARY KEY ASC, override varchar(), category varchar())")
            return True
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])
            return False