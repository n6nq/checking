""" Trigger provides a class method for determining the category of an Entry.
    this is done by searching the description field for known strings. Each
    known string returns a cooresponding category value string. Descriptions
    with no known trigger strings return the category string 'None'
    a signal to the caller that a new category must be defined."""

from category import Category
from override import Override
import pickle

class Trigger(object):
    
    # the category dictionary
    strings = {}
    
    # triggers pickle file name
    picklename = 'triggers.pckl'

    @classmethod
    def save(cls):
        f = open(cls.picklename, 'wb')
        pickle.dump(cls.strings, f)
        f.close()

    @classmethod
    def load(cls):
        try:
            cls.strings = {}
            f = open(cls.picklename, 'rb')
            cls.strings = pickle.load(f)
            f.close()
        except FileNotFoundError:
            print('No categories.pckl file.')
            
        
            
        
    @classmethod
    def fromDesc(cls, desc):
        for over, cat in Override.strings.items():
            if over in desc:
                return cat
            
        for trig, cat in cls.strings.items():
            if trig in desc:
                return cat
        
        return Category.no_category()
    
    @classmethod
    def addTrig(cls, trig, cat):
        if trig == '' or trig == 'None' or trig == None:
            return False
        if trig in cls.strings:
            return False
        cls.strings[trig] = cat
        return True
    
    @classmethod
    def triggers_for_cat(cls, lookFor):
        triggers = []
        for trig, cat in cls.strings.items():
            if cat == lookFor:
                triggers.append(trig)
                
        return triggers
    
    @classmethod
    def change_trigs_for_cat(cls, current_cat, new_cat):
        newd = {}
        for trig, cat in cls.strings.items():
            if cat == current_cat:
                newd[trig] = new_cat
            else:
                newd[trig] = cat
        cls.strings = newd