""" Trigger provides a class method for determining the category of an Entry.
    this is done by searching the description field for known strings. Each
    known string returns a cooresponding category value string. Descriptions
    with no known trigger strings return the category string 'None'
    a signal to the caller that a new category must be defined."""

import accounts
import category
import override
import pickle

class Trigger(object):
    
    def __init__(self, acct_str, db):
        
        self.acct_str = acct_str
        # the category dictionary
        self.strings = {}
        self.db = db
        self.createSQL = 'create table if not exists Triggers(oid INTEGER PRIMARY KEY ASC, trigger varchar(30), category varchar(20))'
        
        #todo: decide about pickle files
        # triggers pickle file name
        self.picklename = self.acct_str + '_triggers.pckl'

    def save(self):
        f = open(self.picklename, 'wb')
        pickle.dump(self.strings, f)
        f.close()

    def load(self):
        try:
            self.strings = {}
            f = open(self.picklename, 'rb')
            self.strings = pickle.load(f)
            f.close()
        except FileNotFoundError:
            print('No acct_categories.pckl file.')
            
        
    def fromDesc(self, desc):
        for over, cat in self.acct.overrides.strings.items():
            if over in desc:
                return cat
            
        for trig, cat in self.strings.items():
            if trig in desc:
                return cat
        
        return self.acct.categories.no_category()
    
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