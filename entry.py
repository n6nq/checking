"""Check entry --- one entry for each transaction on the account"""
from asyncio import locks
import index
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
        self.createSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), sdate date, amount int, cleared boolean, checknum int, desc varchar(255), locked bool)'
        self.selectAllSQL = 'select oid, category, sdate, amount, cleared, checknum, desc, locked from Entries' #TODO check callers
        self.insertSQL = 'insert into Entries(category, sdate, amount, cleared, checknum, desc, locked) values(?, ?, ?, ?, ?, ?, ?)'  #TODOcheck callers
        self.updateCatSQL = 'update Entries set category = ? where category = ?'    #TODOcheck callers
        db.create_table(self.createSQL, 'Entries')  #TODO: maybe skip if temp_entries

        
    def del_cat(self, cat):
        pass
    
    #def load(self, storage):
        #if storage == database.STORE_PCKL:
            #try:
                #f = open(self.db.name()+'_entrylist.pckl', 'rb')
                #self.cache = pickle.load(f)
                #f.close()
            #except FileNotFoundError:
                #print('No entrylist.pckl file.')
        #elif storage == database.STORE_DB:
            #self.cache = self.db.get_all_entries()
            
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
        
    #def save(self, storage):
        #if storage == database.STORE_PCKL:
            #f = open(self.db.name()+'_entrylist.pckl', 'wb')
            #pickle.dump(self.strings, f)
            #f.close()
        #elif storage == database.STORE_DB:
            #self.db.addEntryList(self.entrylist)
        
class Entry(dbrow.DBRow):
    """Entry --- An entry in the check register"""
    def __init__(self, db, row, how_to_cat):  # TODO check callers, how should they pass locked?
        self.db = db
        self.oid = row[index.ENTRY_OID]
        self.category = row[index.ENTRY_CATEGORY]
        self.cat_id = row[index.ENTRY_CAT_ID]
        self.trig_id = row[index.ENTRY_TRIG_ID]
        self.over_id = row[index.ENTRY_OVER_ID]
        self.date = row[index.ENTRY_SDATE]
        self.amount = Money.from_number(row[index.ENTRY_AMOUNT])
        self.cleared = row[index.ENTRY_CLEARED]
        self.checknum = row[index.ENTRY_CHECKNUM]
        self.desc = row[index.ENTRY_DESC].replace('\n', '')
        self.locked = row[index.ENTRY_LOCKED]

        if int(how_to_cat) == int(Entry.categorize()):
            cat_tuple = self.db.cat_from_desc(self.desc)
            self.category = cat_tuple[0]
            self.cat_id = cat_tuple[1]
            self.trig_id = cat_tuple[2]
            self.over_id = cat_tuple[3]
            self.locked = False
            
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
        #print(self.asNotCatStr(''))
        #print(other.asNotCatStr(''))
        if (self.date - other.date).total_seconds() != 0:
            return False
        if self.amount.value != other.amount.value:
            return False
        if self.desc != other.desc:
            return False
        return True
    
    def __ne__(self, other):
        return (self.date != other.date or \
           self.amount.value != other.amount.value or \
           self.desc != other.desc)
    
    def __hash__(self):
        return hash((self.date, self.amount.value, self.desc))

    def amount_as_str(self):
        assert(False)   #deprecated
        return self.amount.as_str()

    def asNotCatStr(self, sep):
        if self.checknum == 0:
            checknum_str = '{:<10} '.format('+ ')
        else:
            checknum_str = '{:<10} '.format(self.checknum) 

        retstr = '{}{:<10} '.format(sep, self.date.strftime("%m/%d/%y"))
        retstr += '{}{:<10} '.format(sep, self.amount.as_str())
        retstr += sep+checknum_str
        retstr += sep+self.desc
            #retstr = self.date.strftime("%m/%d/%y") + '\t' + \
            #    self.amount.as_str() + '\t' + \
            #    checknum_str + '\t' + \
            #    self.desc
        return retstr
    
    def asCategorizedStr(self, sep):
        if self.category == None:
            cat_str = 'None'
        else:
            cat_str = self.category
        if self.locked:         #TODO test lock display
            lockstr = 'L'
        else:
            lockstr = ' '
        if sep == ',':    
            return '{}'.format(cat_str) + ',' + lockstr + ',' + self.asNotCatStr(sep)  
        else:
            return '{:<10}'.format(cat_str) + lockstr + self.asNotCatStr(sep)
    
    def get_category(self):     #TODO check callers
        return self.category
    
    def isMatch(self, line):    #TODO check callers
        #assert(False)
        thisStr = self.asNotCatStr('')
        if thisStr in line:
            return True
        return False
    
    @classmethod
    def no_cat(cls):
        return 0
    
    @classmethod
    def categorize(cls):
        return 1
    
    @classmethod
    def only_none(cls):
        return 2
    
    