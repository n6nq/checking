"""Override.py --- Overrides are trigger strings that take precedence over normal
   trigger strings. Overrides are normally used were two trigger strings occur in
   the same entry, each pointing to a different Category and only one really defines
   what Category this entry must take. For example, an entry where the bank charges
   and Overdraft fee for check to xxxx. Normally xxxx would have determined the
   Category 'Credit Card', but 'Overdraft' signifies that thi charge is actually
   a Bank Fee. Overrides are searched for first, before normal Categories, reating
   a one level hierarchy."""

import pickle

class Override(object):
    
    def __init__(self, db):
        # the Override dictionary
        self.strings = {}
        self.db = db
        self.createSQL = 'create table if not exists Overrides(oid INTEGER PRIMARY KEY ASC, override varchar(30), category varchar(20))'
        self.selectAllSQL = 'select oid, override, category from Overrides'
        #todo: decide about pickle files
        # Override pickle file name
        #self.picklename = acct_str + '_overrides.pckl'
    
    def createTable(self):
        try:
            self.db.conn.execute(self.createSQL)
            return True
        except sqlite3.Error as e:
            self.db.error("An error occurred when creating the Override table:\n", e.args[0])
            return False            

    def add_over(self, over_str, cat):
        if over_str == '' or over_str == None:
            return False
        if over_str in self.strings:
            return False
        self.strings[over_str] = cat
        
    
    def save(self, storage):
        f = open(self.picklename, 'wb')
        pickle.dump(self.strings, f)
        f.close()

    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                self.strings = {}
                f = open(self.db.dbname+'_overrides.pckl', 'rb')
                self.strings = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No overrides.pckl file.')
        elif storage == database.STORE_DB:
            try:
                self.strings = {}
                for row in self.db.conn.execute(self.selectAllSQL):
                    self.strings[row[1]] = row[2]
            except sqlite3.Error as e:
                self.db.error('Error loading memory from the Overrides table:\n', e.args[0])
    
    def overs_for_cat(self, lookFor):
        overs = []
        for over, cat in self.strings.items():
            if cat == lookFor:
                overs.append(over)
                
        return overs
    
    def change_overs_for_cat(self, current_cat, new_cat):
        newd = {}
        for over, cat in self.strings.items():
            if cat == current_cat:
                newd[over] = new_cat
            else:
                newd[over] = cat
                
        self.strings = newd
