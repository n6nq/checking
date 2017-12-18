"""PCycle.py
# Cycle class notes

types

#methods
#    Cycle(typestr, valuestr)    #return new Cycle from input strings set values
#    Cycle(typestr, dstr, vstr)  #return new Cycle from input strings set values
    get_type_str    #get the cycle type as a string
    get_value_str   #get cycle value as a date, dow or dom str
    get_date_str    #get the datatime.date as a string
    get_dow_str     #get the day of week str
    get_dom_str     #get the day of month str
    is_weekly       #return bool 
    is_monthly      #return bool
    
    set_type        #set type with validated input string
    set_date        #set date with datetime.date
    set_date        #set date with QDate
    set_dow         #set day of week with validated string
    set_dom         #set day of month with vlidated string
    
#deprecated  methods
#    pred.get_cyclestr() #changes to cycle.get_type_str()
    pred.get_datestr()  #changes to cycle.get_value_str()
    pred.get_cycle_from_str()   #changes to cycle.set_type()
    
        cycle = pred.get_cycle_from_str(cyclestr)           #changes to Cycle(type, value)
        vdate = pred.get_vdate_from_str(cycle, vdatestr)    #changes to Cycle(type, value)
        
Changes
    pred.set_without_ids    #gets new param of type Cycle
    pred.set_with_ids       #gets new param of type Cycle
    pred.set_with_row       #need to build aand put in row
"""
from datetime import date, datetime
from bidict import bidict


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


class PCycle(object):
    
    def __init__(self, typestr=None, datestr=None, vdatestr=None):
        
        if typestr and typestr in Cycles:
            self.type = Cycles[typestr]
            if datestr:
                self.ddate = datetime.strptime(datestr, "%m-%d-%Y")
            if vdatestr:
                if vdatestr in DaysOfWeek:
                    self.vdate = DaysOfWeek[vdatestr]
                else:
                    self.vdate = int(vdatestr)

    def get_type_str(self):
        return Cycles.inv[self.type]