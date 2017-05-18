"""Accounts class holds all the data for and account, duh"""

import category
import trigger
import override
import entry

class Account(object):

    def __init__(self, acct_str):
        self.categories = category.Category(acct_str)
        self.triggers = trigger.Trigger(acct_str, self)
        self.overrides = override.Override(acct_str)
        self.entries = entry.EntryList(acct_str)
        
    def load(self):
        self.categories.load()
        self.triggers.load()
        self.overrides.load()
        self.entries.load()
        
    def save(self):
        self.categories.save()
        self.triggers.save()
        self.overrides.save()
        self.entries.save()
        
    def mergeNewEntries(self, newList):
        for newEntry in newList:
            if not self.entries.isDupe(newEntry):
                self.entries.entrylist.append(newEntry)
        
    def removeCategory(catStr):
        pass
        
class AccountList(list):
    def __init__(self):
        self.acct_list = []
        