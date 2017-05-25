""" Category class """

import accounts
import database
import pickle
import sqlite3


class Category(object):
    
    def __init__(self, db):
    
        # the category dictionary
        #self.acct_str = acct_str
        self.strings = set()
       # self.nCats = 0
        self.db = db
        self.createSQL = 'create table if not exists Categories(oid INTEGER PRIMARY KEY ASC, name varchar(20), super varchar(20))'
        self.selectAllSQL = 'select oid, name, super from Categories'
        self.insertSQL = 'insert into Categories(name, super) VALUES (?,?)'
        #todo: decide whether pickle will exist after db conversion done
        # categories pickle file name
        #self.picklename = self.acct_str + '_categories.pckl'
    
    def createTable(self):
        try:
            self.db.conn.execute(self.createSQL)
            return True
        except sqlite3.Error as e:
            self.db.error("An error occurred when creating the Catgory table:\n", e.args[0])
            return False            

    def removeCat(self, catStr):
        newSet = set()
        for cat in self.strings:
            if cat != catStr:
                newSet.add(cat)
        self.strings = newSet

    def addCat(self, catStr):
        self.strings.add(catStr)
        
        
    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.picklename, 'wb')
            pickle.dump(self.strings, f)
            f.close()
        elif storage == database.STORE_DB:
            try:
                for cat in self.strings:
                    self.db.conn.execute(self.insertSQL, (cat, 'none'))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.error('Could save category in Category table:\n', e.args[0])
                    

    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                self.strings = set()
                f = open(self.db.dbname+'_categories.pckl', 'rb')
                self.strings = pickle.load(f)
                f.close()
                self.nCats = len(self.strings)
            except FileNotFoundError:
                print('No categories.pckl file.')
        elif storage == database.STORE_DB:
            try:
                self.strings = set()
                for row in self.db.conn.execute(self.selectAllSQL):
                    self.strings.add(row[1])
            except sqlite3.Error as e:
                self.db.error('Error loading memory from the Category table:\n', e.args[0])
            

                
    def no_category(self):
        return 'None'
