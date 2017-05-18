"""Check entry --- one entry for each transaction on the account"""
import datetime
from money import Money
from category import Category
from trigger import Trigger
import pickle

class EntryList(object):
    
    def __init__(self, acct_str):
        self.n_entries = 0
        self.entrylist = []
        self.picklename = acct_str + '_entrylist.pckl'
        
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