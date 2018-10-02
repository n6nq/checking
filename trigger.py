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
    
    def __init__(self, row):
        self.oid = row[0]
        self.trig = row[1]
        self.cat = row[2]

    #def save(self, storage):
        #if storage == database.STORE_PCKL:
            #f = open(self.db.name()+'_triggers.pckl', 'wb')
            #pickle.dump(self.cache, f)
            #f.close()
        #elif storage == database.STORE_DB:
            #for trig, cat in self.cache.items():
                #self.db.addTrigger(trig, cat)

    #def load(self, storage):
        #if storage == database.STORE_PCKL:
            #try:
                #f = open(self.db.name()+'_triggers.pckl', 'rb')
                #self.cache = pickle.load(f)
                #f.close()
            #except FileNotFoundError:
                #print('No triggers.pckl file.')
        #elif storage == database.STORE_DB:
            #self.cache = self.db.get_all_triggers()
        
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
    

    @classmethod
    def no_trig_id(cls):
        return 0
    