#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re

# Quelle: https://provenienz.gbv.de/T-PRO_Thesaurus_der_Provenienzbegriffe

class Thesaurus:
    descriptors = {
        "Aufführungsexemplar" : "Exemplartypen",
        "Auktionsexemplar" : "Exemplartypen",
        "Aussonderungsexemplar" : "Exemplartypen",
        "Belegexemplar" : "Exemplartypen",
        "Bibliotheksexemplar" : "Exemplartypen",
        "Durchschossenes Exemplar" : "Exemplartypen",
        "Exemplar: Autor" : "Exemplartypen",
        "Exemplar: Autorin" : "Exemplartypen",
        "Exemplar: Donator" : "Exemplartypen",
        "Exemplar: Donatorin" : "Exemplartypen",
        "Exemplar: Widmungsempfänger" : "Exemplartypen",
        "Exemplar: Widmungsempfängerin" : "Exemplartypen",
        "Restitutionsexemplar" : "Exemplartypen",
        "Rezensionsexemplar" : "Exemplartypen",
        "Tauschexemplar" : "Exemplartypen",
        "Zensurexemplar" : "Exemplartypen",
        "Beutegut" : "Rechtlicher Status",
        "Bodenreform" : "Rechtlicher Status",
        "Enteignung" : "Rechtlicher Status",
        "Kolonialgut" : "Rechtlicher Status",
        "NS-Raubgut" : "Rechtlicher Status",
        "NS-Raubgut: Verdacht" : "Rechtlicher Status",
        "Restitution" : "Rechtlicher Status",
        "Säkularisationsgut" : "Rechtlicher Status",
        "Zensur" : "Rechtlicher Status",
        "Autogramm" : "Physische Merkmale",
        "Buchschnitt" : "Physische Merkmale",
        "Einband" : "Physische Merkmale",
        "Einlage" : "Physische Merkmale",
        "Einlage: Brief" : "Physische Merkmale",
        "Einlage: Fotografie" : "Physische Merkmale",
        "Einlage: Haar" : "Physische Merkmale",
        "Einlage: Lesezeichen" : "Physische Merkmale",
        "Einlage: Pflanze" : "Physische Merkmale",
        "Einlage: Zettel" : "Physische Merkmale",
        "Einlage: Zettel: Zeitungsausschnitt" : "Physische Merkmale",
        "Emblem" : "Physische Merkmale",
        "Etikett" : "Physische Merkmale",
        "Etikett: Buchbinder" : "Physische Merkmale",
        "Etikett: Buchbinderin" : "Physische Merkmale",
        "Etikett: Buchhändler" : "Physische Merkmale",
        "Etikett: Buchhändlerin" : "Physische Merkmale",
        "Exlibris" : "Physische Merkmale",
        "Extra-Ausstattung" : "Physische Merkmale",
        "Grafisches Zeichen" : "Physische Merkmale",
        "Handzeichnung" : "Physische Merkmale",
        "Initiale" : "Physische Merkmale",
        "Makulatur" : "Physische Merkmale",
        "Marginalie" : "Physische Merkmale",
        "Merkzeichen" : "Physische Merkmale",
        "Monogramm" : "Physische Merkmale",
        "Motto" : "Physische Merkmale",
        "Notiz" : "Physische Merkmale",
        "Genealogische Notiz" : "Physische Merkmale",
        "Nummer" : "Physische Merkmale",
        "Zugangsnummer" : "Physische Merkmale",
        "Porträt" : "Physische Merkmale",
        "Preis" : "Physische Merkmale",
        "Siegel" : "Physische Merkmale",
        "Signatur" : "Physische Merkmale",
        "Stempel" : "Physische Merkmale",
        "Dublettenstempel" : "Physische Merkmale",
        "Stempel: Buchbinder" : "Physische Merkmale",
        "Stempel: Buchbinderin" : "Physische Merkmale",
        "Stempel: Buchhändler" : "Physische Merkmale",
        "Stempel: Buchhändlerin" : "Physische Merkmale",
        "Tektur" : "Physische Merkmale",
        "Tilgung" : "Physische Merkmale",
        "Wappen" : "Physische Merkmale",
        "Widmung" : "Physische Merkmale",
        "Widmung: Autor" : "Physische Merkmale",
        "Widmung: Autorin" : "Physische Merkmale",
        "Datum" : "Zeitangaben",
        "Kaufdatum" : "Zeitangaben",
        "Lesedatum" : "Zeitangaben"
    }
    
def get_descriptors(type = None):
    if type == None:
        return(list([key for key, val in Thesaurus.descriptors.items()]))
    return(list([key for key, val in Thesaurus.descriptors.items() if val == type]))
def validate(descr):
    try:
        type = Thesaurus.descriptors[descr]
    except:
        return(False)
    return(True)
def get_type(descr):
    try:
       return(Thesaurus.descriptors[descr])
    except:
        return(None)