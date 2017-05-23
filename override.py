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
    
    def __init__(self, acct_str, db):
        # the Override dictionary
        self.strings = {}
        self.db = db
    
        #todo: decide about pickle files
        # Override pickle file name
        self.picklename = acct_str + '_overrides.pckl'
    
    def add_over(self, over_str, cat):
        if over_str == '' or over_str == None:
            return False
        if over_str in self.strings:
            return False
        self.strings[over_str] = cat
        
    
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
            print('No overrides.pckl file.')
    
    def overs_for_cat(self, lookFor):
        overs = []
        for over, cat in self.strings.items():
            if cat == lookFor:
                overs.append(over)
                
        return overs
    
    def change_overs_for_cat(self, current_cat, new_cat):
        newd = {}
        for over, cat in self.strings.items():
            if cat == current_cat:
                newd[over] = new_cat
            else:
                newd[over] = cat
                
        self.strings = newd
