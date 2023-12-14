#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import logging
from lib import romnumbers as rn

class Shelfmark:
    def __init__(self, whole):
        self.valid = False
        if not isinstance(whole, str):
            #logging.error(f"Ungültige Signatur: {whole}")
            return
        self.whole = whole[0:140].strip()
        if "544/VP" not in self.whole:
            #logging.error(f"Ungültige Signatur: {self.whole}")
            return
        self.root = "544/VP"
        self.container = ""
        self.number = ""
        self.number_sort = ""
        self.container_sort = ""
        self.sort = ""
        self.augm = ""
        parts = re.search(r"544/VP (VP)?(\d+)?[ /-]?([\d]+|[IVXLCDM]+)?([abc])?", self.whole)
        if parts == None:
            logging.error(f"Signatur nicht zu verarbeiten: {self.whole}")
            return
        if parts.group(2) != None:
            self.container = parts.group(2)
        if parts.group(3) != None:
            self.number = parts.group(3)
        if parts.group(4) != None:
            self.augm = parts.group(4)
        self.valid = True
        self.container_sort = self.container.zfill(4)
        if re.match(f"^[IVXLCDM]+$", self.number):
            self.number_sort = "R-" + str(rn.to_arabic(self.number)).zfill(4)
        elif re.match(f"^\d+$", self.number):
            self.number_sort = "A-" + self.number.zfill(4)
        else:
            self.number_sort = self.number
            logging.error(f"Unregelmäßige Nummer bei {self.whole}")
        self.sort = f"544VP-{self.container_sort}-{self.number_sort}{self.augm}"
    def __str__(self):
        if self.valid == False:
            return(f"Ungültige Signatur: {self.whole}")
        return(f"Vitae Pomeranorm (544/VP), Container {self.container}, Stück Nr. {self.number}")
    