"""Check entry --- one entry for each transaction on the account"""
import datetime
from money import Money
from category import Category
from trigger import Trigger

class EntryList(list):
    
    def __init__(self):
        self.n_entries = 0

class Entry(object):

    def __init__(self, date, amount, cleared, checknum, desc):
        dparts = date.split('/')
        self.date = datetime.date(int(dparts[2]), int(dparts[0]), int(dparts[1]))
        self.amount = Money(amount)
        self.cleared = (cleared == '*')
        if len(checknum) == 0:
            self.checknum = 0
        else:
            self.checknum = int(checknum)
        self.desc = desc
        self.category = Trigger.fromDesc(desc)
        
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