""" Category class """

import dbrow
import database
import accounts
import pickle
import sqlite3

       
class Category(dbrow.DBRow):
    """Category -- Puts a name on a type of account entry, such as Car, Utility, Health.
       These names are used primarily for budgeting purposes.
       Members are:
       id -- a key for foreign key references in other objects, such as an entry.
       cat -- a string containing a categories name, like Insurance
       super_cat -- currently not used. Possible future use is for grouping categories
                    such as Income, Bills, etc.
       Used by:
       CheckFile -- to assign initial category to new entries.
       Database -- a list and table of current categories is maintained by Database class
           The category list in Database is used where ever entries exist"""
    
    def __init__(self, row):
        self.id = row[0]
        self.cat = row[1]
        self.super_cat = row[2]
        
        
#    def save(self, storage):    #deprecated
#        assert(False)
#        if storage == database.STORE_PCKL:
#            f = open(self.db.name()+'_categeories.pckl', 'wb')
#            pickle.dump(self.cache, f)
#            f.close()
#        elif storage == database.STORE_DB:
#            for cat in self.cache:
#                self.addToDB(cat)
                    

#    def load(self, storage):    #deprecated
#        assert(False)
#        if storage == database.STORE_PCKL:
#            try:
#                self.cache = set()
#                f = open(self.db.name()+'_categories.pckl', 'rb')
#                self.cache = pickle.load(f)
#                f.close()
#                self.nCats = len(self.cache)
#            except FileNotFoundError:
#                print('No categories.pckl file.')
#        elif storage == database.STORE_DB:
#            self.cache = self.db.get_all_cats()
            
    @classmethod
    def no_category(cls):
        """no_category -- a class method to provide a string for representing no category"""
        return 'None'
    
    @classmethod
    def no_cat_id(cls):
        """no_cat_id -- a class method to provide the id of uncategorized entries"""
        return 0
