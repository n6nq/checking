""" Trigger provides a class method for determining the category of an Entry.
    this is done by searching the description field for known strings. Each
    known string returns a cooresponding category value string. Descriptions
    with no known trigger strings return the category string 'None'
    a signal to the caller that a new category must be defined."""

import database
import dbrow
import accounts
import category
import override
import sqlite3
import pickle

class Trigger(dbrow.DBRow):
    
    def __init__(self, db):
        self.cache = {}
        self.db = db
        self.createSQL = 'create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(30) unique, category varchar(20))'
        self.selectAllSQL = 'select oid, trigger, category from Triggers'
        self.insertSQL = 'insert into Triggers(trigger, category) values(?, ?)'
        self.deleteCatSQL = 'delete from Triggers where category = ?'
        db.create_table(self.createSQL, 'Triggers')
        #self.load(storage)  load after they are created

    def del_cat(self, lose_cat):
        newd = {}
        for trig, cat in self.cache.items():
            if cat != lose_cat:
                newd[trig] = cat
        self.cache = newd
        
        #try:
        #    cur = self.db.conn.execute(self.deleteCatSQL)
        #pass
    
    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.db.name()+'_triggers.pckl', 'wb')
            pickle.dump(self.cache, f)
            f.close()
        elif storage == database.STORE_DB:
            for trig, cat in self.cache.items():
                self.db.addTrigger(trig, cat)

    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                f = open(self.db.name()+'_triggers.pckl', 'rb')
                self.cache = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No triggers.pckl file.')
        elif storage == database.STORE_DB:
            self.cache = self.db.get_all_triggers()
        
#    def fromDesc(self, desc):
#        for over, cat in self.db.get_all_overrides():
#            if over in desc:
#                return cat
#            
#        for trig, cat in self.cache.items():
#            if trig in desc:
#                return cat
#        
#        return None
    
    def addTrig(self, trig, cat):
        if trig == '' or trig == 'None' or trig == None:
            return False
        if trig in self.cache:
            return False
        self.cache[trig] = cat
        self.db.addTrigger(trig, cat)
        return True
    
    def triggers_for_cat(self, lookFor):
        triggers = []
        for trig, cat in self.cache.items():
            if cat == lookFor:
                triggers.append(trig)
                
        return triggers
    
    def change_trigs_for_cat(self, current_cat, new_cat):
        newd = {}
        for trig, cat in self.cache.items():
            if cat == current_cat:
                newd[trig] = new_cat
            else:
                newd[trig] = cat
        self.strings = newd