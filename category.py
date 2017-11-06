""" Category class """

import dbrow
import database
import accounts
import pickle
import sqlite3

       
class Category(dbrow.DBRow):
    
    def __init__(self, row):
        self.id = row[0]
        self.cat = row[1]
        self.super_cat = row[2]
        
        
    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.db.name()+'_categeories.pckl', 'wb')
            pickle.dump(self.cache, f)
            f.close()
        elif storage == database.STORE_DB:
            for cat in self.cache:
                self.addToDB(cat)
                    

    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                self.cache = set()
                f = open(self.db.name()+'_categories.pckl', 'rb')
                self.cache = pickle.load(f)
                f.close()
                self.nCats = len(self.cache)
            except FileNotFoundError:
                print('No categories.pckl file.')
        elif storage == database.STORE_DB:
            self.cache = self.db.get_all_cats()
            
    @classmethod
    def no_category(cls):
        return 'None'
    
    @classmethod
    def no_cat_id(cls):
        return 0
