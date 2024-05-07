#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as et
import csv
import logging
import time
from lib import gnd
from lib import sru
from lib import xmlreader as xr
from lib import xmlserializer as xs
from lib import pica                   
class ArtCollection:
    def __init__(self, db):
        self.content = []
        self.db = db
    def __iter__(self):
        self.a = 0
        return(self)
    def __next__(self):
        if self.a < len(self.content):
            ret = self.content[self.a]
            self.a += 1
            return(ret)
        else:
            raise StopIteration
    def addWork(self, work):
        if isinstance(work, Artwork):
            self.content.append(work)
        return(1)
    def loadBySQL(self, sqlArtwork):
        cursor = self.db.cursor(dictionary=True, buffered=True)
        cursorPers = self.db.cursor(dictionary=True, buffered=True)
        cursor.execute(sqlArtwork)
        for row in cursor:
            artwork = Artwork()
            artwork.importRow(row)
            cursorPers.execute("SELECT * FROM person_representation RIGHT JOIN person ON person_representation.person_id = person.id WHERE person_representation.artwork_id = " + str(artwork.id))
            for rowPers in cursorPers:
                artwork.importPerson(rowPers)
            self.addWork(artwork)
        return(1)
    def load(self, limit=100, offset=1):
        sql = "SELECT * FROM artwork LIMIT " + str(limit) + " OFFSET " + str(offset)
        self.loadBySQL(sql)
        return(1)
    def loadByANumber(self, anumber, omitLetter = False):
        if omitLetter == False:
            self.loadBySQL(f"SELECT * FROM artwork WHERE anumber LIKE \"{anumber}\"")
            return(True)
        self.loadBySQL(f"SELECT * FROM artwork WHERE anumber LIKE \"A {anumber}\"")
        return(True)
class Serializer:
    def __init__(self, collection):
        self.collection = collection
        self.ser = ""
    def save(self, fileName):
        file = open(fileName, "w", encoding="utf-8")
        file.write(self.ser)
        file.close()

class SerializerXML(Serializer):
    def __init__(self, collection):
        super().__init__(collection)
        pass
    def serialize(self, fileName):
        root = et.fromstring('<ArtCollection></ArtCollection>')
        for artwork in self.collection.content:
            artwork.description = artwork.descriptionClean
            artworkEl = et.SubElement(root, 'artwork')
            for field in artwork.flatFields:
                if field in ['id', 'anumber', 'invNo']:
                    artworkEl.set(field, str(getattr(artwork, field)))
                else:
                    if getattr(artwork, field):
                        subelement = et.SubElement(artworkEl, field)
                        subelement.text = str(getattr(artwork, field))
                        if field in ['sheetsize', 'platesize', 'imagesize']:
                            dimensions = getattr(artwork, field + "Sep")
                            if dimensions != None:
                                subelement.set("height", dimensions["height"])
                                subelement.set("width", dimensions["width"])
            for artist in artwork.artists:
                artistEl = et.SubElement(artworkEl, 'artist')
                for field in artist.flatFields:
                    if getattr(artist, field):
                        subelement = et.SubElement(artistEl, field)
                        subelement.text = str(getattr(artist, field))
            for publisher in artwork.publishers:
                publisherEl = et.SubElement(artworkEl, 'publisher')                    
                for field in publisher.flatFields:
                    if getattr(publisher, field):
                        subelement = et.SubElement(publisherEl, field)
                        subelement.text = str(getattr(publisher, field))
            for person in artwork.personsRepr:
                personEl = et.SubElement(artworkEl, 'personRepr')
                for field in person.flatFields:
                    if field in ['id', 'gnd'] and getattr(person, field):
                        personEl.set(field, str(getattr(person, field)))
                    else:
                        if getattr(person, field):
                            subelement = et.SubElement(personEl, field)
                            subelement.text = str(getattr(person, field))                    
                for attr in person.attributes:
                    persAttrEl = et.SubElement(personEl, 'attribute')
                    persAttrEl.text = attr.value
                    persAttrEl.set("type", attr.type)
                    for rel in attr.related:
                        relatedEl = et.SubElement(persAttrEl, 'related')
                        relatedEl.text = rel
                    for see in attr.seealso:
                        seeEl = et.SubElement(persAttrEl, 'seealso')
                        seeEl.text = see
            for attribute in artwork.attributes:
                attrEl = et.SubElement(artworkEl, 'attribute')
                attrEl.text = attribute.value
                attrEl.set("type", attribute.type)
                for rel in attribute.related:
                    relatedEl = et.SubElement(attrEl, 'related')
                    relatedEl.text = rel
                for see in attribute.seealso:
                    seeEl = et.SubElement(attrEl, 'seealso')
                    seeEl.text = see
        self.ser = et.tostring(root, encoding="unicode")
        self.save(fileName + ".xml")

class SerializerCSV(Serializer):
    def __init__(self, collection):
        super().__init__(collection)
        self.artworkFields = ['id', 'anumber', 'url', 'urlImage', 'invNo', 'sheetsize', 'platesize', 'imagesize', 'technique', 'notes', 'descriptionClean', 'catalogs', 'condition', 'source', 'shelfmarkSource']
        self.numberPersons = 4
        self.personFields = ['name', 'yearStart', 'yearEnd', 'dateBirth', 'placeBirth', 'dateDeath', 'placeDeath']
        self.numberArtists = 3
        self.artistFields = ['name', 'role', 'lifetime', 'description']
        self.numberPublishers = 2
        self.publisherFields = ['name', 'place', 'time', 'placetime']
        self.artworkAttributes = True
    def serialize(self, fileName):
        with open(fileName + ".csv", 'w', encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            metaRow = []
            metaRow.extend(self.artworkFields)
            if self.artworkAttributes == True:
                metaRow.append('attributes')
            for i in range(0, self.numberPersons):
                for prop in self.personFields:
                    metaRow.append(prop + "-person" + str(i))
                metaRow.append("attributes-person" + str(i))
            for i in range(0, self.numberArtists):
                for prop in self.artistFields:
                    metaRow.append(prop + "-artist" + str(i))
            for i in range(0, self.numberPublishers):
                for prop in self.publisherFields:
                    metaRow.append(prop + "-publisher" + str(i))    
            writer.writerow(metaRow)
            for artwork in self.collection.content:
                row = []
                for field in self.artworkFields:
                    row.append(getattr(artwork, field))
                if self.artworkAttributes == True:
                    row.append(artwork.makeAttributeString())
                for i in range(0, self.numberPersons):
                    for f in self.personFields:
                        try:
                            row.append(getattr(artwork.personsRepr[i], f))
                        except:
                            row.append("")
                    try:
                        row.append(artwork.personsRepr[i].makeAttributeString())
                    except:
                        row.append("")
                for i in range(0, self.numberArtists):
                    for f in self.artistFields:
                        try:
                            row.append(getattr(artwork.artists[i], f))
                        except:
                            row.append("")                
                for i in range(0, self.numberPublishers):
                    for f in self.publisherFields:
                        try:
                            row.append(getattr(artwork.publishers[i], f))
                        except:
                            row.append("")
                writer.writerow(row)

class SerializerSel(SerializerCSV):
    def __init__(self, collection):
        super().__init__(collection)
        controllCollection = ArtCollection(self.collection.db)
        for item in self.collection:
            item.fillDerivatedFields(controllCollection)
        self.artworkFields = ['id', 'anumber', 'keywords_technique', 'yearNormalized', 'sourceYear', 'portraitType', 'orientation', 'likeA', 'descriptionClean', 'technique', 'source', 'transcription']
        self.numberPersons = 0
        self.numberArtists = 0
        self.numberPublishers = 0
        self.artworkAttributes = False

class Artwork:    
    def __init__(self):
        self.flatFields = ['id', 'anumber', 'url', 'urlImage', 'invNo', 'sheetsize', 'platesize', 'imagesize', 'technique', 'notes', 'description', 'transcription', 'catalogs', 'condition', 'source', 'shelfmarkSource', 'instime', 'modtime']
        self.id = None
        self.anumber = None
        self.url = ""
        self.urlImage = ""
        self.invNo = ""
        self.path_wdb = ""
        self.artists = []
        self.artistsXML = ""
        self.publishers = []
        self.sheetsize = ""
        self.sheetsizeSep = ""
        self.platesize = ""
        self.platesizeSep = ""
        self.imagesize = ""
        self.imagesizeSep = ""
        self.technique = ""
        self.notes = ""
        self.description = ""
        self.descriptionClean = ""
        self.quotation = ""
        self.catalogs = ""
        self.condition = ""
        self.source = ""
        self.epn = None
        self.shelfmarkSource = ""
        self.instime = None
        self.modtime = None
        self.personsRepr = []
        self.attributes = []
        self.attribute_string = ""
        self.likeA = ""
        self.yearNormalized = ""
        self.sourceYear = ""
        self.keywords_technique = ""
        self.transcription = ""
        self.portraitType = ""
        self.orientation = ""
    def __str__(self):
        ret = "Artwork Nr. " + str(self.id) + ", " + str(self.anumber) + ", URL: " + self.url + ", Image: " + self.urlImage
        if len(self.attributes) == 1:
            ret = ret + ", 1 Attribut"
        elif len(self.attributes) > 1:
            ret = ret + ", " + str(len(self.attributes)) + " Attribute"
        return(ret)
    def __iter__(self):
        self.iterFields = ['id', 'anumber', 'url', 'urlImage', 'invNo', 'sheetsize', 'platesize', 'imagesize', 'technique', 'notes', 'description', 'transcription', 'catalogs', 'condition', 'source', 'shelfmarkSource', 'instime', 'modtime']
        return(self)
    def __next__(self):
        try:
            field = self.iterFields.pop(0)
        except:
            raise StopIteration
        else:            
            return({field : getattr(self, field)})            
    def importRow(self, row):
        self.id = row["id"]
        self.anumber = row["anumber"]
        self.invNo = row["inventorynumber"]
        self.path_wdb = row["path_wdb"]
        self.sheetsize = removeLinebreaks(row["sheetsize"])
        self.sheetsizeSep = separateSize(self.sheetsize)
        self.platesize = removeLinebreaks(row["platesize"])
        self.platesizeSep = separateSize(self.platesize)        
        self.imagesize = removeLinebreaks(row["imagesize"])
        self.imagesizeSep = separateSize(self.imagesize)
        self.technique = row["technique"]
        self.notes = removeLinebreaks(row["notes"])
        self.description = row["description"]
        self.transcription = extractQuo(self.description)
        self.descriptionClean = cleanDescription(self.description)
        self.catalogs = removeLinebreaks(row["catalogs"], ", ")
        self.condition = row["condition_artwork"]
        self.source = removeLinebreaks(row["source"])
        self.attribute_string = row["attributes"]
        self.importAttributesFromString()
        self.shelfmarkSource = extractShelfmark(self.source)
        self.instime = row["instime"]
        self.modtime = row["modtime"]
        self.url = "http://portraits.hab.de/werk/" + str(self.id) + "/"
        self.urlImage = "http://diglib.hab.de/varia/portrait/a-" + self.anumber.zfill(5) + "/origsize/000001.jpg"
        self.importArtists(row["artists"])
        self.importPublishers(row["publishers"])
        return(1)
    def importArtists(self, artistsXML):
        artists = XMLReader.readElement(artistsXML, "artist")
        if artists == 0:
            return(0)
        for artist in artists:
            if artist["name"] == None:
                continue            
            artistObj = Artist()
            for x in artist:
                setattr(artistObj, x, artist[x])
            self.artists.append(artistObj)
        return(1)
    def importPublishers(self, publishersXML):
        publishers = XMLReader.readElement(publishersXML, "publisher")
        if publishers == 0:
            return(0)
        for publisher in publishers:
            if publisher["name"] == None:
                continue            
            publisherObj = Publisher()
            for x in publisher:
                setattr(publisherObj, x, publisher[x])
            self.publishers.append(publisherObj)
        return(1)        
    def importPerson(self, row):
        personObj = Person(row)
        personObj.id = row["id"]
        personObj.gnd = row["gndid"]
        personObj.name = row["name"]
        personObj.aliases = removeLinebreaks(row["aliases"], "; ")
        personObj.nationality = row["nationality"]
        personObj.yearStart = row["startyear"]
        personObj.yearEnd = row["endyear"]
        personObj.biography = row["biography"]
        personObj.literature = removeLinebreaks(row["literature"])
        personObj.instime = row["instime"]
        personObj.modtime = row["instime"]
        personObj.attribute_string = row["attributes"]
        personObj.attributes = self.importAttributesFromString()
        bornData = XMLReader.readElement(row["lifetime"], "born")
        try:
            bornData[0]["date"]
        except:
            pass
        else:
            personObj.dateBirth = bornData[0]["date"]
        try:
            bornData[0]["place"]
        except:
            pass
        else:
            personObj.placeBirth = bornData[0]["place"]
        bornData = None            
        diedData = XMLReader.readElement(row["lifetime"], "died")
        try:
            diedData[0]["date"]
        except:
            pass
        else:
            personObj.dateDeath = diedData[0]["date"]
        try:
            diedData[0]["place"]
        except:
            pass
        else:
            personObj.placeDeath = diedData[0]["place"]
        self.personsRepr.append(personObj)
        return(1)
    def importAttributesFromString(self):
        pieces = self.attribute_string.split("|")
        for piece in pieces:
            subpieces = piece.split("_")
            try:
                attr = Attribute(subpieces[0], subpieces[1])
            except:
                attr = Attribute(subpieces[0], "")
            self.attributes.append(attr)
    def makeAttributeString(self, sep="/"):
        attr = [attr.value for attr in self.attributes]
        return(sep.join(attr))
    def getArtistsXML(self):
        return(self.artistsXML);
    def getPublishersXML(self):
        return("");
    def getNormalizedYear(self):
        for pub in self.publishers:
            if pub.getYear() != None:
                return(pub.getYear())
        return(None)
    def extractTechnique(self):
        tech = self.technique
        match = re.findall(r"Kupferstich|Radierung|Schabkunst|Lithographie|Farblithographie|Holzschnitt|Stahlstich|Holzstich|Roulettestich|Umrißkupfer|Umrisskupfer|Punktierstich|Punzstich|Aquatinta|Silhouettenstich|Umrissradierung|Silhouettendruck|Silhouettenzeichnung|Photogr|Farbtuschzeichnung|Tuschzeichnung|Kreidezeichnung|Farbzeichnung|Farbezeichnung|Federzeichnung|Zeichnung|Crayonmanier|Scherenschnitt|in Braun[ d]|koloriert", tech)
        ret = []
        conc = {"Farbezeichnung":"Farbzeichnung", "Photogr":"Fotografie", "Umrißkupfer":"Umrisskupfer", "in Braun ":"Braundruck", "in Braund":"Braundruck"}
        for el in match:
            try:
                ret.append(conc[el])
            except:
                ret.append(el)
        ret.sort()
        ret = set(ret)
        try:
            return("/".join(ret))
        except:
            return(None)
    def getPortraitType(self):
        descr = self.descriptionClean
        match = re.search(r"Büste|Brustb|Hüftb|Halbf|Kopfb|[gG]anzer? Fig|Kniest|Silhouette Kopf|Kopfsilhouette", descr)
        conc = {"Brustb" : "Brustbild", "Hüftb" : "Hüftbild", "Halbf" : "Halbfigur", "Kopfb" : "Kopfbild", "ganzer Fig" : "ganze Figur", "ganze Fig" : "ganze Figur", "Ganze Fig" : "ganze Figur", "Kniest" : "Kniestück", "Silhouette Kopf" : "Kopfsilhouette"}
        try:
            ret = match.group(0)
        except:
            return(None)
        else:
            try:
                ret = conc[ret]
            except:
                pass
            return(ret)
    def getOrientation(self):
        descr = self.descriptionClean
        match = re.search(r"((leicht )?nach (r\.|l\.|hr\.|hl\.)|von vorn)", descr)
        try:
            return(match.group(0))
        except:
            return(None)            
    def getLikeA(self):
        descr = self.descriptionClean
        match = re.search(r" A ([0-9]+)", descr)
        try:
            return(match.group(1))
        except:
            return(None)
    def fillDerivatedFields(self, controllCollection):
        self.keywords_technique = self.extractTechnique()
        self.sourceYear = None
        self.yearNormalized = self.getNormalizedYear()
        if self.yearNormalized != None:
            self.sourceYear = "publisher"
        else:
            self.yearNormalized = extractYearPrecisely(self.technique)
            if self.yearNormalized != None:
                self.sourceYear = "technique"
            else:
                self.yearNormalized = extractYearPrecisely(self.source)
                if self.yearNormalized != None:
                    self.sourceYear = "source"
        self.portraitType = self.getPortraitType()
        self.orientation = self.getOrientation()
        self.likeA = self.getLikeA()
        if self.likeA != None:
            controllCollection.content = []
            controllCollection.loadByANumber(self.likeA)
            try:
                model = controllCollection.content[0]
            except:
                pass
            else:
                if self.keywords_technique == "" or self.keywords_technique == None:
                    self.keywords_technique = model.extractTechnique()
                if self.yearNormalized == "" or self.yearNormalized == None:
                    self.yearNormalized = model.getNormalizedYear()
                    if self.yearNormalized != None:
                        self.sourceYear = "publisherA"
                    else:
                        self.yearNormalized = extractYearPrecisely(model.technique)
                        if self.yearNormalized != None:
                            self.sourceYear = "techniqueA"
                        else:
                            self.yearNormalized = extractYearPrecisely(model.source)
                            if self.yearNormalized != None:
                                self.sourceYear = "sourceA"
                if self.portraitType == "" or self.portraitType == None:
                    self.portraitType = model.getPortraitType()
                if self.orientation == "" or self.orientation == None:
                    self.orientation = model.getOrientation()    
    def make_source(self):
        if self.epn == None:
            return(None)
        req = sru.Request_HAB()
        num = req.prepare(f"pica.epn={self.epn}")
        if num != 1:
            logging.error(f"Keine Titelaufnahme zu EPN {self.epn}")
            return(None)
        reader = xr.WebReader(req.url, "record", "http://docs.oasis-open.org/ns/search-ws/sruResponse")
        for node in reader:
            rec = pica.Record(node)
            break
        sm = rec.get_sm(self.epn)
        cit = rec.make_citation()
        self.source = f"Aus: {cit} [HAB: {sm}]"
    def makeTuple(self):       
        val = (self.anumber, make_sortable(self.anumber), prepare_string(self.invNo), prepare_string(self.path_wdb), self.getArtistsXML(), self.getPublishersXML(), prepare_string(self.sheetsize), prepare_string(self.platesize), prepare_string(self.imagesize), prepare_string(self.technique), prepare_string(self.notes), prepare_string(self.description), prepare_string(self.catalogs), prepare_string(self.condition), prepare_string(self.source), int(time.time()), int(time.time()), prepare_string(self.likeA), prepare_string(self.yearNormalized), prepare_string(self.sourceYear), prepare_string(self.keywords_technique), prepare_string(self.descriptionClean), prepare_string(self.transcription), prepare_string(self.portraitType), prepare_string(self.orientation), self.attribute_string)
        return(val)
    def insertIntoDB(self, db):
        self.fillDerivatedFields(ArtCollection(db))
        if self.anumber == "":
            logging.error("Keine A- oder B-Nummer übergeben")
            return(False)
        contrColl = ArtCollection(db)
        contrColl.loadByANumber(self.anumber, False)
        if len(contrColl.content) > 0:
            logging.error(f"ID {self.anumber} bereits vorhanden")
            return(False)
        cursor = db.cursor()
        sql = "INSERT INTO `artwork`(`anumber`, `sort`, `inventorynumber`, `path_wdb`, `artists`, `publishers`, `sheetsize`, `platesize`, `imagesize`, `technique`, `notes`, `description`, `catalogs`, `condition_artwork`, `source`, `instime`, `modtime`, `like_a`, `year_normalized`, `source_year`, `keywords_technique`, `description_clean`, `transcription`, `portrait_type`, `orientation`, `attributes`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = self.makeTuple()
        cursor.execute(sql, val)
        db.commit()
        if cursor.rowcount != 1:
            logging.error(f"Fehler: {cursor.rowcount} Zeilen in Tabelle artwork geschrieben")
            return(False)
        logging.info(f"{cursor.rowcount} Zeilen in Tabelle artwork geschrieben. Letzte ID: {cursor.lastrowid}")
        id_artwork = cursor.lastrowid
        for pers in self.personsRepr:
            id_person = pers.insertIfNew(db)
            sql_rel = "INSERT INTO `person_representation`(`artwork_id`, `person_id`, `location`) VALUES (%s, %s, %s)"
            val = (id_artwork, id_person, '')
            cursor.execute(sql_rel, val)
            db.commit()
            logging.info(f"{cursor.rowcount} Zeilen in Tabelle person_representation geschrieben. Letzte ID: {cursor.lastrowid}")
        return(id_artwork)
    def updateInDB(self, db):
        pass
    def deleteFromDB(self, db):
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM person_representation WHERE artwork_id LIKE {self.id}")
        db.commit()
        logging.info(f"{cursor.rowcount} Zeilen aus Tabelle person_representation gelöscht")
        cursor.execute(f"DELETE FROM artwork WHERE id LIKE {self.id}")
        db.commit()
        logging.info(f"{cursor.rowcount} Zeilen aus Tabelle artwork gelöscht")
        return(True)

class Person:
    def __init__(self, name = ""):
        self.flatFields = ['id', 'gnd', 'name', 'aliases', 'nationality', 'yearStart', 'yearEnd', 'biography', 'literature', 'instime', 'modtime', 'dateBirth', 'dateDeath', 'placeBirth', 'placeDeath']
        self.id = None
        self.gnd = None
        self.name = name
        self.aliases = ""
        self.nationality = ""
        self.yearStart = None
        self.yearEnd = None
        self.lifetime = ""
        self.biography = ""
        self.literature = ""
        self.deprecated = 0
        self.notes = ""
        self.instime = None
        self.modtime = None
        self.dateBirth = ""
        self.placeBirth = ""
        self.dateDeath = ""
        self.placeDeath = ""
        self.attributes = []
        self.attribute_string = ""
    def __str__(self):
        if self.name == "":
            self.name = "Person"
        ret = self.name
        if self.id != None:
            ret = ret + ", ID " + str(self.id)
        if self.gnd != None:
            ret = ret + ", GND " +  self.gnd
        return(ret)    
    def __iter__(self):
        self.iterFields = self.flatFields
        return(self)
    def __next__(self):
        try:
            field = self.iterFields.pop(0)
        except:
            raise StopIteration
        else:            
            return({field : getattr(self, field)})
    def harvestFromGND(self, cache):
        gnd_obj = gnd.ID(self.gnd)
        if gnd_obj.valid != True:
            return(False)
        data = gnd_obj.get_info(cache)
        if self.name == "":
            try:
                self.name = data["preferredName"]
            except:
                pass
        try:
            self.dateBirth = data["dateOfBirth"]
        except:
            pass
        self.yearStart = extractYear(self.dateBirth)
        try:
            self.dateDeath = data["dateOfDeath"]
        except:
            pass            
        self.yearEnd = extractYear(self.dateDeath)        
        try:
            self.biography = data["biographicalOrHistoricalInformation"]
        except:
            pass
        if self.biography == "":
            try:
                self.biography = data["professions"]
            except:
                pass
        try:
            self.placeBirth = data["placeOfBirth"]
        except:
            pass
        try:
            self.placeDeath = data["placeOfDeath"]
        except:
            pass
        try:
            self.aliases = data["variantNames"]
        except:
            pass
        if self.lifetime == "":
            self.lifetime = self.make_lifetime()
        return(True)
    def make_lifetime(self):
        if self.dateBirth == "" and self.placeBirth == "" and self.dateDeath == "" and self.placeDeath == "":
            return("")
        ser = xs.Serializer("_lifetime", "lifetime")
        if self.dateBirth != "" or self.placeBirth != "":
            node_born = xs.make_node("born")
            if self.dateBirth != "":
                node_born_date = xs.make_node("date", self.dateBirth)
                node_born_type = xs.make_node("type", "eq")
                xs.add_subnode(node_born, node_born_date)
                xs.add_subnode(node_born, node_born_type)
            if self.placeBirth != "":
                node_born_place = xs.make_node("place", self.placeBirth)
                xs.add_subnode(node_born, node_born_place)
            ser.add_node(node_born)
        if self.dateDeath != "" or self.placeDeath != "":
            node_died = xs.make_node("died")
            if self.dateDeath != "":
                node_died_date = xs.make_node("date", self.dateDeath)
                node_died_type = xs.make_node("type", "eq")
                xs.add_subnode(node_died, node_died_date)
                xs.add_subnode(node_died, node_died_type)
            if self.placeDeath != "":
                node_died_place = xs.make_node("place", self.placeDeath)
                xs.add_subnode(node_died, node_died_place)
            ser.add_node(node_died)
        xml = ser.to_string()
        return(xml)
    def importAttributesFromString(self):
        pieces = self.attribute_string.split("|")
        for piece in pieces:
            subpieces = piece.split("_")
            try:
                attr = Attribute(subpieces[0], subpieces[1])
            except:
                attr = Attribute(subpieces[0], "")
            self.attributes.append(attr)
    def makeAttributeString(self, sep="/"):
        attr = [attr.value for attr in self.attributes]
        return(sep.join(attr))
    def getYear(self):
        if self.yearEnd != None:
            return(self.yearEnd)
        if self.dateDeath != "":
            return(extractYear(str(self.dateDeath)))
        return(None)
    def insertIfNew(self, db):
        cursor = db.cursor()
        if self.gnd != None:
            cursor.execute(f"SELECT id FROM person WHERE gndid LIKE \"{self.gnd}\"")
            result = cursor.fetchone()
            if result != None:
                return(result[0])
        return(self.insertIntoDB(db))
    def insertIntoDB(self, db):
        sql = "INSERT INTO `person`(`gndid`, `name`, `sort`, `aliases`, `nationality`, `startyear`, `endyear`, `lifetime`, `biography`, `literature`, `deprecated`, `notes`, `instime`, `modtime`, `attributes`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (prepare_string(self.gnd), prepare_string(self.name), prepare_string(self.name), prepare_string(self.aliases), prepare_string(self.nationality), self.yearStart, self.yearEnd, self.lifetime, prepare_string(self.biography), prepare_string(self.literature), self.deprecated, prepare_string(self.notes), int(time.time()), int(time.time()), self.attribute_string)
        cursor = db.cursor()
        cursor.execute(sql, val)
        db.commit()
        logging.info(f"{cursor.rowcount} Zeilen in Tabelle person geschrieben. Letzte ID: {cursor.lastrowid}")
        return(cursor.lastrowid)
        # Zurücksetzen von Auto_increment: ALTER TABLE artwork AUTO_INCREMENT = 29000
        
class Artist(Person):
    def __init__(self):
        super().__init__()
        self.flatFields.extend(['role', 'lifetime', 'description'])
        self.role = ""
        self.lifetime = ""
        self.description = ""
    def getYear(self):
        if self.lifetime != "":
            year = extractYearFromSpan(self.lifetime)
            return(year)

class Publisher(Person):
    def __init__(self):
        super().__init__()        
        self.flatFields.extend(['role', 'place', 'time', 'placeTime'])
        self.role = ""
        self.place = ""
        self.time = ""
        self.placeTime = ""
    def getYear(self):
        if re.fullmatch(r"1[456789]\d{2}", self.time) != None:
            return(self.time)
        year = extractYearPrecisely(self.time)
        if year != None:
            return(year)
        year = extractYearPlaceTime(self.placeTime)
        return(year)

class Attribute:
    concordance = {'1' : 'Sache', '2' : 'Bibelstelle', '3' : 'Zitat', '4' : 'Emblem', '5' : 'Motiv', '6' : 'Person', '7' : 'Devise', '8' : 'Ort', '9' : 'Ereignis', '10' : 'Person', 'B' : 'Beruf', 'O' : 'Ort', 'P' : 'Person'}
    def __init__(self, attribute, id):
        self.value = attribute
        try:
            self.type = self.concordance[id]
        except:
            self.type = "Unbestimmt"
        self.related = []
        self.seealso = []

class XMLReader:
    def readElement(XML, element):
        if XML == "":
            return(0)
        ret = []
        tree = et.ElementTree(et.fromstring(XML))
        root = tree.getroot()
        items = root.findall('.//' + element)
        for item in items:
            content = {}
            for child in item:
                content[child.tag] = child.text
            ret.append(content)
        return(ret)
        readElement = classmethod(readElement)
        
def extractSeeAlso(seeAlso):
    seeAlso = seeAlso.replace(", -- > ", ", --> ").replace(", > ", ", --> ")
    parts = seeAlso.split(" s.auch --> ")
    content = parts.pop()
    #content.replace(", --> ", " --> ")
    return(content.split(", --> "))

def separateSize(size):
    numbers = re.findall('([0-9]+) ?x ?([0-9]+)', size)
    ret = {}
    try:
        numbers[0][0]
    except:
        return(None)
    else:
        ret["height"] = numbers[0][0]
    try:
        numbers[0][1]
    except:
        return(None)
    else:
        ret["width"] = numbers[0][1]
        return(ret)

def extractQuo(description):
    trans = []
    description = removeBr(description)
    bq = re.findall('<blockquote>([^<]+)<', description)
    quo = re.findall("„([^“]+)“", description)
    try:
        trans.extend(quo)
    except:
        pass
    try:
        trans.extend(bq)
    except:
        pass
    ret = " - ".join(trans)
    ret = removeLinebreaks(ret)
    return(ret)

def extractShelfmark(source):
    sm = re.findall('\[HAB: ?([^\]]+)\]', source)
    try:
        shelfmark = sm[0]
    except:
        return(None)
    else:
        return(shelfmark)

def removeBr(string):
    string = re.sub('<br ?/?>', ' / ', string)
    return(string)

def removeTags(string):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', string)    

def cleanDescription(description):
    description = re.sub('<br ?/?>', ' / ', description)
    description = removeTags(description)
    description = description.strip()
    description = removeLinebreaks(description)
    return(description)

def removeLinebreaks(text, replacement=" "):
    text = text.replace("\n", replacement)
    text = text.replace('\n', replacement)
    text = text.replace("  ", " ")
    return(text)

def extractYear(string):
    match = re.search(r"[0-9]{3,4}", string)
    try:
        return(match.group(0))
    except:
        return(None)

def extractYearPrecisely(string):
    match = re.search(r"[.\s–/-](1[456789][0-9]{2})", string)
    try:
        return(match.group(1))
    except:
        return(None)

def extractYearPlaceTime(string):
    extract = re.search(r"/(1\d{3})$", string)
    try:
        return(extract.group(1))
    except:
        pass    
    extract = re.search(r"[–-](1\d{3})", string)
    try:
        return(extract.group(1))
    except:
        pass
    extract = re.search(r"[a-z]\s(1\d{3})", string)
    try:
        return(extract.group(1))
    except:
        pass
    extract = re.search(r"([12]\d)\. Jh", string)
    try:
        jh = extract.group(1)
    except:
        return(None)
    conc = { "15":1450, "16":1550, "17":1650, "18":1750, "19":1850, "20":1950 }
    try:
        jh = conc[jh]
    except:
        return(None)
    extract = re.search(r"([12])\. Hälfte", string)
    try:
        hf = extract.group(1)
    except:
        return("ca " + str(jh))
    if hf == "1":
        return("ca " + str(jh - 25))
    if hf == "2":
        return("ca " + str(jh + 25))    
    return(None)

def extractYearFromSpan(string)        :
    match = re.search(r"([0-9]{3,4})[^0-9]+([0-9]{3,4})", string)
    try:
        year = int(match.group(1)) + int(match.group(2))
        year = int(year / 2)
        return(year)
    except:
        match = re.search(r"[0-9]{3,4}", string)
        try:        
            year = int(match.group(0))
            return(year)
        except:
            return(None)

def make_sortable(string):
    if string[0] == "A":
        return(string[2:].zfill(6))
    if string [0] == "B":
        return("b" + string[2:].zfill(6))
        
def prepare_string(val):
    if isinstance(val, str):
        return(val)
    return("")
