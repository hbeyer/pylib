#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import csvt
import collections

class Catalogue:
# Daten nach Maria von Katte, Herzog August und die Kataloge seiner Bibliothek, in: Wolfenbütteler Beiträge 1 (1972), S. 168-199, hier S. 177-182
    struct = [
    { "start":1, "end":79, "group":"Theologici in 2°", "dateBegin":"1625-02-25", "year":1625, "writer":"Herzog August" },
    { "start":80, "end":429, "group":"Theologici in 4° etc.", "dateBegin":"1625-04-21", "year":1625, "writer":"Herzog August" },
    { "start":430, "end":451, "group":"Juridici in 2°", "dateBegin":"1626-02-26", "year":1626, "writer":"Herzog August" },
    { "start":452, "end":515, "group":"Juridici in 4° etc.", "dateBegin":"1626-03-04", "year":1626, "writer":"Herzog August" },
    { "start":516, "end":613, "group":"Historici in 2°", "dateBegin":"1626-03-28", "year":1626, "writer":"Herzog August" },
    { "start":614, "end":757, "group":"Historici in 4° etc.", "dateBegin":"1626-05-10", "year":1626, "writer":"Herzog August" },
    { "start":758, "end":769, "group":"Bellici in 2°", "dateBegin":"1626-07-17", "year":1626, "writer":"Herzog August" },
    { "start":770, "end":781, "group":"Bellici in 4° etc.", "dateBegin":"1626-07-19", "year":1626, "writer":"Herzog August" },
    { "start":782, "end":791, "group":"Politici in 2°", "dateBegin":"1626-07-21", "year":1626, "writer":"Herzog August" },
    { "start":792, "end":867, "group":"Politici in 4° etc.", "dateBegin":"1626-07-24", "year":1626, "writer":"Herzog August" },
    { "start":868, "end":869, "group":"Oeconomici in 2°", "dateBegin":"1626-08-21", "year":1626, "writer":"Herzog August" },
    { "start":870, "end":873, "group":"Oeconomici in 4° etc.", "dateBegin":"1626-08-21", "year":1626, "writer":"Herzog August" },
    { "start":874, "end":879, "group":"Ethici in 2°", "dateBegin":"1626-08-22", "year":1626, "writer":"Herzog August" },
    { "start":880, "end":907, "group":"Ethici in 4° etc.", "dateBegin":"1626-08-26", "year":1626, "writer":"Herzog August" },
    { "start":908, "end":917, "group":"Medici in 2°", "dateBegin":"1626-09-11", "year":1626, "writer":"Herzog August" },
    { "start":918, "end":957, "group":"Medici in 4° etc.", "dateBegin":"1626-09-15", "year":1626, "writer":"Herzog August" },
    { "start":958, "end":959, "group":"Geographici in 2°", "dateBegin":"1626-10-11", "year":1626, "writer":"Herzog August" },
    { "start":960, "end":693, "group":"Geographici in 4° etc.", "dateBegin":"1626-10-11", "year":1626, "writer":"Herzog August" },
    { "start":964, "end":696, "group":"Astronomici in 2°", "dateBegin":"1626-10-12", "year":1626, "writer":"Herzog August" },
    { "start":970, "end":989, "group":"Astronomici in 4° etc.", "dateBegin":"1626-10-14", "year":1626, "writer":"Herzog August" },
    { "start":990, "end":991, "group":"Musici in 2°", "dateBegin":"1626-10-27", "year":1626, "writer":"Herzog August" },
    { "start":992, "end":993, "group":"Musici in 4° etc.", "dateBegin":"1626-10-27", "year":1626, "writer":"Herzog August" },
    { "start":994, "end":1001, "group":"Physici in 2°", "dateBegin":"1626-10-27", "year":1626, "writer":"Herzog August" },
    { "start":1002, "end":1029, "group":"Physici in 4° etc.", "dateBegin":"1626-10-30", "year":1626, "writer":"Herzog August" },
    { "start":1030, "end":1039, "group":"Geometrici in 2°", "dateBegin":"1626-11-15", "year":1626, "writer":"Herzog August" },
    { "start":1040, "end":1049, "group":"Geometrici in 4° etc.", "dateBegin":"1626-11-18", "year":1626, "writer":"Herzog August" },
    { "start":1050, "end":1051, "group":"Arithmetici in 2°", "dateBegin":"1626-11-23", "year":1626, "writer":"Herzog August" },
    { "start":1052, "end":1055, "group":"Arithmetici in 4° etc.", "dateBegin":"1626-11-23", "year":1626, "writer":"Herzog August" },
    { "start":1056, "end":1059, "group":"Poetici in 2°", "dateBegin":"1626-11-23", "year":1626, "writer":"Herzog August" },
    { "start":1060, "end":1111, "group":"Poetici in 4° etc.", "dateBegin":"1626-11-25", "year":1626, "writer":"Herzog August" },
    { "start":1112, "end":1112, "group":"Logici in 2°", "dateBegin":"1627-01-25", "year":1627, "writer":"Herzog August" },
    { "start":1113, "end":1115, "group":"Logici in 4° etc.", "dateBegin":"1627-01-25", "year":1627, "writer":"Herzog August" },
    { "start":1116, "end":1119, "group":"Rhetorici in 2°", "dateBegin":"1627-01-27", "year":1627, "writer":"Herzog August" },
    { "start":1120, "end":1153, "group":"Rhetorici in 4° etc.", "dateBegin":"1627-01-29", "year":1627, "writer":"Herzog August" },
    { "start":1154, "end":1159, "group":"Grammatici in 2°", "dateBegin":"1627-02-19", "year":1627, "writer":"Herzog August" },
    { "start":1160, "end":1175, "group":"Grammatici in 4° etc.", "dateBegin":"1627-02-21", "year":1627, "writer":"Herzog August" },
    { "start":1176, "end":1223, "group":"Quodlibetici in 2°", "dateBegin":"1627-02-28", "year":1627, "writer":"Herzog August" },
    { "start":1224, "end":1439, "group":"Quodlibetici in 4° etc.", "dateBegin":"1627-07-13", "year":1627, "writer":"Herzog August" },
    { "start":1440, "end":1485, "group":"Manuscripti in 2°", "dateBegin":"1627-07-30", "year":1627, "writer":"Herzog August" },
    { "start":1486, "end":1521, "group":"Manuscripti in 4° etc.", "dateBegin":"1627-08-10", "year":1627, "writer":"Herzog August" },
    { "start":1522, "end":1541, "group":"Libri Varii", "dateBegin":"1627-08-12", "year":1627, "writer":"Herzog August" },
    { "start":1542, "end":1667, "group":"Libri Varii", "dateBegin":"1627", "year":1627, "writer":"Herzog August" },
    { "start":1668, "end":1697, "group":"Libri Varii", "dateBegin":"1628", "year":1628, "writer":"Herzog August" },
    { "start":1698, "end":1776, "group":"Libri Varii", "dateBegin":"1629", "year":1628, "writer":"Herzog August" },
    { "start":1777, "end":1966, "group":"Libri Varii", "dateBegin":"1630", "year":1630, "writer":"Herzog August" },
    { "start":1967, "end":2378, "group":"Libri Varii", "dateBegin":"1631", "year":1631, "writer":"Herzog August" },
    { "start":2379, "end":2400, "group":"Libri Varii", "dateBegin":"1632", "year":1632, "writer":"Herzog August" },
    { "start":2401, "end":2405, "group":"Libri Varii", "dateBegin":"1632-06-22", "year":1632, "writer":"Herzog August" },
    { "start":2406, "end":2510, "group":"Libri Varii", "dateBegin":"1633", "year":1633, "writer":"Herzog August" },
    { "start":2511, "end":2738, "group":"Libri Varii", "dateBegin":"1634", "year":1634, "writer":"Herzog August" },
    { "start":2739, "end":2787, "group":"Libri Varii", "dateBegin":"1635", "year":1635, "writer":"Herzog August" },
    { "start":2788, "end":2904, "group":"Libri Varii", "dateBegin":"1636-09-23", "year":1636, "writer":"Herzog August" },
    { "start":2905, "end":2954, "group":"Libri Varii", "dateBegin":"1637", "year":1637, "writer":"Herzog August" },
    { "start":2955, "end":3052, "group":"Libri Varii", "dateBegin":"1638", "year":1638, "writer":"Herzog August" },
    { "start":3053, "end":3210, "group":"Libri Varii", "dateBegin":"1640", "year":1640, "writer":"Herzog August" },
    { "start":3211, "end":3346, "group":"Libri Varii", "dateBegin":"1641", "year":1641, "writer":"Herzog August" },
    { "start":3347, "end":3383, "group":"Libri Varii", "dateBegin":"1642", "year":1642, "writer":"Herzog August" },
    { "start":3384, "end":3398, "group":"Libri Varii", "dateBegin":"1643", "year":1643, "writer":"Herzog August" },
    { "start":3399, "end":3408, "group":"Libri Varii", "dateBegin":"1644", "year":1644, "writer":"Herzog August" },
    { "start":3409, "end":3426, "group":"Libri Varii", "dateBegin":"1645", "year":1645, "writer":"Herzog August" },
    { "start":3427, "end":3578, "group":"Libri Varii", "dateBegin":"1646", "year":1646, "writer":"Herzog August" },
    { "start":3579, "end":3599, "group":"Libri Varii", "dateBegin":"1647", "year":1647, "writer":"Herzog August" },
    { "start":3600, "end":3600, "group":"Libri Varii", "dateBegin":"1647-05-02", "year":1647, "writer":"Herzog August" },
    { "start":3601, "end":3659, "group":"Libri Varii", "dateBegin":"1647-05-03", "year":1647, "writer":"Herzog August" },
    { "start":3660, "end":3691, "group":"Libri Varii", "dateBegin":"1648", "year":1648, "writer":"Herzog August" },
    { "start":3692, "end":3698, "group":"Libri Varii", "dateBegin":"1648", "year":1648, "writer":"H. J. Willershausen" },
    { "start":3697, "end":3769, "group":"Libri Varii", "dateBegin":"1649", "year":1649, "writer":"H. J. Willershausen" },
    { "start":3770, "end":3848, "group":"Libri Varii", "dateBegin":"1650", "year":1650, "writer":"H. J. Willershausen" },
    { "start":3849, "end":4035, "group":"Libri Varii", "dateBegin":"1650-10-08", "year":1650, "writer":"J. H. Arlt" },
    { "start":4036, "end":4210, "group":"Libri Varii", "dateBegin":"1652", "year":1652, "writer":"J. H. Arlt" },
    { "start":4211, "end":4236, "group":"Libri Varii", "dateBegin":"1653", "year":1653, "writer":"J. H. Arlt" },
    { "start":4237, "end":4350, "group":"Libri Varii", "dateBegin":"1654", "year":1654, "writer":"J. H. Arlt" },
    { "start":4351, "end":4420, "group":"Libri Varii", "dateBegin":"1655", "year":1655, "writer":"J. H. Arlt" },
    { "start":4421, "end":4464, "group":"Libri Varii", "dateBegin":"1656", "year":1656, "writer":"J. H. Arlt" },
    { "start":4465, "end":4467, "group":"Libri Varii", "dateBegin":"1656", "year":1656, "writer":"H. J. Willershausen" },
    { "start":4468, "end":4475, "group":"Libri Varii", "dateBegin":"1664-05", "year":1664, "writer":"H. J. Willershausen, J. H. Arlt" },
    { "start":4476, "end":4740, "group":"Libri Varii", "dateBegin":"1664", "year":1664, "writer":"J. H. Arlt" },
    { "start":4741, "end":4800, "group":"Libri Varii", "dateBegin":"1665", "year":1665, "writer":"J. H. Arlt" },
    { "start":4801, "end":4940, "group":"Libri Varii", "dateBegin":"1655-08-10", "year":1655, "writer":"Unbekannt" },    
    { "start":4941, "end":5020, "group":"Libri Varii", "dateBegin":"um 1656", "year":1656, "writer":"J. H. Arlt" },    
    { "start":5021, "end":5087, "group":"Libri Varii", "dateBegin":"1657", "year":1657, "writer":"J. H. Arlt" },    
    { "start":5088, "end":5263, "group":"Libri Varii", "dateBegin":"1658", "year":1658, "writer":"J. H. Arlt" },    
    { "start":5264, "end":5453, "group":"Libri Varii", "dateBegin":"1659", "year":1659, "writer":"J. H. Arlt" },    
    { "start":5453, "end":5731, "group":"Libri Varii", "dateBegin":"1660", "year":1660, "writer":"J. H. Arlt" },    
    { "start":5732, "end":5851, "group":"Libri Varii", "dateBegin":"1663", "year":1663, "writer":"J. H. Arlt" },    
    { "start":5852, "end":5999, "group":"Libri Varii", "dateBegin":"1664", "year":1664, "writer":"J. H. Arlt" },    
    { "start":6000, "end":6000, "group":"Libri Varii", "dateBegin":"1665-08-02", "year":1665, "writer":"J. H. Arlt" },    
    { "start":6001, "end":6165, "group":"Libri Varii", "dateBegin":"1665-08-03", "year":1665, "writer":"J. H. Arlt" },    
    { "start":6166, "end":6358, "group":"Libri Varii", "dateBegin":"1666", "year":1666, "writer":"J. H. Arlt" },    
    { "start":6359, "end":6680, "group":"Libri Varii", "dateBegin":"1667-07-08", "year":1667, "writer":"J. H. Arlt" },    
    { "start":6681, "end":6695, "group":"Libri Varii", "dateBegin":"1667", "year":1667, "writer":"J. H. Arlt" },    
    { "start":6696, "end":6700, "group":"Libri Varii", "dateBegin":"1668-1669", "year":1668, "writer":"J. H. Arlt" },    
    { "start":6701, "end":6706, "group":"Libri Varii", "dateBegin":"1671?", "year":1671, "writer":"K. H. Möser" },    
    { "start":6707, "end":6708, "group":"Libri Varii", "dateBegin":"1672", "year":1672, "writer":"K. H. Möser" },    
    { "start":6709, "end":6711, "group":"Libri Varii", "dateBegin":"1674", "year":1674, "writer":"K. H. Möser" },    
    { "start":6712, "end":6715, "group":"Libri Varii", "dateBegin":"1675", "year":1675, "writer":"K. H. Möser" },
    { "start":6716, "end":6721, "group":"Libri Varii", "dateBegin":"1680", "year":1680, "writer":"K. H. Möser" },
    { "start":6722, "end":6792, "group":"Libri Varii", "dateBegin":"1682?", "year":1682, "writer":"M. Ritthaler" },
    { "start":6793, "end":6872, "group":"Libri Varii", "dateBegin":"1682-1684", "year":1682, "writer":"J. T. Reinerding" },
    { "start":6873, "end":6874, "group":"Libri Varii", "dateBegin":"1682-1684", "year":1683, "writer":"M. Ritthaler" },
    { "start":6875, "end":6875, "group":"Libri Varii", "dateBegin":"1682-1684", "year":1684, "writer":"J. T. Reinerding, M. Ritthaler" },
    { "start":6876, "end":6878, "group":"Libri Varii", "dateBegin":"1684", "year":1684, "writer":"M. Ritthaler" },    
    { "start":6879, "end":6884, "group":"Libri Varii", "dateBegin":"1687", "year":1687, "writer":"M. Ritthaler" },    
    { "start":6885, "end":6887, "group":"Libri Varii", "dateBegin":"1687-1688", "year":1687, "writer":"K. A. Stenger" },    
    { "start":6888, "end":6936, "group":"Libri Varii", "dateBegin":"1687-1688", "year":1688, "writer":"J. T. Reinerding" },    
    { "start":6937, "end":6937, "group":"Libri Varii", "dateBegin":"1688", "year":1688, "writer":"J. T. Reinerding" },    
    { "start":6938, "end":6938, "group":"Libri Varii", "dateBegin":"1689", "year":1689, "writer":"J. T. Reinerding" },    
    { "start":6939, "end":6946, "group":"Libri Varii", "dateBegin":"1690", "year":1690, "writer":"J. T. Reinerding" },    
    { "start":6947, "end":6949, "group":"Libri Varii", "dateBegin":"1691", "year":1691, "writer":"J. T. Reinerding" },    
    { "start":6950, "end":6954, "group":"Libri Varii", "dateBegin":"1692", "year":1692, "writer":"J. T. Reinerding" },    
    { "start":6955, "end":6961, "group":"Libri Varii", "dateBegin":"1693", "year":1693, "writer":"J. T. Reinerding" },    
    { "start":6962, "end":6962, "group":"Libri Varii", "dateBegin":"nach 1705", "year":1705, "writer":"L. Hertel" },    
    { "start":6963, "end":7058, "group":"Libri Varii", "dateBegin":"nach 1705", "year":1705, "writer":"J. T. Reinerding" },    
    { "start":7059, "end":7500, "group":"Libri Varii", "dateBegin":"1698", "year":1698, "writer":"G. B. Lauterbach" }
    ]
    def __init__(self):
        pass
    def get_section(self, page):
        for sect in self.struct:
            if sect["start"] <= page and sect["end"] >= page:
                return(sect)
        return(None)
    def get_year(self, page):
        sect = Catalogue.get_section(page)
        try:
            ret = sect["year"]
        except:
            return(None)
        return(ret)
Catalogue.get_section = classmethod(Catalogue.get_section)
Catalogue.get_year = classmethod(Catalogue.get_year)

# Das Folgende generiert eine Auswertung im CSV-Format zu einer Liste mit Seitenzahlen aus dem Bücherradkatalog
# Die Seitenzahlen werden getrennt durch Zeilenumbruch in einer Datei unter path abgespeichert
class Evaluation:
    def __init__(self, path):
        file = open(path)
        self.data = [int(num.strip()) for num in file]
        self.counter = collections.Counter(self.data)
        self.pageData = []
        self.fields = []
        self.result = []
    def get_page_data(self):
        for num in self.counter:
            sect = Catalogue.get_section(num)
            self.pageData.append([str(num), str(self.counter[num]), sect["group"], sect["dateBegin"], str(sect["year"]), sect["writer"]])  
    def save(self, fileName):
        table = csvt.Table(self.fields, self.result)
        table.save(fileName)
        return(True)

# Auflistung nach Seiten
class EvaluationPage(Evaluation):
    def __init__(self, path):
        super().__init__(path)
        self.fields = ["Seite", "Frequenz", "Klasse", "Datum_ab", "Jahr", "Schreiber"]
        self.get_page_data()
        self.result = self.pageData

# Summarische Auflistung nach Jahren
class EvaluationYear(Evaluation):
    def __init__(self, path):
        super().__init__(path)
        self.fields = ["Jahr", "Seiten", "Einträge", "Klasse", "Datum_ab", "Schreiber"]
        self.get_page_data()
        groups = {}
        for row in self.pageData:
            try:
                groups[row[4]].append(row)
            except:
                groups[row[4]] = [row]
        for year in groups:
            self.result.append([str(year), ",".join([row[0] for row in groups[year]]), sum([int(row[1]) for row in groups[year]]), groups[year][0][2], groups[year][0][3], groups[year][0][5]])