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
from pcycle import PCycle
from money import Money

#class PType(Enum):
#    BILL = 1
#    PRED = 2
#    SUBSCR = 3
#    MONTH = 4
#    ELECT = 5
Types = bidict({'None': 0,'Bill': 1, 'Prediction': 2, 'Subscription': 3, 'Monthly': 4, 'Elective': 5})

class Prediction(object):
    
    def __init__(self, db):
        self.db = db
        self.cycle = None
    
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
        
    def get_cycle_from_str(self, str):
        assert(False)   #deprecated
        self.cycle = Cycles[str]
        return self.cycle
    
    def get_income_str(self):
        if self.income == 0:
            return 'N'
        else:
            return 'Y'
        
    def get_ptype_from_str(self, str):
        self.p_type = Types[str]
        return self.p_type
    
    def get_vdate_from_str(self, cycle, str):
        assert(False)   #deprecated
        if cycle == Cycles['Weekly']:
            self.vdate = DaysOfWeek[str]
            return self.vdate
        elif cycle == Cycles['Monthly']:
            self.vdate = int(str)
        else:
            self.vdate = 0      # equals none
        return self.vdate
    
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

    def set_with_row(self, row):
        self.oid = row[0]
        self.amount = Money.from_number(row[1])
        self.income = row[2]
        self.cat = row[3]
        self.trig = row[4]
        self.over = row[5]
        self.cat_id = row[6]
        self.trig_id = row[7]
        self.over_id = row[8]
        self.p_type = row[9]
        self.cycle = PCycle(row[10], row[11], row[12])
        self.desc = row[13]

    @classmethod
    def headers(cls):
        return ['Amount', 'Income', 'Category', 'Trigger', 'Override', 'Type', 'Cycle', 'Date', 'Desc']