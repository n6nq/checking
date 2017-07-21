"""Override.py --- Overrides are trigger strings that take precedence over normal
   trigger strings. Overrides are normally used were two trigger strings occur in
   the same entry, each pointing to a different Category and only one really defines
   what Category this entry must take. For example, an entry where the bank charges
   and Overdraft fee for check to xxxx. Normally xxxx would have determined the
   Category 'Credit Card', but 'Overdraft' signifies that thi charge is actually
   a Bank Fee. Overrides are searched for first, before normal Categories, reating
   a one level hierarchy."""

import dbrow
import database
import sqlite3
import pickle

class Overrides(object):
    
    def __init__(self, db):
        self.cache = {}
        self.db = db
        self.createSQL = 'create table if not exists Overrides(oid INTEGER PRIMARY KEY ASC, override varchar(30) unique, category varchar(20))'
        self.selectAllSQL = 'select oid, override, category from Overrides'
        self.insertSQL = 'insert into Overrides(override, category) values(?, ?)'
        db.create_table(self.createSQL, 'Overrides')

    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.name()+'_overrides.pckl', 'rb')
                self.cache = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No overrides.pckl file.')
        elif storage == database.STORE_DB:
            self.cache = self.db.get_all_overrides()

    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.db.name()+'_overrides.pckl', 'wb')
            pickle.dump(self.strings, f)
            f.close()
        elif storage == database.STORE_DB:
            for over, cat in self.strings.items():
                self.db.addOverride(over, cat)
        
class Override(dbrow.DBRow):
    
    def __init__(self, db, storage):
        pass
#        self.strings = set()
#        self.db = db
#        self.load(storage)

    def del_cat(self, cat):
        pass
    
    def add_over(self, over_str, cat):
        if over_str == '' or over_str == None:
            return False
        if over_str in self.strings:
            return False
        self.strings[over_str] = cat
        
    
