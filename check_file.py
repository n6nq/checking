"""This is the check_file class. All aspects of handling the file from the bank are here"""
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
            
            self.entries.append(Entry(self.db, (0, Category.no_category(), prt[0], prt[1], prt[2], prt[3], prt[4])))
            line = f.readline()
        f.close()
        
    def find(self, line):
        for anEntry in self.entries:
            if anEntry.isMatch(line):
                return anEntry
            
        return None