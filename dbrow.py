"""dbrow.py  --- base class for database rows (memory resident copy)"""

# clean and dirty
CLEAN = 0
DIRTY = 1

class DBRow(object):
    def __init__(self):
        self.state = DIRTY
        
    def isDirty(self):
        return self.state == DIRTY
    
