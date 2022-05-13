#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

class MapShelfmark():
    def __init__(self, string):
        parts = string.split(" - ")
        self.root = parts[0]
        try:
            self.folder = parts[1]
        except:
            self.folder = None
        self.arabic = self.replace_rom(self.root)
        self.normalized = self.normalize(self.arabic)
        self.omit_sheet = re.sub(" [IVXL]+", "", self.root)
        self.normalized2 = self.normalize(self.omit_sheet)
    def normalize(self, string):
        normalized = string.replace(" ", "-").replace(",", "-").replace(":", "-").replace(".", "-").replace("(", "").replace(")", "").lower()
        normalized = re.sub("([a-z])$", lambda group: "-" + group[1], normalized)
        normalized = re.sub("([a-z])([0-9])", lambda group: group[1] + "-" + group[2], normalized)
        return(normalized)
    def replace_rom(self, string):
        extract = re.findall(r" (([IVXL]+)-)?([IVXL]+)$", string)
        try:
            self.rom1, self.rom2 = extract[0][1], extract[0][2]
        except:
            return(string)
        else:
            if rom_arab(self.rom1) != None:
                string = re.sub(self.rom1 + "-", rom_arab(self.rom1) + "-", string)
            if rom_arab(self.rom2) != None:
                string = re.sub(self.rom2, rom_arab(self.rom2), string)
            #if self.rom1 != "":
            #    print(f"{string}: {self.rom1} - {self.rom2}")
            return(string)
            
def rom_arab(string):
    conc = {
        "I" : "1",
        "II" : "2",
        "III" : "3",
        "IV" : "4",
        "V" : "5",
        "VI" : "6",
        "VII" : "7",
        "VIII" : "8",
        "IX" : "9",
        "X" : "10",
        "XI" : "11",
        "XII" : "12",
        "XIII" : "13",
        "XIV" : "14",
        "XV" : "15",
        "XVI" : "16",
        "XVII" : "17",
        "XVIII" : "18",
        "XIX" : "19",
        "XX" : "20",
        "XXI" : "21",
        "XXII" : "22",
        "XXIII" : "23",
        "XXIV" : "24",
        "XXV" : "25",
        "XXVI" : "26",
        "XXVII" : "27",
        "XXVIII" : "28",
        "XXIX" : "29",
        "XXX" : "30",
        "XXXI" : "31",
        "XXXII" : "32",
        "XXXIII" : "33",
        "XXXIV" : "34",
        "XXXV" : "35",
        "XXXVI" : "36",
        "XXXVII" : "37",
        "XXXVIII" : "38",
        "XXXIX" : "39",
        "XL" : "40",
        "XLI" : "41",
        "XLII" : "42",
        "XLIII" : "43",
        "XLIV" : "44",
        "XLV" : "45",
        "XLVI" : "46",
        "XLVII" : "47",
        "XLVIII" : "48",
        "XLIX" : "49",
        "L" : "50"
    }
    try:
        return(conc[string])
    except:
        return("")
