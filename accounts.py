"""Accounts class holds all the data for an account, duh"""

import database
import dbrow
import category
import trigger
import override
import entry
from datetime import date
import sqlite3


class Account(dbrow.DBRow):
    """ACCOUNT - The account class holds values for identifyng an account to the user
    and to the bank. As of 08/13/2018 none of these values are not used for anything
    as the Account class has no user interface. Current UI to the bank is simply to
    download csv file from the bank and use the read check file interface. This may
    be the only way to interface with the bank, as they become more security aware.
    Possible members are:
    name -- user supplied name for the account, such as checking, savings, xyz card
    start -- starting balance probably
    last -- last known balance or date?
    bankurl -- address for accessing the bank interface
    state -- is the account dirty or saved"""
    def __init__(self, name, start, last, url):
        self.name = name
        self.start = start
        self.last = last
        self.bankurl = url
        self.state = dbrow.DIRTY
        pass
    
        
class Accounts(object):
    """Accounts (deprecated)-- currently a list in the database class. Database
       interface in the Database class.     
       (old)is an interface between a database table and a memory cache holding
       records of account data. This class woould be used if the program ever gets an
       account UI and bank interface."""
    def __init__(self, db):
        """decrepated"""
        assert(False)
        self.db = db
        self.createSQL = 'create if not exists Accounts(id integer primary key, name varchar(30) unique, start date, last date, bankurl varchar(255))'
        self.insertSQL = 'insert into Accounts(name, start, last, bankurl) VALUES (?,?,?,?)'
        self.selectAllSQL = 'select oid, name, start, last, bankurl from Accounts'
        db.create_table(self.createSQL, 'Account')
        #self.load(storage)
           
#    def load(self, storage):
#        """deprecated"""
#        assert(False)
#        if storage == database.STORE_PCKL:
#            try:
#                f = open(self.db.name()+'_accounts.pckl', 'rb')
#                self.cache = pickle.load(f)
#                f.close()
#            except FileNotFoundError:
#                print('No accounts.pckl file.')
#        elif storage == database.STORE_DB:
#            self.cache = self.db.get_all_accounts()

    #def createAccount(self, name):
        #"""deprecated"""
        #assert(False)
        #today = date.today()
        #self.cache.append(Account(name, today, today, ''))
        #self.db.addAccount((name, today, today, ''))
