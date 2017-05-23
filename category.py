""" Category class """

import account
import pickle


class Category(object):
    
    def __init__(self, acct_str, db):
    
        # the category dictionary
        self.acct_str = acct_str
        self.strings = set()
        self.nCats = 0
        self.db = db
    
        #todo: decide whether pickle will exist after db conversion done
        # categories pickle file name
        self.picklename = self.acct_str + '_categories.pckl'
    
    def removeCat(self, catStr):
        newSet = set()
        for cat in self.strings:
            if cat != catStr:
                newSet.add(cat)
        self.strings = newSet

    def addCat(self, catStr):
        self.strings.add(catStr)
        
        
    def save(self):
        f = open(self.picklename, 'wb')
        pickle.dump(self.strings, f)
        f.close()

    def load(self, storage):
        if storage == account.ACCT_PCKL:
            try:
                self.strings = set()
                f = open(self.picklename, 'rb')
                self.strings = pickle.load(f)
                f.close()
                self.nCats = len(self.strings)
            except FileNotFoundError:
                print('No categories.pckl file.')
        elif storage == account.ACCT_DB:
            try:
                sql = 'select'
    def no_category(self):
        return 'None'
