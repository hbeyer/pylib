#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

def get_prof_cat(url):
    conc = { "lips" : "Leipzig", "helmst" : "Helmstedt", "bamb" : "Bamberg" }
    for term, result in conc.items():
        if term in url:
            return(result)
    return("")

def get_faculty(text):
    text = text.lower()
    conc = { "med" : "Medizinische Fakultät",
             "phil" : "Philosophische Fakultät",
             "artist" : "Philosophische Fakultät",
             "jur" : "Juristische Fakultät",
             "theol" : "Theologische Fakultät",
             "recht" : "Juristische Fakultät"
             }
    for term, result in conc.items():
        if term in text:
            return(result)
    return("Offen")

def normalize_year(text):
    match = re.search(r"1[456789][0-9]{2}", text)
    try:
        return(match.group(0))
    except:
        return(None)

def abbr_title(title):
    title = title.replace(" || ", " ")
    pieces = title.split()
    new = " ".join(pieces[0:3])
    return(new)
        
def merge_period(start, end, new_start, new_end):
    start = int(start)
    end = int(end)
    new_start = int(new_start)
    new_end = int(new_end)
    if new_start < start:
        start = new_start
    if new_end > end:
        end = new_end
    return((start, end))
    
        
def get_subject(text):
    match = re.search(r"für (.+) an", text)
    try:
        return(match.group(1))
    except:
        return("")
		
def get_faculty_by_subject(text):
	conc = {
		"Alte Geschichte" : "Philosophische",
		"Anatomie" : "Medizinische",
		"Anatomie / Chirurgie" : "Medizinische",
		"Anatomie / Physiologie" : "Medizinische",
		"Anatomie / Physiologie / Pharmazie" : "Medizinische",
		"Aristotelismus" : "Philosophische",
		"Astronomie" : "Philosophische",
		"Astronomie / Geometrie" : "Philosophische",
		"Botanik" : "Medizinische",
		"Chemie" : "Medizinische",
		"Chemie / Anatomie / Pharmazie" : "Medizinische",
		"Chemie / Pharmazie / Bergbau" : "Medizinische",
		"Chirurgie" : "Medizinische",
		"Codex" : "Juristische",
		"Codex / Lehnsrecht" : "Juristische",
		"Codex des Justinian" : "Juristische",
		"Dialektik" : "Philosophische",
		"Dialektik / Ethik" : "Philosophische",
		"Dogmatik / Moral" : "Theologische",
		"Eloquenz" : "Philosophische",
		"Eloquenz / Latein" : "Philosophische",
		"Eloquenz / Poesie" : "Philosophische",
		"Englisch" : "Philosophische",
		"Ethik" : "Philosophische",
		"Ethik / Dialektik" : "Philosophische",
		"Ethik / Politik" : "Philosophische",
		"Französisch" : "Philosophische",
		"Geburtshilfe" : "Medizinische",
		"Geschichte" : "Philosophische",
		"Geschichte / Poesie" : "Philosophische",
		"Geschichte / Statistik" : "Philosophische",
		"Griechisch" : "Philosophische",
		"Griechisch / Hebräisch" : "Philosophische",
		"Griechisch / Latein" : "Philosophische",
		"Griechisch / Latein / Poesie" : "Philosophische",
		"Griechisch / orientalische Sprachen" : "Philosophische",
		"Griechisch / Poesie" : "Philosophische",
		"Griechsch" : "Philosophische",
		"Griechsisch" : "Philosophische",
		"Hebräisch" : "Philosophische",
		"höhere Mathematik" : "Philosophische",
		"Inquisitionsprozesse / Forensik" : "Juristische",
		"Institutionen" : "Juristische",
		"Institutiones" : "Juristische",
		"Institutiones / Criminalia" : "Juristische",
		"Institutiones / Lehnrecht / jur. Encycolpädie" : "Juristische",
		"Institutiones / Pandekten" : "Juristische",
		"Italienisch" : "Philosophische",
		"Italienisch / Englisch" : "Philosophische",
		"Jurisprudenz" : "Juristische",
		"Kameralistik / Policey-Wissenschaften" : "Juristische",
		"kanonisches- / Feudalrecht" : "Juristische",
		"kanonisches Recht" : "Juristische",
		"Kirchen- / Lehnsrecht" : "Juristische",
		"Kirchengeschichte" : "Theologische",
		"Konstitution / Pandekten" : "Juristische",
		"Kontroverstheologie" : "Theologische",
		"Landwirtschaft / Tierheilkunde" : "Philosophische",
		"Latein" : "Philosophische",
		"Latein / Geburtshilfe / Botanik" : "Medizinische",
		"Literaturgeschichte" : "Philosophische",
		"Logik" : "Philosophische",
		"Logik / Ethik" : "Philosophische",
		"Logik / Ethik / Politik / Geschichte" : "Philosophische",
		"Logik / Metaphysik" : "Philosophische",
		"Mathematik" : "Philosophische",
		"Mathematik / Baukunst / Trigonometrie" : "Philosophische",
		"Mathematik / Philosophie" : "Philosophische",
		"Mathematik / Physik" : "Philosophische",
		"Medizin / Chemie" : "Medizinische",
		"Medizin / Physik" : "Medizinische",
		"Medizin /Chemie" : "Medizinische",
		"Metaphysik" : "Philosophische",
		"Metaphysik / Natur- Völkerrecht / Sittenlehre" : "Philosophische",
		"Metaphysik / Physik" : "Philosophische",
		"Moral" : "Philosophische",
		"Moral / Ethik" : "Philosophische",
		"morgenländische Sprachen" : "Philosophische",
		"Natur- / Völkerrecht" : "Juristische",
		"Naturphilosophie / Rhetorik" : "Philosophische",
		"niedere Mathematik" : "Philosophische",
		"nstitutiones / Kirchenrecht / Pandekten" : "Juristische",
		"Institutiones / Kirchenrecht / Pandekten" : "Juristische",
		"orientalische Sprachen" : "Philosophische",
		"Pandekten" : "Juristische",
		"Pathologie" : "Medizinische",
		"Pathologie / Botanik" : "Medizinische",
		"Pathologie / med. Semiotik" : "Medizinische",
		"Philosophie" : "Philosophische",
		"Philosophie (Historia Literaria)" : "Philosophische",
		"Phyik" : "Philosophische",
		"Physik" : "Philosophische",
		"Physik / Anatomie" : "Medizinische",
		"Physik / Anatomie / Mathematik" : "Medizinische",
		"Physik / Physiologie" : "Medizinische",
		"Physiologie" : "Medizinische",
		"Poesie" : "Philosophische",
		"Politik" : "Philosophische",
		"Politik / Geschichte" : "Philosophische",
		"praktische Medizin" : "Medizinische",
		"Privat- / Lehns- / Staatsrecht" : "Juristische",
		"Privatrecht / europ. Völkerrecht" : "Juristische",
		"Rechte" : "Juristische",
		"Rechts- / Kameralwissenschaften" : "Juristische",
		"Rechtswissenschaft" : "Juristische",
		"röm. Recht / Lehnrecht" : "Juristische",
		"röm. Recht / Staatsrecht / Naturrecht" : "Juristische",
		"römisches Recht" : "Juristische",
		"Staatsrecht" : "Juristische",
		"Strafrecht / Privatrecht / westfälsicher Zivilprozess" : "Juristische",
		"theoretische Medizin" : "Medizinische"
	}
	try:
		return(conc[text] + " Fakultät")
	except:
		return("Offen")