"""Check entry --- one entry for each transaction on the account"""
import database
import dbrow
import datetime
from money import Money
#from category import Category
from trigger import Trigger
import sqlite3
import pickle

class Entries(object):
    
    def __init__(self, db):
        #self.n_entries = 0
        self.cache = []
        self.db = db
        self.createSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), sdate date, amount int, cleared boolean, checknum int, desc varchar(255))'
        self.selectAllSQL = 'select oid, category, sdate, amount, cleared, checknum, desc from Entries'
        self.insertSQL = 'insert into Entries(category, sdate, amount, cleared, checknum, desc) values(?, ?, ?, ?, ?, ?)'
        self.updateCatSQL = 'update Entries set category = ? where category = ?'
        db.create_table(self.createSQL, 'Entries')  #TODO: maybe skip if temp_entries
        #self.load(storage)   load after it's created

    def del_cat(self, cat):
        pass
    
    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.name()+'_entrylist.pckl', 'rb')
                self.cache = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No entrylist.pckl file.')
        elif storage == database.STORE_DB:
            self.cache = self.db.get_all_entries()
            
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
            f = open(self.db.name()+'_entrylist.pckl', 'wb')
            pickle.dump(self.strings, f)
            f.close()
        elif storage == database.STORE_DB:
            self.db.addEntryList(self.entrylist)
        
class Entry(dbrow.DBRow):
    
    @classmethod
    def no_cat(cls):
        return 0
    
    @classmethod
    def categorize(cls):
        return 1
    
    @classmethod
    def only_none(cls):
        return 2
    
    def __init__(self, db, row, how_to_cat):
        self.db = db
        self.oid = row[0]
        self.category = row[1]
        self.date = row[2]
        self.amount = Money.from_number(row[3])
        self.cleared = row[5]
        self.checknum = row[4]
        self.desc = row[6]
        if how_to_cat == Entry.categorize():
            self.category = self.db.cat_from_desc(self.desc)
            
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
        
    def __eq__(self, other):
        return ((self.date - other.date).total_seconds() == 0 and \
           self.amount.value == other.amount.value and \
           self.desc == other.desc)
    
    def __ne__(self, other):
        return (self.date != other.date or \
           self.amount.value != other.amount.value or \
           self.desc != other.desc)

    def asNotCatStr(self):
        if self.checknum == 0:
            checknum_str = '    '
        else:
            checknum_str = '{}'.format(self.checknum) 

        retstr = self.date.strftime("%m/%d/%y") + '\t' + \
            self.amount.as_str() + '\t' + \
            checknum_str + '\t' + \
            self.desc
        return retstr
    
    def asCategorizedStr(self):
        if self.category == None:
            cat_str = 'None'
        else:
            cat_str = self.category
        return cat_str + '\t' + self.asNotCatStr()
    
    def isMatch(self, line):
        thisStr = self.asNotCatStr()
        if thisStr in line:
            return True
        return False