"""databsae.py --- this module provides an application specific interface
   to a sqlite3 database for storage of application records. This module is
   also responsible all table creation and maintenance."""

# tables to create
#
# accounts
# transactions
# categories
# triggers
# overrides

import sqlite3

class database(object):