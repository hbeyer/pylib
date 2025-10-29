import math
import re
from datetime import datetime
import logging

class EasterDate():
    def __init__(self, year):
        if re.match(r"\d{3,4}", str(year)):
            self.year = int(year)
            self.old = self.gaussEasterOld()
            self.new = self.gaussEasterNew()
            return
        logging.error(f" Kein gültiges Jahr: {year}")
    def get_date(self, new = None):
        date_format = "%Y-%m-%d"
        if new in [None, True]:
            return(datetime.strptime(self.new, date_format))
        return(datetime.strptime(self.old, date_format))
    def get_date_ger(self, new = None):
        date_obj = self.get_date(new)
        return(date_obj.strftime("%d.%m.%Y"))
        
    def gaussEasterOld(self):
        a = self.year % 19
        b = self.year % 4
        c = self.year % 7
        m = 15
        d = ((19 * a) + m) % 30
        n = 6
        e = ((2 * b) + (4 * c) + (6 * d) + n) % 7
        day_march = 22 + d + e
        if d == 29 and e == 6:
            return(f"{self.year}-04-19")
        if d == 29 and e == 6 and ((11 * m) + 11) % 30 < 19:
            return(f"{self.year}-04-18")
        if day_march > 31:
            return(f"{self.year}-04-{str(day_march - 31).zfill(2)}")
        return(f"{self.year}-03-{str(day_march).zfill(2)}")

    def gaussEasterNew(self):
        a = self.year % 19
        b = self.year % 4
        c = self.year % 7
        k = math.floor(self.year / 100)
        p = math.floor(((8 * k) + 13) / 25)
        q = math.floor(k / 4)
        m = (15 + k - p - q) % 30
        d = ((19 * a) + m) % 30
        n = (4 + k - q) % 7
        e = ((2 * b) + (4 * c) + (6 * d) + n) % 7
        day_march = 22 + d + e
        if d == 29 and e == 6:
            return(f"{self.year}-04-19")
        if d == 28 and e == 6 and (((11 * m) + 11) % 30) < 19:
            return(f"{self.year}-04-18")
        if day_march > 31:
            return(f"{self.year}-04-{str(day_march - 31).zfill(2)}")
        return(f"{self.year}-03-{str(day_march).zfill(2)}")