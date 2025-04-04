"""Override.py --- Overrides are trigger strings that take precedence over normal
   trigger strings. Overrides are normally used were two trigger strings occur in
   the same entry, each pointing to a different Category and only one really defines
   what Category this entry must take. For example, an entry where the bank charges
   and Overdraft fee for check to xxxx. Normally xxxx would have determined the
   Category 'Credit Card', but 'Overdraft' signifies that thi charge is actually
   a Bank Fee. Overrides are searched for first, before normal Categories, reating
   a one level hierarchy."""
import index
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

    #def load(self, storage):
        #if storage == database.STORE_PCKL:
            #try:
                #f = open(self.db.name()+'_overrides.pckl', 'rb')
                #self.cache = pickle.load(f)
                #f.close()
            #except FileNotFoundError:
                #print('No overrides.pckl file.')
        #elif storage == database.STORE_DB:
            #self.cache = self.db.get_all_overrides()

    #def save(self, storage):
        #if storage == database.STORE_PCKL:
            #f = open(self.db.name()+'_overrides.pckl', 'wb')
            #pickle.dump(self.strings, f)
            #f.close()
        #elif storage == database.STORE_DB:
            #for over, cat in self.strings.items():
                #self.db.addOverride(over, cat)
        
class Override(dbrow.DBRow):
    """Override -- An override is a search string that has prioritt over normal trigger strings. For
    example: If an entry contained a description 'aaaa bbbbb ccccc' and there was a trigger named
    B that triggered on the string 'bbbbb' setting this entries Category to 'Bee', that could be
    overridden by defining and Override 'ccccc' therefore making the netries category 'See'."""
    def __init__(self, row):
        self.oid = row[index.OVER_OID]     # TODO check for dupes
        self.over = row[index.OVER_OVER]
        self.cat = row[index.OVER_CAT]
        
    def del_cat(self, cat):
        pass
    
    def add_over(self, over_str, cat):
        if over_str == '' or over_str == None:   # TODO check for dupes
            return False
        if over_str in self.strings:
            return False
        self.strings[over_str] = cat
        
    @classmethod
    def no_over_id(cls):
        return 0
