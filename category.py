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
        
        #self.cache = set()
        #self.db = db
        #self.createSQL = 'create table if not exists Categories(oid INTEGER PRIMARY KEY ASC, name varchar(20) unique, super varchar(20))'
        #self.selectAllSQL = 'select oid, name, super from Categories'
        #self.insertSQL = 'insert into Categories(name, super) VALUES (?,?)'
        #db.create_table(self.createSQL, 'Categories')
        #self.load(storage)  load after they are created

    def removeCat(self, catStr):
        newSet = set()
        for cat in self.cache:
            if cat != catStr:
                newSet.add(cat)
        self.cache = newSet

    def addCat(self, catStr):
        self.cache.add(catStr)
        self.db.addCat(catStr)

#   def addToDB(self, catStr):
#        try:
#            self.db.conn.execute(self.insertSQL, (catStr, None))
#            self.db.commit()
#        except sqlite3.Error as e:
#            self.db.error('Could not save category in Category table:\n', e.args[0])
     
        
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
    def no_category(self):
        return 'None'
