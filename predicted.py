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

class Type(Enum):
    BILL = 1
    PRED = 2
    SUBSCR = 3
    MONTH = 4
    ELECT = 5
Types = bidict({'Bill': Type.BILL, 'Prediction': Type.PRED, 'Subscription': Type.SUBSCR, 'Monthly': Type.MONTH, 'Elective': Type.ELECT})

class Cycle(Enum):
    MONTHLY = 1
    WEEKLY = 2
    QUARTERLY = 3
    ANNUAL = 4
    BIWEEKLY = 5
    ADHOC = 6

Cycles = bidict({'Monthly': Cycle.MONTHLY, 'Weekly': Cycle.WEEKLY, 'Quarterly': Cycle.QUARTERLY, 'Annual': Cycle.ANNUAL, 'BiWeekly': Cycle.BIWEEKLY, 'Adhoc': Cycle.ADHOC})

class DayOfWeek(Enum):
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    SUN = 7

DaysOfWeek = bidict({'Monday': DayOfWeek.MON, 'Tuesday': DayOfWeek.TUE, 'Wednesday': DayOfWeek.WED, 'Thursday': DayOfWeek.THU, 'Friday': DayOfWeek.FRI, 'Saturday': DayOfWeek.SAT, 'Sunday': DayOfWeek.SUN})]

class Prediction(object):
    
    def __init__(self, db):
        self.db = db
    
    def get_typestr(self):
        return TypeToStr[self.p_type]
    
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
        self.comment = comment

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
        self.comment = row[12]

    @classmethod
    def headers(cls):
        return ['Name', 'Category', 'Trigger', 'Override', 'Type', 'Cycle', 'Date', 'Comment']