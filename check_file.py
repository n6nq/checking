"""This is the check_file class. All aspects of handling the file from the bank are here"""
import datetime
from money import Money
from entry import Entry
from entry import Entries
from category import Category
from trigger import Trigger
import database

class CheckFile(object):
    
    def __init__(self, db):
        """Read the check file into memory"""
        self.db = db
        
    def open(self, filename):
        self.db.clear_ncf_entries()
        f = open(filename, 'r')
        line = f.readline()
        
        while len(line) > 1:
            line = line.replace('"', '')
            line = line.replace('\n', '')
            prt = line.split(',')
            #     oid  cat_id trig_id  cat datestr amtstr  clr*    chknum''  desc
            trans_date = datetime.datetime.strptime(prt[0], '%m/%d/%Y').date()
            row = (0, Category.no_cat_id, Trigger.no_trig_id, Category.no_category, trans_date, Money.str_to_num(prt[1]),
                   self.cleared(prt[2]), self.check_num(prt[3]), prt[4])
            self.db.add_ncf_entry(Entry(self.db, row, Entry.categorize()))
            #self.db.temp_entries.entrylist.append(Entry(self.db, row, Entry.categorize()))
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
        for anEntry in self.db.get_ncf_entries():
            if anEntry.isMatch(line):
                return anEntry
            
        return None