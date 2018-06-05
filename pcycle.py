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
from datetime import date, datetime, timedelta
from bidict import bidict


#class Cycle(Enum):
#    MONTHLY = 1
#    WEEKLY = 2
#    QUARTERLY = 3
#    ANNUAL = 4
#    BIWEEKLY = 5
#    ADHOC = 6

Cycles = bidict({
    #'None': 0, 
    'Monthly': 1, 'Weekly': 2, 'Quarterly': 3, 'Annual': 4, 'BiWeekly': 5, 'Adhoc': 6})


DaysOfWeek = bidict({'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6})


class PCycle(object):
    
    def __init__(self, ctype=None, ddate=None, vdate=None):
        
        if ctype == None or ddate == None or vdate == None:
            assert(False)
        
        if type(ctype) == str:
            if ctype in Cycles:
                self.ctype = Cycles[ctype]
            else:
                assert(False)
        elif type(ctype) == int:
            if ctype in Cycles.inv:
                self.ctype = ctype
            else:
                assert(False)
        else:
            assert(False)
            
        if type(ddate) == str:
            self.ddate = datetime.strptime(ddate, "%m-%d-%Y")
        elif type(ddate) == date:
            self.ddate = ddate
        else:
            assert(False)
        #if vdate:
        if type(vdate) == str:
            if vdate in DaysOfWeek:
                self.vdate = DaysOfWeek[vdate]
            elif vdate == '':
                self.vdate = 0
            elif int(vdate) in range(1, 32):
                self.vdate = int(vdate)
            else:
                assert(False)
        elif type(vdate) == int:
            if vdate in DaysOfWeek:
                self.vdate = vdate
            elif vdate in range(0, 32):
                self.vdate = vdate
            else:
                assert(False)
        else:
            assert(False)
            
    def __str__(self):
        return 'Type: ' + self.get_type_str() + ' ' + self.get_date_str()
    
    def get_type_str(self):
        return Cycles.inv[self.ctype]
    
    def get_date_str(self):
        if Cycles.inv[self.ctype] == 'Monthly':
            return str(self.vdate)
        elif Cycles.inv[self.ctype] == 'Weekly':
            if self.vdate >= 7:
                return "Over"   #HACK
            return DaysOfWeek.inv[self.vdate]
        elif self.ctype in Cycles.inv:
            return str(self.ddate)
        else:
            assert(False)
        
    def get_date_type(self):
        if Cycles.inv[self.ctype] == 'Monthly':
            return type(self.vdate)
        elif Cycles.inv[self.ctype] == 'Weekly':
            return type(self.vdate)
        elif self.ctype in Cycles.inv:
            return type(self.ddate)
        else:
            assert(False)

    def in_the_past(self, today):
        ctype = self.ctype
        if ctype == Cycles['Weekly'] or ctype == Cycles['Monthly']:
            return False
        else:
            if self.ddate >= today:
                return False
        return True
    
    def promote(self, today):
        # Monthly, Weekly, Quarterly, Annual, BiWeekly, Adhoc
        assert(self.ddate < today)
        ctype = self.ctype
        while self.ddate < today:
            if ctype == Cycles['Quarterly']:
                self.ddate += timedelta(91)
                continue
            elif ctype == Cycles['Annual']:
                self.ddate += timedelta(365)
                continue
            elif ctype == Cycles['BiWeekly']:
                self.ddate += timedelta(14)
                continue
            else:
                assert(False)

    def future_dates(self, start, end):
        # Monthly=1, Weekly=2, Quarterly=3, Annual=4, BiWeekly=5, Adhoc=6
        ctype = self.ctype
        
        if ctype == Cycles['Monthly']:
            return self.future_monthlies(start, end)
        elif ctype == Cycles['Annual']:
            return self.future_annuals(start, end)
        elif ctype == Cycles['Weekly']:
            return self.future_weeklies(start, end)
        elif ctype == Cycles['BiWeekly']:
            return self.future_biweeklies(start, end)
        elif ctype == Cycles['Quarterly']:
            return self.future_quarterlies(start, end)
        elif ctype == Cycles['Adhoc']:
            return self.future_adhoc(start, end)
        else:
            assert(False)

    def future_quarterlies(self, start, end):
        new_date = date(self.ddate.year, self.ddtae.month, self.ddate.day)
        while new_date < start:
            new_date += timedelta(days=91)
        if new_date <= end:
            return [new_date]
        return []
    
    def future_adhoc(self, start, end):
        if self.ddate >= start and self.ddate <= end:
            return [date(self.ddate.year, self.ddate.month, self.ddate.day)]
        return []
    
    def future_annuals(self, start, end):
        new_date = date(self.ddate.year, self.ddate.month, self.ddate.day)
        if new_date < start:
            new_date = new_date.replace(year=(new_date.year+1))
        if new_date >= start and new_date <= end:
            print(new_date)
            return [new_date]
        else:
            return[]
            
    def future_monthlies(self, start, end):
        futures = []
        d_next = start.replace(day=self.vdate)

        if self.vdate >= start.day:
            futures.append(d_next)
            print(d_next)
        while d_next < end:
            n_month = d_next.month + 1
            n_year = d_next.year
            
            if n_month > 12:
                n_month = 1
                n_year += 1
            
            d_next = d_next.replace(month=n_month, year=n_year)
            if d_next <= end:
                futures.append(d_next)
                print(d_next)
        return futures

    def future_weeklies(self, start, end):
        futures = []
        dow = start.weekday()
        want = self.vdate
        addin = ((want - dow) + 7) % 7
        d_next = start + timedelta(days=addin)
        
        while d_next >= start and d_next <= end:
            print(d_next)
            futures.append(d_next)
            d_next = d_next + timedelta(days=7)
        return futures
    
    def future_biweeklies(self, start, end):
        futures = []
        d_next = self.ddate
        
        while d_next <= end:
            if d_next >= start:
                print(d_next)
                futures.append(d_next)
            d_next = d_next + timedelta(days=14)
        return futures
    
    def promote_all(self, today, dnext, first):
        # Monthly=1, Weekly=2, Quarterly=3, Annual=4, BiWeekly=5, Adhoc=6
        ctype = self.ctype
        
#        if self.ddate > today and first:
#            return dnext
        
        if ctype == Cycles['Monthly']:
            if first:
                if self.vdate >= today.day:
                    new_date = today.replace(day=self.vdate)
                else:
                    assert(dnext.day == self.vdate)
                    month = dnext
                    new_date = dnext
            if self.vdate >= next.day <= self.vdate and first:
                new_date = dnext.replace(day=self.vdate)
            else:
                if dnext.month == 12:
                    month = 1
                    year = dnext.year + 1
                else:
                    month = dnext.month + 1
                    year = dnext.year
                new_date = dnext.replace(year=year, month=month, day=self.vdate)
        elif ctype == Cycles['Weekly']:
            new_date = dnext + timedelta(weeks=1)
        elif ctype == Cycles['Quarterly']:
            new_date = self.ddate + timedelta(91)
        elif ctype == Cycles['Annual']:
            
            new_date = self.ddate + timedelta(365)
        elif ctype == Cycles['BiWeekly']:
            new_date = self.ddate + timedelta(14)
        else:
            assert(False)
        return new_date
    
    @classmethod
    def get_cycle_from_str(cls, str):
        assert(str in Cycles)
        return Cycles[str]

    @classmethod
    def get_vdate_from_str(cls, cycle, str):
        if cycle == Cycles['Weekly']:
            assert(str in DaysOfWeek)
            return DaysOfWeek[str]
        elif cycle == Cycles['Monthly']:
            if str == '':
                return 0
            assert(int(str))
            return int(str)
        else:
            return 0

    @classmethod
    def get_cycle_list(cls):
        cycleList = []
        for key in Cycles.keys():
            cycleList.append(key)
        return cycleList
    


