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
        
        #self.acct_str = acct_str
        # the category dictionary
        self.strings = {}
        self.db = db
        self.createSQL = 'create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(30), category varchar(20))'
        self.selectAllSQL = 'select oid, trigger, category from Triggers'
        self.insertSQL = 'insert into Triggers(trigger, category) values(?, ?)'
        #todo: decide about pickle files
        # triggers pickle file name
        #self.picklename = self.acct_str + '_triggers.pckl'

    def createTable(self):
        try:
            self.db.conn.execute(self.createSQL)
            return True
        except sqlite3.Error as e:
            self.db.error("An error occurred when creating the Triggers table:\n", e.args[0])
            return False            

    def save(self, storage):
        if storage == database.STORE_PCKL:
            f = open(self.db.dbname+'_triggers.pckl', 'wb')
            pickle.dump(self.strings, f)
            f.close()
        elif storage == database.STORE_DB:
            try:
                for trig, cat in self.strings.items():
                    self.db.conn.execute(self.insertSQL, (trig, cat))
                self.db.commit()
            except sqlite3.Error as e:
                self.db.error('Could save triggers in Triggers table:\n', e.args[0])        

    def load(self, storage):
        if storage == database.STORE_PCKL:
            try:
                self.strings = {}
                f = open(self.db.dbname+'_triggers.pckl', 'rb')
                self.strings = pickle.load(f)
                f.close()
            except FileNotFoundError:
                print('No triggers.pckl file.')
        elif storage == database.STORE_DB:
            try:
                self.strings = {}
                for row in self.db.conn.execute(self.selectAllSQL):
                    self.strings[row[1]] = row[2]
            except sqlite3.Error as e:
                self.db.error('Error loading memory from the Triggers table:\n', e.args[0])
        
    def fromDesc(self, desc):
        for over, cat in self.db.overrides.strings.items():
            if over in desc:
                return cat
            
        for trig, cat in self.strings.items():
            if trig in desc:
                return cat
        
        return self.db.categories.no_category()
    
    def addTrig(self, trig, cat):
        if trig == '' or trig == 'None' or trig == None:
            return False
        if trig in self.strings:
            return False
        self.strings[trig] = cat
        return True
    
    def triggers_for_cat(self, lookFor):
        triggers = []
        for trig, cat in self.strings.items():
            if cat == lookFor:
                triggers.append(trig)
                
        return triggers
    
    def change_trigs_for_cat(self, current_cat, new_cat):
        newd = {}
        for trig, cat in self.strings.items():
            if cat == current_cat:
                newd[trig] = new_cat
            else:
                newd[trig] = cat
        self.strings = newd