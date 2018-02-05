""" predicted.py  --- This data type stores bills and other predictable transactions. They
will be used to project future balances for 'what-if scenarios.

Amount
category
trigger
type bill, prediction, subscription, monthly, elective
cycle monthly, weekly, quarterly, annual, bi-weekly, ad-hoc
date day-of-month, day-of-week, day/month, adhoc
"""
from enum import Enum
from bidict import bidict
from pcycle import PCycle, Cycles
from money import Money

# Keep Types in alphabetical order so type combo will sort correctly
Types = bidict({'None': 0, 'Bill': 1, 'Elective': 2, 'Income': 3, 'Monthly': 4, 'Prediction': 5, 'Subscription': 6})

class Prediction(object):
    
    def __init__(self, db):
        self.db = db
        self.cycle = None
    
    def as_str(self):
        return ' Amount: ' + self.amount.as_str() + ' cat: ' + self.cat + ' trig: ' + self.trig + ' desc: ' + self.desc
    
    def get_typestr(self):
        return Types.inv[self.p_type]

    
    def get_cyclestr(self):
        assert(False)  #deprecated
        #return PCycles.inv[self.cycle]
    
    def get_datestr(self):
        assert(False)   #deprecated
        if self.cycle == Cycles['Weekly']:
            return DaysOfWeek.inv[self.vdate]
        elif self.cycle == Cycles['Monthly']:
            return str(self.vdate)
        else:
            return str(self.ddate)
        
    def get_income_str(self):
        if self.income == 0:
            return 'N'
        else:
            return 'Y'
        
    def in_next_week(self, today):
        ctype = self.cycle.ctype
        if ctype == Cycles['Weekly']:
            return True
        elif ctype == Cycles['Monthly']:
            self.cycle.vdate < 
    
    def in_next_month(self, today):
        pass
    
    def in_three_month(self, today):
        pass
    
    def set_without_ids(self, amount, income, cat, trig=None, over=None, p_type=None, cycle=None, ddate=None, vdate=None, desc=None):
        self.amount = amount
        self.income = income
        self.cat = cat
        self.trig = trig
        if over == 'None':
            self.over = None
        self.cat_id = 0
        self.trig_id = 0
        self.over_id = 0
        self.p_type = p_type
        self.cycle = PCycle(cycle, ddate, vdate)
        self.desc = desc

    def set_with_ids(self, oid, amount, income, cat, trig=None, over=None, cat_id=0, trig_id=0, over_id=0, p_type=None, cycle=None, ddate=None, vdate=None, desc=None):
        self.oid = oid
        self.amount = amount
        self.income = income
        self.cat = cat
        self.trig = trig
        self.over = over
        self.cat_id = cat_id
        self.trig_id = trig_id
        self.over_id = over_id
        self.p_type = p_type
        self.cycle = PCycle(cycle, ddate, vdate)
        self.desc = desc

    def set_without_oid(self, lst):
        self.amount = Money.from_number(lst[1])
        self.income = lst[2]
        self.cat = lst[3]
        self.trig = lst[4]
        self.over = lst[5]
        self.cat_id = lst[6]
        self.trig_id = lst[7]
        self.over_id = lst[8]
        self.p_type = lst[9]
        self.cycle = PCycle(lst[10], lst[11], lst[12])
        self.desc = lst[13]
        
    def set_with_list(self, lst):
        self.oid = lst[0]
        self.set_without_oid(lst)
        
    def update_with_list(self, lst):
        assert(self.oid == lst[0])
        self.set_without_oid(lst)
        
    #---- CLASSMETHODS -------------------------------#
    @classmethod
    def headers(cls):
        return ['Amount', 'Income', 'Category', 'Trigger', 'Override', 'Type', 'Cycle', 'Date', 'Desc']
    
    @classmethod
    def get_type_list(cls):
        keyList = []
        for key in Types.keys():
            keyList.append(key)
        return keyList
    
    @classmethod
    def get_ptype_from_str(cls, str):
        assert(str in Types)
        return Types[str]

    @classmethod
    def get_cycle_from_str(cls, str):
        assert(False)           #deprecated
        return Cycles[str]

    @classmethod
    def get_vdate_from_str(cls, cycle, str):
        assert(False)               #deprecated
        if cycle == Cycles['Weekly']:
            assert(str in DaysOfWeek)
            return DaysOfWeek[str]
        elif cycle == Cycles['Monthly']:
            assert(int(str))
            return int(str)
        else:
            assert(False)
        return 0
    
    
    