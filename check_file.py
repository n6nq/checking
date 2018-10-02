import datetime
from money import Money
from entry import Entry
from entry import Entries
from category import Category
from trigger import Trigger
from override import Override
import database

class CheckFile(object):
    """ CheckFile -- This is the check_file class. All aspects of handling the file from the bank are here.
        Member variables:
        db -- reference to the single instance of Database class for storage and retrieval of all persistant data.
    """

    def __init__(self, db):
        """Creates a instance of the CheckFile class. Used by the CheckFileDialog"""
        self.db = db
        
    def open(self, filename):
        """Open file by provided name and read check entries to ncf(new check file) list.
           Used by CheckFileDialog."""
        self.db.clear_ncf_entries()
        f = open(filename, 'r')
        line = f.readline()
        
        while len(line) > 1:
            # Remove all quotes and linefeeds
            line = line.replace('"', '')
            line = line.replace('\n', '')
            prt = line.split(',')
            #     oid  cat_id trig_id  cat datestr amtstr  clr*    chknum''  desc
            trans_date = datetime.datetime.strptime(prt[0], '%m/%d/%Y').date()
            row = (0, 'None', Category.no_cat_id(), Trigger.no_trig_id(), Override.no_over_id(), trans_date, Money.str_to_num(prt[1]),
                   self.cleared(prt[2]), self.check_num(prt[3]), prt[4])
            self.db.add_ncf_entry(Entry(self.db, row, Entry.categorize()))
            #self.db.temp_entries.entrylist.append(Entry(self.db, row, Entry.categorize()))
            line = f.readline()
        f.close 
    
    def check_num(self, check_str):
        """Returns an integer, representing the checks number or a 0 if the entry did not hav a check number.
           Used by open in this class."""
        if check_str == '':
            return 0
        else:
            return int(check_str)
        
    def cleared(self, cleared_str):
        """Returns a boolean to indicate whether the line in the check had an '*' in it.
           Wells Fargo uses this to indicate that a chck has cleared.
           Used by open in this class."""
        return cleared_str == '*'
    
    def find(self, line):
        """Returns an entry from the new checks list that matches the str(s) in 'line'.
           Used by the CheckFileDialog to find entries based on strings selected in lists."""
        for anEntry in self.db.get_ncf_entries():
            if anEntry.isMatch(line):
                return anEntry
            
        return None