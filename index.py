"""Column Indexes for database base records. All SQLite rows are returned as tuples.
Normal access to the columns is like this: tuple[index]. The defined numbers in this file
provide something descriptive than using  numbers like 0,1,2,3,4,etc.  If you make change 
to the column definitiions of the tables in database.py, you will need to make changes."""

# ACCOUNTS
ACCT_OID = 0
ACCT_NAME = 1
ACCT_START = 2
ACCT_LAST = 3
ACCT_BANKURL = 4

#ENTRIES
ENTRY_OID = 0
ENTRY_CATEGORY = 1
ENTRY_CAT_ID = 2
ENTRY_TRIG_ID = 3
ENTRY_OVER_ID = 4
ENTRY_SDATE = 5
ENTRY_AMOUNT = 6
ENTRY_CLEARED = 7
ENTRY_CHECKNUM = 8
ENTRY_DESC = 9

#PREDICTIONS
PRED_OID = 0
PRED_AMOUNT = 1
PRED_INCOME = 2
PRED_CAT = 3
PRED_TRIG = 4
PRED_OVER = 5
PRED_CAT_ID = 6
PRED_TRIG_ID = 7
PRED_OVER_ID = 8
PRED_CYCLE = 9
PRED_DDATE = 10
PRED_VDATE = 11
PRED_DESC = 12

#CATEGORY
CAT_OID = 0
CAT_NAME = 1
CAT_SUPER = 2

#TRIGGERS
TRIG_OID = 0
TRIG_TRIGGER = 1
TRIG_CATEGORY = 2

#OVERRIDES
OVER_OID = 0
OVER_OVER = 1
OVER_CAT = 2 
