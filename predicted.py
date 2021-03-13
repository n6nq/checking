""" predicted.py  --- This data type stores bills and other predictable transactions. They
will be used to project future balances for 'what-if scenarios.

Amount
category
trigger
type bill, prediction, subscription, monthly, elective
cycle monthly, weekly, quarterly, annual, bi-weekly, ad-hoc
date day-of-month, day-of-week, day/month, adhoc
"""

""" NOTES:
    TODOS: Remove type from predictions and UI
    
"""
import index
from enum import Enum
from bidict import bidict
from pcycle import PCycle, Cycles
from money import Money
from datetime import datetime, timedelta

#              jan feb mar apr may jun jul aug sep oct nov dec
DaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Keep Types in alphabetical order so type combo will sort correctly
#Types = bidict({'None': 0, 'Bill': 1, 'Elective': 2, 'Income': 3, 'Monthly': 4, 'Prediction': 5, 'Subscription': 6})
#TODO -- Get rid of types
class Prediction(object):
    
    def __init__(self, db):
        self.db = db
        self.cycle = None
    
    def __str__(self):
        return str(self.cycle) + ' Amount: ' + self.amount.as_str() + ' cat: ' + self.cat + ' trig: ' + self.trig + ' desc: ' + self.desc
    
    #def get_typestr(self):
        #return Types.inv[self.p_type]

    
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
        end = (today + timedelta(7)).day
        start = today.day
        if ctype == Cycles['Weekly']:
            return True
        elif ctype == Cycles['Monthly']:
            pday = self.cycle.vdate
            if end > start and pday >= start and pday <= end:
                return True
            elif start > end and (pday >= start or pday <= end):
                return True
            else:
                return False
        elif ctype == Cycles['Quarterly'] or ctype == Cycles['Annual'] or \
             ctype == Cycles['BiWeekly'] or ctype == Cycles['Adhoc']:
            if self.cycle.in_the_past(today):
                self.cycle.promote(today)
            end = (today + timedelta(7))
            if self.cycle.ddate <= end:
                return True
        else:
            assert(False)
        return False
    
    def in_next_month(self, today):
        ctype = self.cycle.ctype
        end = (today + timedelta(30)).day
        start = today.day
        if ctype == Cycles['Weekly'] or ctype == Cycles['Monthly']:
            return True
        elif ctype == Cycles['Quarterly'] or ctype == Cycles['Annual'] or \
             ctype == Cycles['BiWeekly'] or ctype == Cycles['Adhoc']:
            if self.cycle.in_the_past(today):
                self.cycle.promote(today)
            end = (today + timedelta(30))
            if self.cycle.ddate <= end:
                return True
        else:
            assert(False)
        return False
    
    def in_three_month(self, today):
        ctype = self.cycle.ctype
        end = (today + timedelta(30)).day
        start = today.day
        if ctype == Cycles['Weekly'] or ctype == Cycles['Monthly']:
            return True
        elif ctype == Cycles['Quarterly'] or ctype == Cycles['Annual'] or \
             ctype == Cycles['BiWeekly'] or ctype == Cycles['Adhoc']:
            if self.cycle.in_the_past(today):
                self.cycle.promote(today)
            end = (today + timedelta(91))
            if self.cycle.ddate <= end:
                return True
        else:
            assert(False)
        return False
    
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
        self.amount = Money.from_number(lst[index.PRED_AMOUNT])  # TODO
        self.income = lst[index.PRED_INCOME]
        self.cat = lst[index.PRED_CAT]
        self.trig = lst[index.PRED_TRIG]
        self.over = lst[index.PRED_OVER]
        self.cat_id = lst[index.PRED_CAT_ID]
        self.trig_id = lst[index.PRED_TRIG_ID]
        self.over_id = lst[index.PRED_OVER_ID]
        self.cycle = PCycle(lst[index.PRED_CYCLE], lst[index.PRED_DDATE], lst[index.PRED_VDATE])
        self.desc = lst[index.PRED_DESC]
        
    def set_with_list(self, lst):
        self.oid = lst[0] # TODO
        self.set_without_oid(lst)
        
    def update_with_list(self, lst):
        assert(self.oid == lst[0])  # TODO
        self.set_without_oid(lst)
        
    #---- CLASSMETHODS -------------------------------#
    @classmethod
    def headers(cls):
        return ['Amount', 'Income', 'Category', 'Trigger', 'Override', 'Cycle', 'Date', 'Desc']
    
    #@classmethod
    #def get_type_list(cls):
        #keyList = []
        #for key in Types.keys():
            #keyList.append(key)
        #return keyList
    
    #@classmethod
    #def get_ptype_from_str(cls, str):
        #assert(str in Types)
        #return Types[str]

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
    
    
    