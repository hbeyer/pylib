#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as et
import csv

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
        cursorPersAttr = self.db.cursor(dictionary=True, buffered=True)
        cursorPersAttrSeeAlso = self.db.cursor(dictionary=True, buffered=True)
        cursorAttr = self.db.cursor(dictionary=True, buffered=True)
        cursorAttrRel = self.db.cursor(dictionary=True, buffered=True)
        cursor.execute(sqlArtwork)
        for row in cursor:
            artwork = Artwork()
            artwork.importRow(row)
            cursorPers.execute("SELECT * FROM artwork_person RIGHT JOIN person ON artwork_person.person = person.id WHERE artwork_person.artwork = " + str(artwork.id))
            for rowPers in cursorPers:
                cursorPersAttr.execute("SELECT * FROM person_attribute WHERE person_attribute.person = " + str(rowPers["id"]))
                attributes = []
                for rowAttributes in cursorPersAttr:
                    attribute = Attribute(rowAttributes["value"], rowAttributes["type"])
                    sql = "SELECT * FROM person_attribute_seealso WHERE person_attribute_seealso.value = %s"
                    val = (rowAttributes["value"], )
                    cursorPersAttrSeeAlso.execute(sql, val)
                    for seeAlso in cursorPersAttrSeeAlso:
                        seeAlsoValues = extractSeeAlso(seeAlso["seealso"])
                        attribute.seealso.extend(seeAlsoValues)
                    attributes.append(attribute)
                artwork.importPerson(rowPers, attributes)
            cursorAttr.execute("SELECT * FROM artwork_attribute WHERE artwork_attribute.artwork = " + str(artwork.id))
            for rowAttr in cursorAttr:
                attribute = Attribute(rowAttr["value"], rowAttr["type"])
                sql = "SELECT * FROM artwork_attribute_related WHERE artwork_attribute_related.value = %s"
                val = (rowAttr["value"], )
                cursorAttrRel.execute(sql, val)
                for rowAttrRel in cursorAttrRel:
                    attribute.related.append(rowAttrRel["related"])
                artwork.attributes.append(attribute)
            self.addWork(artwork)
        return(1)
    def load(self, limit=100, offset=1):
        sql = "SELECT * FROM artwork LIMIT " + str(limit) + " OFFSET " + str(offset)
        self.loadBySQL(sql)
        return(1)
    def loadByANumber(self, anumber):
        anumber = str(anumber)
        number = re.search('[0-9]+', anumber).group(0)
        sql = "SELECT * FROM artwork WHERE artwork.anumber = \"A " + number + "\""
        self.loadBySQL(sql)

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
            item.keywords_technique = item.extractTechnique()
            item.sourceYear = None
            item.yearNormalized = item.getNormalizedYear()
            if item.yearNormalized != None:
                item.sourceYear = "publisher"
            else:
                item.yearNormalized = extractYearPrecisely(item.technique)
                if item.yearNormalized != None:
                    item.sourceYear = "technique"
                else:
                    item.yearNormalized = extractYearPrecisely(item.source)
                    if item.yearNormalized != None:
                        item.sourceYear = "source"
            item.portraitType = item.getPortraitType()
            item.orientation = item.getOrientation()
            item.likeA = item.getLikeA()
            if item.likeA != None:
                controllCollection.content = []
                controllCollection.loadByANumber(item.likeA)
                try:
                    model = controllCollection.content[0]
                except:
                    pass
                else:
                    if item.keywords_technique == "" or item.keywords_technique == None:
                        item.keywords_technique = model.extractTechnique()
                    if item.yearNormalized == "" or item.yearNormalized == None:
                        item.yearNormalized = model.getNormalizedYear()
                        if item.yearNormalized != None:
                            item.sourceYear = "publisherA"
                        else:
                            item.yearNormalized = extractYearPrecisely(model.technique)
                            if item.yearNormalized != None:
                                item.sourceYear = "techniqueA"
                            else:
                                item.yearNormalized = extractYearPrecisely(model.source)
                                if item.yearNormalized != None:
                                    item.sourceYear = "sourceA"
                    if item.portraitType == "" or item.portraitType == None:
                        item.portraitType = model.getPortraitType()
                    if item.orientation == "" or item.orientation == None:
                        item.orientation = model.getOrientation()                    
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
        self.invNo = None
        self.artists = []
        self.publishers = []
        self.sheetsize = None
        self.sheetsizeSep = None
        self.platesize = None
        self.platesizeSep = None
        self.imagesize = None
        self.imagesizeSep = None
        self.technique = None
        self.notes = None
        self.description = None
        self.descriptionClean = None
        self.quotation = None
        self.catalogs = None
        self.condition = None
        self.source = None
        self.shelfmarkSource = None
        self.instime = None
        self.modtime = None
        self.personsRepr = []
        self.attributes = []
    def __str__(self):
        ret = "Artwork Nr. " + str(self.id) + ", A " + str(self.anumber) + ", URL: " + self.url + ", Image: " + self.urlImage
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
        self.anumber = row["anumber"][2:]
        self.invNo = row["inventorynumber"]
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
        self.condition = row["condition"]
        self.source = removeLinebreaks(row["source"])
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
    def importPerson(self, row, attributes):
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
        personObj.attributes = attributes
        self.personsRepr.append(personObj)
        return(1)
    def makeAttributeString(self, sep="/"):
        attr = [attr.value for attr in self.attributes]
        return(sep.join(attr))
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
        self.biography = ""
        self.literature = ""
        self.instime = None
        self.modtime = None
        self.dateBirth = ""
        self.placeBirth = ""
        self.dateDeath = ""
        self.placeDeath = ""
        self.attributes = []
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
    def makeAttributeString(self, sep="/"):
        attr = [attr.value for attr in self.attributes]
        return(sep.join(attr))
    def getYear(self):
        if self.yearEnd != None:
            return(self.yearEnd)
        if self.dateDeath != "":
            return(extractYear(str(self.dateDeath)))
        return(None)

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