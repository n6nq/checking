"""Check entry --- one entry for each transaction on the account"""
import database
import dbrow
import datetime
from money import Money
#from category import Category
from trigger import Trigger
import sqlite3
import pickle

class EntryList(object):
    
    def __init__(self, db, storage):
        #self.n_entries = 0
        self.entrylist = []
        self.db = db
        self.createSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), sdate text, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.selectAllSQL = 'select oid, category, sdate, amount, cleared, checknum, desc from Entries'
        self.insertSQL = 'insert into Entries(category, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?)'
        db.createTable(self.createSQL, 'Entries')
        self.load(storage)

        #todo: decide about pickle files
        #self.picklename = acct_str + '_entrylist.pckl'

    def load(self, storage):
        self.entrylist = []
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.dbname+'_entrylist.pckl', 'rb')
                self.entrylist = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No entrylist.pckl file.')
        elif storage == database.STORE_DB:
            try:
                for row in self.db.conn.execute(self.selectAllSQL):
                    #todo: convert all query results to objects
                    #oid category date amount cleared checknum desc
                    #todo: consider re-assessing all 'None' entries
                    self.entrylist.append(Entry(self.db, row), Entry.NO_CAT)
            except sqlite3.Error as e:
                self.db.error('Error loading memory from the EntryList table:\n', e.args[0])
        self.n_entries = len(self.entrylist)

    #def createTable(self):
    #    try:
    #        self.db.conn.execute(self.createSQL)
    #        return True
    #    except sqlite3.Error as e:
    #        self.db.error("An error occurred when creating the EntryList table:\n", e.args[0])
    #        return False            
        

    def isDupe(self, newEtry):
        for entry in self.entrylist:
            if entry.compare(newEtry):
                return True
        return False
        
    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.db.dbname+'_entrylist.pckl', 'wb')
            pickle.dump(self.strings, f)
            f.close()
        elif storage == database.STORE_DB:
            try:
                for entry in self.entrylist:
                    cur = self.db.conn.cursor()
                    cur.execute(self.insertSQL, (entry.category, entry.date, entry.amount.value, entry.checknum, entry.cleared, entry.desc))
            except sqlite3.Error as e:
                self.db.error('Could not save entries in EntryList table:\n', e.args[0])
        
class Entry(dbrow.DBRow):
    NO_CAT = 0
    CATEGORIZE = 1
    ONLY_NONE = 2
    
    def __init__(self, db, row, how_to_cat):
        self.db = db
        self.oid = row[0]
        self.category = row[1]
        self.date = row[2]
        self.amount = row[3]
        self.cleared = row[4]
        self.checknum = row[5]
        self.desc = row[6]
        if how_to_cat == Entry.CATEGORIZE:
            self.category = self.db.triggers.fromDesc(self.desc)
            
#oid  cat  datestr amtstr  clr*    chknum''  desc
#    def __init__(self, db, date, amount, cleared, checknum, desc):
#        self.db = db
#        dparts = date.split('/')
#        self.date = datetime.date(int(dparts[2]), int(dparts[0]), int(dparts[1]))
#        self.amount = Money(amount)
#        self.cleared = (cleared == '*')
#        if len(checknum) == 0:
#            self.checknum = 0
#        else:
#            self.checknum = int(checknum)
#        self.desc = desc
#        self.category = self.db.triggers.fromDesc(desc)
        
    def compare(self, newEntry):
        if (self.date - newEntry.date).total_seconds() == 0:
            if self.amount.value == newEntry.amount.value:
                if self.desc == newEntry.desc:
                    return True
        return False
            
    def asNotCatStr(self):
        retstr = self.date.strftime("%m/%d/%y") + ' ' + \
            self.amount.as_str() + ' ' + \
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