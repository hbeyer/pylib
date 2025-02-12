#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Subject:
    # Quelle: ZfBB 65 (2018), S. 337
    # https://www.bibliotheksstatistik.de/konkordanz?art=bix&jahr=2018&fb=WB#haupt198
    conc = [
        { "sdd" : "01", "name" : "Allgemeines", "dbs" : "01", "name-dbs" : "Allgemeines"},
        {"sdd" : "02", "name" : "Philosophie", "dbs" : "02", "name-dbs" : "Philosophie"},
        {"sdd" : "03", "name" : "Psychologie", "dbs" : "03", "name-dbs" : "Psychologie"},
        {"sdd" : "04", "name" : "Theologie", "dbs" : "04", "name-dbs" : "Religion und Theologie"},
        {"sdd" : "05", "name" : "Erziehung, Bildung", "dbs" : "05", "name-dbs" : "Erziehung, Bildung, Unterricht"},        
        {"sdd" : "06", "name" : "Soziologie", "dbs" : "06", "name-dbs" : "Soziologie, Gesellschaft, Statistik"},        
        {"sdd" : "07", "name" : "Politik, Verwaltung", "dbs" : "07", "name-dbs" : "Politik, Öffentliche Verwaltung, Militär"},        
        {"sdd" : "08", "name" : "Wirtschaft", "dbs" : "08", "name-dbs" : "Wirtschaft, Arbeit, Tourismusindustrie"},        
        {"sdd" : "09", "name" : "Recht", "dbs" : "09", "name-dbs" : "Recht"},        
        {"sdd" : "10", "name" : "Allgemeine Naturwissenschaft", "dbs" : "10", "name-dbs" : "Natur, Naturwissenschaft allgemein"},        
        {"sdd" : "11", "name" : "Mathematik", "dbs" : "11", "name-dbs" : "Mathematik"},        
        {"sdd" : "", "name" : "", "dbs" : "12", "name-dbs" : "Informatik, Kybernetik"},        
        {"sdd" : "13", "name" : "Physik, Astronomie", "dbs" : "13", "name-dbs" : "Physik, Astronomie"},
        {"sdd" : "14", "name" : "Chemie, Alchemie", "dbs" : "14", "name-dbs" : "Chemie"},        
        {"sdd" : "15", "name" : "Geowissenschaften, Bergbau", "dbs" : "15", "name-dbs" : "Geowissenschaften, Bergbau"},
        {"sdd" : "16", "name" : "Biologie", "dbs" : "16", "name-dbs" : "Biologie"},        
        {"sdd" : "17", "name" : "Medizin, Tiermedizin", "dbs" : "17", "name-dbs" : "Medizin, Veterinärmedizin"},        
        {"sdd" : "18", "name" : "Technik", "dbs" : "18", "name-dbs" : "Technik, Grundlagen"},        
        {"sdd" : "", "name" : "", "dbs" : "19", "name-dbs" : "Maschinenbau inkl. Werkstoffwiss., Fertigungstechnik, Technik der Verkehrsmittel, Mikrotechnik, Verfahrenstechnik"},        
        {"sdd" : "", "name" : "", "dbs" : "20", "name-dbs" : "Elektrotechnik inkl. Elektronik, Kommunikationstechnik, Energietechnik"},        
        {"sdd" : "", "name" : "", "dbs" : "21", "name-dbs" : "Bauingenieurwesen, Bergbautechnik"},        
        {"sdd" : "22", "name" : "Land- und Hauswirtschaft", "dbs" : "22", "name-dbs" : "Agrar- und Forstwissenschaft, Haushalts- und Ernährungswiss., Lebensmitteltechnologie"},        
        {"sdd" : "", "name" : "", "dbs" : "23", "name-dbs" : "Umweltschutz, Raumordnung, Landschaftsgestaltung"},        
        {"sdd" : "24", "name" : "Architektur, Bildende Kunst", "dbs" : "24", "name-dbs" : "Architektur, Bildende Kunst, Photographie"},        
        {"sdd" : "25", "name" : "Musik, Theater", "dbs" : "25", "name-dbs" : "Musik, Theater, Tanz, Film"},        
        {"sdd" : "26", "name" : "Sport, Spiele, Festkultur", "dbs" : "26", "name-dbs" : "Sport"},        
        {"sdd" : "27", "name" : "Allgemeine Sprach- und Literaturwissenschaft", "dbs" : "27", "name-dbs" : "Allgemeine und Vergleichende Sprach- und Literaturwissenschaft"},        
        {"sdd" : "28", "name" : "Englische Sprach- und Literaturwissenschaft", "dbs" : "28", "name-dbs" : "Englische Sprach- und Literaturwissenschaft"},        
        {"sdd" : "29", "name" : "Deutsche Sprach- und Literaturwissenschaft", "dbs" : "29", "name-dbs" : "Deutsche Sprach- und Literaturwissenschaft"},        
        {"sdd" : "30", "name" : "Romanische Sprach- und Literaturwissenschaft", "dbs" : "30", "name-dbs" : "Romanische Sprach- und Literaturwissenschaft"},        
        {"sdd" : "31", "name" : "Klassische Sprach- und Literaturwissenschaft", "dbs" : "31", "name-dbs" : "Klassische Sprach- und Literaturwissenschaft"},        
        {"sdd" : "32", "name" : "Slawische und baltische Sprach- und Literaturwissenschaft", "dbs" : "31", "name-dbs" : "Slawische und baltische Sprach- und Literaturwissenschaft"},      
        {"sdd" : "33", "name" : "Sonstige Sprachen und Literaturen", "dbs" : "33", "name-dbs" : "Sprach- und Literaturwissenschaft sonstiger Sprachen"},         
        {"sdd" : "34", "name" : "Archäologie, Geschichte", "dbs" : "34", "name-dbs" : "Archäologie, Geschichte, einschl. Sozial- und Wirtschaftsgeschichte"},        
        {"sdd" : "35", "name" : "Geographie, Volkskunde", "dbs" : "35", "name-dbs" : "Geographie, Heimat- und Länderkunde, Reisen, Atlanten, Volks- und Völkerkunde"}
        ]
def get_sys():
    ret = {}
    for row in Subject.conc:
        if row["sdd"] == "":
            continue
        ret[row["sdd"]] = row["name"]
    return(ret)

def get_sys_dbs():
    ret = {}
    for row in Subject.conc:
        if row["dbs"] == "":
            continue
        ret[row["dbs"]] = row["name-dbs"]
    return(ret)
    
def get_label(num):
    if isinstance(num, str):
        if len(num) == 1:
            num = num.zfill(2)
    elif isinstance(num, int):
        num = str(num).zfill(2)
    for row in Subject.conc:
        if row["sdd"] == num:
            return(row["name"])
    return(None)
    
def get_label_dbs(num):
    if isinstance(num, str):
        if len(num) == 1:
            num = num.zfill(2)
    elif isinstance(num, int):
        num = str(num).zfill(2)
    for row in Subject.conc:
        if row["dbs"] == num:
            return(row["name"])
    return(None)