"""This is the check_file class. All aspects of handling the file from the bank are here"""
import datetime
from money import Money
from entry import Entry
from category import Category
import database

class CheckFile(object):
    
    def __init__(self, db):
        """Read the check file into memory"""
        self.db = db
        self.entries = []
        
    def open(self, filename):
        f = open(filename, 'r')
        line = f.readline()
        
        while len(line) > 1:
            line = line.replace('"', '')
            prt = line.split(',')
            #                                   oid  cat                   datestr amtstr  clr*    chknum''  desc
            trans_date = datetime.datetime.strptime(prt[0], '%m/%d/%Y').date()
            row = (0, Category.no_category(), trans_date, Money.from_str(prt[1]),
                   self.cleared(prt[2]), self.check_num(prt[3]), prt[4])
            self.entries.append(Entry(self.db, row, Entry.CATEGORIZE))
            line = f.readline()
        f.close 
    
    def check_num(self, check_str):
        if check_str == '':
            return 0
        else:
            return int(check_str)
        
    def cleared(self, cleared_str):
        return cleared_str == '*'
    
    def find(self, line):
        for anEntry in self.entries:
            if anEntry.isMatch(line):
                return anEntry
            
        return None