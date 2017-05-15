"""Override.py --- Overrides are trigger strings that take precedence over normal
   trigger strings. Overrides are normally used were two trigger strings occur in
   the same entry, each pointing to a different Category and only one really defines
   what Category this entry must take. For example, an entry where the bank charges
   and Overdraft fee for check to xxxx. Normally xxxx would have determined the
   Category 'Credit Card', but 'Overdraft' signifies that thi charge is actually
   a Bank Fee. Overrides are searched for first, before normal Categories, reating
   a one level hierarchy."""

import pickle

class Override(object):
    
    # the Override dictionary
    strings = {}
    
    # Override pickle file name
    picklename = 'overrides.pckl'
    
    @classmethod
    def add_over(cls, over_str, cat):
        if over_str == '' or over_str == None:
            return False
        if over_str in cls.strings:
            return False
        cls.strings[over_str] = cat
        
    
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
            print('No overrides.pckl file.')
    
    @classmethod
    def overs_for_cat(cls, lookFor):
        overs = []
        for over, cat in cls.strings.items():
            if cat == lookFor:
                overs.append(over)
                
        return overs
    
    @classmethod
    def change_overs_for_cat(cls, current_cat, new_cat):
        newd = {}
        for over, cat in cls.strings.items():
            if cat == current_cat:
                newd[over] = new_cat
            else:
                newd[over] = cat
                
        cls.strings = newd
