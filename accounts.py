"""Accounts class holds all the data for and account, duh"""

import category
import trigger
import override
import entry

# storage defines
ACCT_DB = 1
ACCT_PCKL = 2

class Account(object):

    def __init__(self, acct_str, db):
        self.db = db
        self.categories = category.Category(acct_str, db)
        self.triggers = trigger.Trigger(acct_str, self, db)
        self.overrides = override.Override(acct_str, db)
        self.entries = entry.EntryList(acct_str, db)
        
    def convertPickleToDB(self):
        self.categories.load(ACCT_PCKL)
        self.categories.save(ACCT_DB)
        self.triggers.load(ACCT_PCKL)
        self.triggers.save(ACCT_DB)
        self.overrides.load(ACCT_PCKL)
        self.overrides.save(ACCT_DB)
        self.entries.load(ACCT_PCKL)
        self.entries.save(ACCT_DB)

    def load(self, storage):
        self.categories.load(storage)
        self.triggers.load(storage)
        self.overrides.load(storage)
        self.entries.load(storage)
        
    def save(self, storage):
        self.categories.save(storage)
        self.triggers.save(storage)
        self.overrides.save(storage)
        self.entries.save(storage)
        
    def mergeNewEntries(self, newList):
        for newEntry in newList:
            if not self.entries.isDupe(newEntry):
                self.entries.entrylist.append(newEntry)
        
    def removeCategory(catStr):
        pass
        
class AccountList(list):
    def __init__(self):
        self.acct_list = []
        