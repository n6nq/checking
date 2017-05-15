""" Category class """

import pickle


class Category(object):
    
    # the category dictionary
    strings = set()
    
    nCats = 0
    
    # categories pickle file name
    picklename = 'categories.pckl'
    
    @classmethod
    def removeCat(cls, catStr):
        newSet = set()
        for cat in cls.strings:
            if cat != catStr:
                newSet.add(cat)
        cls.strings = newSet

    @classmethod
    def addCat(cls, catStr):
        cls.strings.add(catStr)
        
        
    @classmethod
    def save(cls):
        f = open(cls.picklename, 'wb')
        pickle.dump(cls.strings, f)
        f.close()

    @classmethod
    def load(cls):
        try:
            cls.strings = set()
            f = open(cls.picklename, 'rb')
            cls.strings = pickle.load(f)
            f.close()
            cls.nCats = len(cls.strings)
        except FileNotFoundError:
            print('No categories.pckl file.')
    
    @classmethod
    def no_category(cls):
        return 'None'
