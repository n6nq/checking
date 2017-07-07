"""Check entry --- one entry for each transaction on the account"""
import database
import dbrow
import datetime
from money import Money
#from category import Category
from trigger import Trigger
import sqlite3
import pickle

class Entrys(object):
    
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

        #todo: decide about pickle files
        #self.picklename = acct_str + '_entrylist.pckl'

    def del_cat(self, cat):
        pass
    
    def change_cat_of_entries(self, current, new, do_db):
        list_affected = 0
        for entry in self.entrylist:
            if entry.category == current:
                entry.category = new
                list_affected += 1
        if do_db:
            db_affected = self.db.updateEntriesCats(current, new)
            if db_affected != list_affected:
                self.db.error('Update error. {} rows affected in database, but {} affected entries in the list.\n'.format(db_affected, list_affected))

    def load(self, storage):
        entries = []
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.name()+'_entrylist.pckl', 'rb')
                entries = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No entrylist.pckl file.')
        elif storage == database.STORE_DB:
            for row in self.db.get_all_entries():
                entries.append(Entry(self.db, row, Entry.no_cat()))
        self.n_entries = len(entries)
        return entries
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
        self.amount = row[3]
        self.cleared = row[4]
        self.checknum = row[5]
        self.desc = row[6]
        if how_to_cat == Entry.categorize():
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
        if self.category == None:
            cat_str = 'None'
        else:
            cat_str = self.category
        return cat_str + ' ' + self.asNotCatStr()
    
    def isMatch(self, line):
        thisStr = self.asNotCatStr()
        if thisStr in line:
            return True
        return False