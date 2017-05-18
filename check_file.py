"""This is the check_file class. All aspects of handling the file from the bank are here"""
from entry import Entry

class CheckFile(object):
    
    def __init__(self, acct):
        """Read the check file into memory"""
        self.acct = acct
        self.entries = []
        
    def open(self, filename):
        f = open(filename, 'r')
        line = f.readline()
        
        while len(line) > 1:
            line = line.replace('"', '')
            prt = line.split(',')
            
            self.entries.append(Entry(self.acct, prt[0], prt[1], prt[2], prt[3], prt[4]))
            line = f.readline()
        f.close()
        
    def find(self, line):
        for anEntry in self.entries:
            if anEntry.isMatch(line):
                return anEntry
            
        return None