#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re

class Numeral:
    conc = {
        "i" : 1,
        "v" : 5,
        "x" : 10,
        "l" : 50,
        "c" : 100,
        "d" : 500,
        "m" : 1000
    }
    conca = {
        1000 : "m",
        500 : "d",
        100 : "c",
        50 : "l",
        10 : "x",
        5 : "v",
        1 : "i"
    }
    subst = {
        "dcccc" : "cm",
        "lxxxx" : "xc",
        "viiii" : "ix",
        "cccc" : "cd",
        "xxxx" : "xl",
        "iiii" : "iv"
    }

def to_arabic(lett):
    sum = 0
    subtr = False
    lett = lett.strip().lower().replace(".", "").replace(" ", "")
    if re.match(r"[ivxlcdm]+", lett) == None:
        return(None)
    rev = lett[::-1]
    last = 0
    for let in rev:
        val = Numeral.conc[let]
        if val >= last:
            sum += val
            subtr = False
        elif val < last:
            sum -= val
            subtr = True
        elif val == last and subtr == True:
            sum -= val
        last = val
    return(sum)
    
def to_roman(num):
    if isinstance(num, int) == False:
        return(None)
    rom = ""
    while num > 0:
        for key in Numeral.conca:
            if num >= key:
                rom = rom + Numeral.conca[key]
                num -= key
                break
    for add, sub in Numeral.subst.items():
        rom = rom.replace(add, sub)
    return(rom)