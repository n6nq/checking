""" predicted.py  --- This data type stores bills and other predictable transactions. They
will be used to project future balances for 'what-if scenarios.

Amount
Name
category
trigger
type bill, prediction, subscription, monthly, elective
cycle monthly, weekly, quarterly, annual, bi-weekly, ad-hoc
date day-of-month, day-of-week, day/month, adhoc
"""
from enum import Enum
from bidict import bidict

#class PType(Enum):
#    BILL = 1
#    PRED = 2
#    SUBSCR = 3
#    MONTH = 4
#    ELECT = 5
Types = bidict({'None': 0,'Bill': 1, 'Prediction': 2, 'Subscription': 3, 'Monthly': 4, 'Elective': 5})

#class Cycle(Enum):
#    MONTHLY = 1
#    WEEKLY = 2
#    QUARTERLY = 3
#    ANNUAL = 4
#    BIWEEKLY = 5
#    ADHOC = 6

Cycles = bidict({'None': 0,'Monthly': 1, 'Weekly': 2, 'Quarterly': 3, 'Annual': 4, 'BiWeekly': 5, 'Adhoc': 6})

#class DayOfWeek(Enum):
#    NONE = 0
#    MON = 1
#    TUE = 2
#    WED = 3
#    THU = 4
#    FRI = 5
#    SAT = 6
#    SUN = 7

DaysOfWeek = bidict({'None': 0, 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7})
#DaysOfWeek = bidict({'None': DayOfWeek.NONE,'Mon': DayOfWeek.MON, 'Tue': DayOfWeek.TUE, 'Wed': DayOfWeek.WED, 'Thu': DayOfWeek.THU, 'Fri': DayOfWeek.FRI, 'Sat': DayOfWeek.SAT, 'Sun': DayOfWeek.SUN})

class Prediction(object):
    
    def __init__(self, db):
        self.db = db
    
    def get_typestr(self):
        return Types.inv[self.p_type]

    def get_cyclestr(self):
        return Cycles.inv[self.cycle]
    
    def get_datestr(self):
        if self.cycle == Cycles['Weekly']:
            return DaysOfWeek.inv[self.vdate]
        elif self.cycle == Cycles['Monthly']:
            return str(self.vdate)
        else:
            return str(self.ddate)
        
    def get_cycle_from_str(self, str):
        self.cycle = Cycles[str]
        return self.cycle
    
    def get_ptype_from_str(self, str):
        self.p_type = Types[str]
        return self.p_type
    def get_vdate_from_str(self, cycle, str):
        if cycle == Cycles['Weekly']:
            self.vdate = DaysOfWeek[str]
            return self.vdate
        elif cycle == Cycles['Monthly']:
            self.vdate = int(str)
        else:
            self.vdate = 0      # equals none
        return self.vdate
    def set_without_ids(self, name, cat, trig=None, over=None, p_type=None, cycle=None, ddate=None, vdate=None, desc=None):
        self.name = name
        self.cat = cat
        self.trig = trig
        self.over = over
        self.cat_id = 0
        self.trig_id = 0
        self.over_id = 0
        self.p_type = p_type
        self.cycle = cycle
        self.ddate = ddate
        self.vdate = vdate
        self.desc = desc

    def set_with_ids(self, oid, name, cat, trig=None, over=None, cat_id=0, trig_id=0, over_id=0, p_type=None, cycle=None, ddate=None, vdate=None, desc=None):
        self.oid = oid
        self.name = name
        self.cat = cat
        self.trig = trig
        self.over = over
        self.cat_id = cat_id
        self.trig_id = trig_id
        self.over_id = over_id
        self.p_type = p_type
        self.cycle = cycle
        self.ddate = ddate
        self.vdate = vdate
        self.desc = desc

    def set_with_row(self, row):
        self.oid = row[0]
        self.name = row[1]
        self.cat = row[2]
        self.trig = row[3]
        self.over = row[4]
        self.cat_id = row[5]
        self.trig_id = row[6]
        self.over_id = row[7]
        self.p_type = row[8]
        self.cycle = row[9]
        self.ddate = row[10]
        self.vdate = row[11]
        self.desc = row[12]

    @classmethod
    def headers(cls):
        return ['Name', 'Category', 'Trigger', 'Override', 'Type', 'Cycle', 'Date', 'Desc']