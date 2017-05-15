"""Accounts class holds all the data for and account, duh"""

import category
import trigger
import override

class Account(object):

    def __init__(self, acct_str):
        self.categories = category.Category(acct_str)
        self.triggers = trigger.Trigger(acct_str, self)
        self.overrides = override.Override(acct_str)

    def load(self):
        self.categories.load()
        self.triggers.load()
        self.overrides.load()
        
class AccountList(list):
    def __init__(self):
        self.acct_list = []
        