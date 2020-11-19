#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import table_winibw as tw
from lib import shelfmark as sm
from lib import localsql as ls

table = tw.Table("augusteer-luther.csv")
table.toSQLite()