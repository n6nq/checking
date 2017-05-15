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
    
    def __init__(self, acct_str, acct):
        
        self.acct = acct
        self.acct_str = acct_str
        # the category dictionary
        self.strings = {}
    
        # triggers pickle file name
        self.picklename = self.acct_str + 'triggers.pckl'

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
    
    @classmethod
    def addTrig(cls, trig, cat):
        if trig == '' or trig == 'None' or trig == None:
            return False
        if trig in cls.strings:
            return False
        cls.strings[trig] = cat
        return True
    
    def triggers_for_cat(self, lookFor):
        triggers = []
        for trig, cat in self.strings.items():
            if cat == lookFor:
                triggers.append(trig)
                
        return triggers
    
    def change_trigs_for_cat(cls, current_cat, new_cat):
        newd = {}
        for trig, cat in cls.strings.items():
            if cat == current_cat:
                newd[trig] = new_cat
            else:
                newd[trig] = cat
        cls.strings = newd