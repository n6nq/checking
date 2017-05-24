"""Check entry --- one entry for each transaction on the account"""
import datetime
from money import Money
from category import Category
from trigger import Trigger
import pickle

class EntryList(object):
    
    def __init__(self, db):
        #self.n_entries = 0
        self.entrylist = []
        self.db = db
        self.createSQL = 'create table if not exists Entries(oid INTEGER PRIMARY KEY ASC, category varchar(20), edate date, amount int, checknum int, cleared boolean, desc varchar(255))'
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
        
    def load(self):
        try:
            self.strings = set()
            f = open(self.picklename, 'rb')
            self.entrylist = pickle.load(f)
            f.close()
            self.n_entries = len(self.entrylist)
        except FileNotFoundError:
            print('No acct_categories.pckl file.')

    def save(self):
        f = open(self.picklename, 'wb')
        pickle.dump(self.entrylist, f)
        f.close()
        
class Entry(object):

    def __init__(self, acct, date, amount, cleared, checknum, desc):
        self.acct = acct
        dparts = date.split('/')
        self.date = datetime.date(int(dparts[2]), int(dparts[0]), int(dparts[1]))
        self.amount = Money(amount)
        self.cleared = (cleared == '*')
        if len(checknum) == 0:
            self.checknum = 0
        else:
            self.checknum = int(checknum)
        self.desc = desc
        self.category = self.acct.triggers.fromDesc(desc)
        
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