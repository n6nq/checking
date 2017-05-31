"""Check entry --- one entry for each transaction on the account"""
import datetime
from money import Money
from category import Category
from trigger import Trigger
import database
import sqlite3
import pickle

class EntryList(object):
    
    def __init__(self, db):
        #self.n_entries = 0
        self.entrylist = []
        self.db = db
        self.createSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), edate date, amount int, checknum int, cleared boolean, desc varchar(255))'
        self.selectAllSQL = 'select oid, category, edate, amount, checknum, cleared, desc from Entries'
        self.insertSQL = 'insert into Entries{category, edate, amount, checkum, cleared, desc} values(?, ?, ?, ?, ?, ?)'

        #todo: decide about pickle files
        #self.picklename = acct_str + '_entrylist.pckl'

    def createTable(self):
        try:
            self.db.conn.execute(self.createSQL)
            return True
        except sqlite3.Error as e:
            self.db.error("An error occurred when creating the EntryList table:\n", e.args[0])
            return False            
        

    def isDupe(self, newEtry):
        for entry in self.entrylist:
            if entry.compare(newEtry):
                return True
        return False
        
    def load(self, storage):
        self.entrylist = []
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.dbname+'_entrylist.pckl', 'rb')
                self.strings = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No entrylist.pckl file.')
        elif storage == database.STORE_DB:
            try:
                for row in self.db.conn.execute(self.selectAllSQL):
                    self.entrylist.append((row[1], row[2], row[3], row[4], row[5], row[6]))
            except sqlite3.Error as e:
                self.db.error('Error loading memory from the EntryList table:\n', e.args[0])
        self.n_entries = len(self.entrylist)

    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.db.dbname+'_entrylist.pckl', 'wb')
            pickle.dump(self.strings, f)
            f.close()
        elif storage == database.STORE_DB:
            try:
                for entry in self.entrylist:
                    self.db.conn.execute(self.insertSQL, (entry[1], entry[2], entry[3], entry[4], entry[5], ntry[6]))
            except sqlite3.Error as e:
                self.db.error('Could not save entries in EntryList table:\n', e.args[0])
        
class Entry(database.DBObj):

    def __init__(self, db, date, amount, cleared, checknum, desc):
        self.db = db
        dparts = date.split('/')
        self.date = datetime.date(int(dparts[2]), int(dparts[0]), int(dparts[1]))
        self.amount = Money(amount)
        self.cleared = (cleared == '*')
        if len(checknum) == 0:
            self.checknum = 0
        else:
            self.checknum = int(checknum)
        self.desc = desc
        self.category = self.db.triggers.fromDesc(desc)
        
    def compare(self, newEntry):
        if (self.date - newEntry.date).total_seconds() == 0:
            if self.amount.value == newEntry.amount.value:
                if self.desc == newEntry.desc:
                    return True
        return False
            
    def asNotCatStr(self):
        retstr = self.date.strftime("%m/%d/%y") + ' ' + \
            self.amount.asStr() + ' ' + \
            '<' + '{}'.format(int(self.checknum)) + '> ' + \
            self.desc
        return retstr
    
    def asCategorizedStr(self):
        return self.category + ' ' + self.asNotCatStr()
    
    def isMatch(self, line):
        thisStr = self.asNotCatStr()
        if thisStr in line:
            return True
        return False