
cp1252
# PyLib: Sammlung von Python-Modulen für die Arbeit mit bibliographischen Daten
Das Repositorium enthält Module, die für die Arbeit mit bibliographischen Daten an der Herzog August Bibliothek Wolfenbüttel mit dem Schwerpunkt Alte Drucke entwickelt wurden. Sie sind optimiert für die Arbeit mit dem PICA-Format, den SRU-Schnittstellen des GBV und K10plus, der WinIBW 3 und das Signaturensystem der HAB. Die Module werden laufend erweitert und angepasst, bei der Verwendung von älterem Client Code kann es daher zu Problemen kommen.
## Installation
Herunterladen des Repositoriums in ein beliebiges Verzeichnis. Im Wurzelverzeichnis der Anwendung (in der Regel "pylib") können Skripte mit Python 3 (getestet mit Python 3.7.0) ausgeführt werden. Die einzelnen Module liegen im Ordner "lib". Sie können folgendermaßen geladen werden:
```python
from lib import {modul} as {namespace}
```
{modul} ist dabei der Name einer im Ordner "lib" liegenden Python-Datei ohne Endung. {namespace} ist ein frei wählbares Kürzel, die Verwendung ist optional.

## Beschreibung der Module
Unvollständige oder obsolete Module werden ausgelassen. Methoden oder Eigenschaften werden nur angegeben, wenn sie für die Benutzung relevant sind.

### Modul bookwheel

Recherche von Erwerbungsdaten anhand von Seitenzahlen im Bücherradkatalogs von August dem Jüngeren (1579–1666).  Zugrunde gelegt werden die Angaben bei Maria von Katte, Herzog August und die Kataloge seiner Bibliothek, in: Wolfenbütteler Beiträge 1 (1972), S. 168–199, hier S. 177–182

Klasse **Catalogue**:

Repräsentation des Bücherradkatalogs.
Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| get_section | page | Dictionary (Daten zur Katalogsektion), None bei Misserfolg | - |
| get_year | page (Seitenzahl als Integer) | Erwerbungsjahr, normalisiert (Integer), None bei Misserfolg | - |

Beispiel: Suche nach den Daten zur Katalogseite 2589:

```python
from lib import bookwheel as bw
cat = bw.Catalogue
sec = cat.get_section(2589)
print(sec)
```
Ausgabe: 

`{'start': 2511, 'end': 2738, 'group': 'Libri Varii', 'dateBegin': '1634', 'year': 1634, 'writer': 'Herzog August'}`

---
### Modul csvt

Abspeichern von Daten in einer CSV-Tabelle, Auslesen vorhandener CSV-Tabellen.

Klasse **Table**:

Abstraktionsschicht für die Arbeit mit einer CSV-Tabelle

Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | fields (Liste mit Feldnamen, Standard leer), content (Liste mit Listen, die Werte enthalten, Standard leer) | Objekt der Klasse Table | - |
| save | path (Pfad zum Speichern ohne Namenserweiterung), encoding (Zeichencodierung, Standard ist "utf-8") | True | Abspeichern einer CSV-Tabelle mit Zeichencodierung utf-8 und Delimiter ";" unter dem angegebenen Namen oder Pfad |
| load | path (Pfad zu der zu ladenden CSV-Datei ohne Namenserweiterung), encoding (Zeichencodierung des Dokuments, Standard ist utf-8) | True bei Erfolg, sonst False | Laden der Feldnamen in Table.fields und der Daten in Table.content |

Beispiel:
```python
from lib import csvt
fields = ["VD16-Nummer", "Jahr", "Signatur"]
data = [
	["VD16 D 2342", "1589", "Rd 2 37 (1)"],
	["VD16 D 2633", "1549", "1003.6 Theol. (5)"],	
	["VD16 D 340", "1586", "QuN 741 (1)"]
	]
table = csvt.Table(fields, data)
table.save("VD16")
```

---
### Modul dataset

Speichern und Verarbeiten von einfachen Metadensätzen wie Dublin Core. 

Klasse **Dataset**
Container für Einträge, diese werden in der Eigenschaft Dataset.fields gespeichert, standardmäßig ein leeres Dictionary.
Daten werden mit dem Feldnamen (z. B. "title") als Index darin gespeichert. Der zugehörige Wert ist eine Liste, die eine beliebige Anzahl an Objekten der Klasse Entry enthält.
Die Klasse ist nicht für die direkte Instanziierung vorgesehen, s. stattdessen Dataset DC

| Methode | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | - | Instanz von Dataset |  |
| add_entry | field (Feldname), entry (Instanz von Entry) |||
| get_entries | field (Feldname) | Liste mit den unter dem Feldnamen gespeicherten Entries | - |
| to_dict | - | Dictionary mit den Feldnamen als Schlüssel und einer Repräsentation der Entries als String, getrennt mit ";" | - |
| to_list | - | Liste mit Dictionaries, die jeden einzelnen Eintrag als Schlüssel-Wert-Paare repräsentieren | - |

Abgeleitete Klasse **DatasetDC**
Dataset mit vordefinierten Feldern für das Datenmodell Dublin Core.

Klasse **Entry**
Ein einzelner Eintrag des Datensatzes. Er beinhaltet neben dem Wert auch optional eine Sprachangabe und eine Normdatenverknüpfung.

| Methode | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | value, lang (Sprachangabe nach ISO 639-2), auth_sys (System der Normdatenverknüpfung, z. B. "GND"), auth_id (Identifier im Normdatensystem, z. B. GND-Nummer) | Instanz von Entry | - |
| \_\_str\_\_ | - | String-Repräsentation des Eintrags mit angehängter Sprachangabe und Normdatenverknüpfung insoweit vorhanden | - |

Beispiel:

```python
import logging
from lib import dataset as ds

example = ds.DatasetDC()
example.add_entry("dc.identifier", ds.Entry("VD16 D 340"))
example.add_entry("dc.title", ds.Entry("Poematum || HENRICI || DECIMATORIS || GIFFHORNENSIS.|| Libri IIII.||", "lat"))
example.add_entry("dc.creator", ds.Entry("Decimator, Heinrich", "", "GND", "124613934"))
example.add_entry("dc.date", ds.Entry("1586"))

print(example.to_dict())
```

Ausgabe:

`{'dc.identifier': 'VD16 D 340', 'dc.identifier.urn': '', 'dc.format': '', 'dc.type': '', 'dc.language': '', 'dc.title': 'Poematum || HENRICI || DECIMATORIS || GIFFHORNENSIS.|| Libri IIII.||@lat', 'dc.subject': '', 'dc.coverage': '', 'dc.description': '', 'dc.creator': 'Decimator, Heinrich#GND_124613934', 'dc.contributor': '', 'dc.publisher': '', 'dc.rights': '', 'dc.rights.uri': '', 'dcterms.rightsHolder': '', 'dc.source': '', 'dc.relation': '', 'dc.date': '1586', 'dc.date.embargo': '', 'dcterms.extent': '', 'dcterms.isPartOf': ''}`

---
### Modul evalpdf
Durchsuchen von PDF-Dateien nach einer Liste von Suchbegriffen oder mit regulären Ausdrücken. Erfordert Installation des Moduls [pdfplumber](https://pypi.org/project/pdfplumber/0.1.2/)

Klasse **Evaluation**:

| Methode | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| __init\_\_ | path (Pfad zu einer lokalen PDF-Datei), sww (Liste mit Suchbegriffen in Kleinbuchstaben), rexx (Set mit Tupeln, in denen jeweils ein Indexbegriff einem regulären Ausdruck zugeordnet wird) | Instanz von Evaluation | - |
| eval | - | True bei Erfolg, None bei Fehler | Durchführen der Suche, Speichern der Ergebnisse unter Evaluation::index |
| \_\_str\_\_ | - | Auflistung der Treffer | - |

Abgeleitete Klasse **EvaluationSDD**:
Evaluation mit vordefinierten Suchwörtern für SDD-relevante Titel der HAB und 

Beispiel: Auswertung von [Auktion 208](ev%20=%20ep.EvaluationSDD%28%22source/kataloge/Reiss-208.pdf%22%29%20ev.eval%28%29%20print%28ev%29) bei Reiss & Sohn

```python
ev = ep.EvaluationSDD("Reiss-208.pdf")
ev.eval()
print(ev)
```

Ausgabe:
```
SDD-Evaluation für source/kataloge/Reiss-208.pdf
17. Jh.: 5, 6, 13, 19, 20, 21, 22, 30, 34, 52, 54, 70, 76, 77, 78, 79, 80, 81, 82, 86, 87, 88, 97, 98, 99, 100, 115, 116, 118, 119, 129
emblem: 19, 38, 79, 116
lüneburg: 65
alchem: 79
```
---
### Modul geo

Modul zum Laden, Speichern und Auffinden von Geodaten. Als Datenbank dient die Datei `placeData.csv` im Wurzelverzeichnis.

Klasse **DB**:

Datenbank, die die Daten aus der CSV-Tabelle lädt und performant vorhält.

 Methoden der Klasse DB:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | path (Dateiname der CSV-Datei ohne Endung, Standardwert ist "placeData") | - | Einlesen der unter path angegebenen CSV-Datei |
| get_by_name | name (Ortsname) | Liste mit den Ortsdaten, False wenn nicht gefunden | - |
| add_place | placeName (Ortsname), getty (Getty-ID, optional), gnd (GND-Nummer, optional), long (geographische Länge, optional), lat (geographische Breite, optional), comment (Kommentar zum Ort, optional) | True | Einfügen eines neuen Datensatzes in die Tabelle |
| get_geodata | - | True | Laden aller fehlenden Geodaten, für die ein Identifier vorliegt, aus dem Getty Thesaurus oder der GND |
| save | - | - | Abspeichern der aktualisierten CSV-Tabelle |


Funktionen des Moduls:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| normalize_placename | placeName (Ortsname) | String (normalisierte Form des Ortsnamens, z. B. "Frankfurt am Main" für "Frankfurt/M.") | - |
| get_geodata_getty | id (des Ortes im Getty Thesaurus) | Liste mit den Werten für Länge und Breite | - |
| get_geodata_gnd | id (GND-Nummer des Normdatensatzes) | Liste mit den Werten für Länge und Breite | - |

Beispiel: Laden der Datenbank, Hinzufügen eines Ortseintrags mit GND-Nummer, Laden der Geodaten, Abspeichern der aktualisierten Tabelle

```python
from lib import geo
db = geo.DB()
db.add_place("Haselünne", "", "4104376-5", "", "", "Landkreis Emsland")
db.get_geodata()
db.save()
```
Beispiel 2: Laden der Datenbank, Suche nach einem Ortseintrag, Ausgeben des Datensatzes als Liste
```python
from lib import geo
db = geo.DB()
test = db.get_by_name("Neustadt an der Aisch")
print(test)
```
Ausgabe: 

``` ['Neustadt an der Aisch', '1040479', '', '10.6333', '49.5833', '']```


---
### Modul gnd

Validieren einer GND-Nummer und Harvesten von Informationen dazu.

Klasse **ID**
| Methode | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | gnd (GND-Nummer) | Instanz der Klasse | Validieren der GND-Nummer, Ergebnis unter ID.valid |
| \_\_str\_\_ | - | String-Repräsentation der GND-Nummer. Bei gescheiterter Validierung wird "(ungültig)" mit ausgegeben | - |
| get_info | - | Dictionary mit Informationen zur beschriebenen Entität (preferredName, dateOfBirth, dateOfDeath, biographicalOrHistoricalInformation, placeOfBirth, placeOfDeath, gender). None bei Misserfolg | - |

Beispiel:
```python
from lib import gnd
test = gnd.ID("141678615")
res = test.get_info()
print(res)
```
Ausgabe:

`{'preferredName': 'Antoinette Amalie, Braunschweig-Lüneburg, Herzogin', 'dateOfBirth': '22. April 1696', 'dateOfDeath': '6. März 1762', 'biographicalOrHistoricalInformation': 'Frau von Herzog Ferdinand Albrecht II. von Braunschweig-Bevern (1680-1735); jüngste Tochter von Herzog Ludwig Rudolf von Braunschweig-Lüneburg (1671-1735) und Prinzessin Christine Luise von Oettingen-Oettingen', 'placeOfBirth': 'Wolfenbüttel', 'placeOfDeath': 'Braunschweig', 'gender': 'Frau'}`

---
### Modul html
Beschreibung folgt

---
### Modul incunabula
Beschreibung folgt

---
### Modul isil

Umrechnung der kataloginternen Bibliothekskennung ELN in eine ISIL gemäß der Berliner [ISIL- und Sigeldatei](https://sigel.staatsbibliothek-berlin.de/suche/). Berücksichtigt werden alle Biblitoheken im VD17. Bereitstellung zusätzlicher Informationen zur Bibliothek und zum Ort.

| Funktion | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| get_isil | ELN (String) | ISIL der Bibliothek, Ausgangswert falls unbekannt | - |
| get_bib | ELN oder ISIL (String) | Dictionary mit den Feldern "bib" (Bibliotheksname), "place" (Ortsname), "gettyPlace" (ID des Ortes im Getty Thesaurus of Geographic Names), "long" (geographische Länge), "lat" (geographische Breite) | - |

---
### Modul language
Beschreibung folgt

---
### Modul lido
Beschreibung folgt

---
### Modul localsql
Beschreibung folgt

---
### Modul maps
Beschreibung folgt

---
### Modul mets
Beschreibung folgt

---
### Modul oai
Beschreibung folgt

---
### Modul opac
Beschreibung folgt

---
### Modul pica
Auslesen von bibliographischen Daten in PICA-XML. Jeder Datensatz wird in eine objektförmige Struktur mit sprechenden Feldnamen und intuitiven hierarchischen Beziehungen umgewandelt. Die Daten können in JSON oder XML abgespeichert werden.

Klasse **Record**
Objekt zur Repräsentation eines bibliographischen Datensatzes. Zur gemeinsamen Benutzung mit xmlreader.DownloadReader

Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | node (xml.etree.ElementTree.Element) | Instanz von Record | - |
| \_\_str\_\_ | - | Repräsentation des Datensatzes als String (enthält PPN und Jahr) | - |

Beispiel:

```python
from lib import xmlreader as xr
from lib import pica

folder = "downloads/helmstedt"
reader = xr.DownloadReader(folder, "record", "info:srw/schema/5/picaXML-v1.0")
for node in reader:
	rec = pica.Record(node)
	print(rec)
```

Klasse **RecordVD16**
Abgeleitete Klasse zur Verarbeitung von Daten aus dem VD 16

Klasse **RecordVD17**
Abgeleitete Klasse zur Verarbeitung von Daten aus dem VD 17

Klasse **RecordVD18**
Abgeleitete Klasse zur Verarbeitung von Daten aus dem VD 18

Klasse **RecordInc**
Abgeleitete Klasse zur Verarbeitung von Inkunabeln

---
### Modul portapp

Abstraktionsschicht für die Porträtdatenbank der HAB, veröffentlicht unter http://portraits.hab.de.

Klasse **ArtCollection**

...

Klasse **Serializer**

...

Abgeleitete Klasse **SerializerXML(Serializer)**

...

Abgeleitete Klasse **SerializerCSV(Serializer)**

...

Abgeleitete Klasse **SerializerSel(SerializerCSV)**

...

Klasse **Artwork**

Enthält die zu einem Porträt gehörigen Daten. 
| Property | Datentyp | Erklärung |
|--|--|--|
| id | String | Interne ID |
| anumber | String | A-Nummer aus Mortzfeld A |
| url | String | URL des Datensatzes in der Online-Fassung |
| urlImage | String | URL der Bilddatei auf dem Server der HAB |
| invNo | String | Inventarnummer |
| artists | Liste | Enthält Instanzen von Artist |
| publishers | Liste | Enthält Instanzen von Publisher |
| sheetsize | String |  |
| sheetsizeSep | Dictionary | Indices "height" und "width" |
| platesize | String |  |
| platesizeSep | Dictionary | Indices "height" und "width" |
| imagesize | String |  |
| imagesizeSep | Dictionary | Indices "height" und "width" |
| technique | String |  |
| notes | String |  |
| description | String |  |
| descriptionClean | String |  |
| quotation | String |  |
| catalogs | String |  |
| condition | String |  |
| source | String |String |
| shelfmarkSource | String |  |
| instime | String | Datum der Anlage des Datensatzes als Unix-Timestamp  |
| modtime | String | Datum der letzten Änderung als Unix-Timestamp  |
| yearNormalized | String | Jahr als vierstellige Zahl |
| sourceYear | Code zur Ermittlung von yearNormalized |  |
| keywords_technique | String  |  |
| transcription | String  |  |
| portraitType | String  |  |
| orientation | String  |  |
| personsRepr | Liste | Instanzen von Person |
| attributes | Liste | Instanzen von Attribute |


Klasse **Person**

...

Abgeleitete Klasse **Artist(Person)**

...

Abgeleitete Klasse **Publisher(Person)**

...

Klasse **Attribute**

...

Klasse **XMLReader**

...

Beispiel: Laden von 100 Datensätzen aus der Datenbank in eine Instanz von ArtCollection. Die Iteration über die ArtCollection ergibt Instanzen von Artwork:

```python
import mysql.connector
from lib import portapp as pa

db = mysql.connector.connect(
  host="{server}",
  user="{user}",
  password="{password}",
  database="portraits"
)
col = pa.ArtCollection(db)
col.loadBySQL("SELECT * FROM artwork LIMIT 100 OFFSET 0")
for aw in col:
	print(aw)
```

---
### Modul romnumbers

Parsen und Erzeugen römischer Zahlen. Anders als mit dem Modul roman (https://pypi.org/project/roman/)  können auch additive Zahlen (IIII statt IV) gelesen werden. Punkte und Leerzeichen werden automatisch entfernt.

| Funktion | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| to_arabic | lett (String) | Wert der römischen Zahl als Integer, None bei Validierungsfehler | - |
| to_roman | num (Integer) | Zahl in klein geschriebenen römischen Ziffern, None falls kein Integer übergeben wurde | - 

---
### Modul shelfmark
Beschreibung folgt

---
### Modul sru
Das Modul ermöglicht den Zugriff auf SRU-Schnittstellen zum Download bibliographischer Daten

Klasse **Request_SRU**

Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | base (URL SRU-Schnittstelle), version (optional, Standard ist "2.0") | Instanz von SRU_Request | - |
|prepare|query_pica (Suchbefehl in PICA-Kommandozeilensprache), format (optional, Standard "picaxml")|Anzahl der gefundenen Treffer|  Ermittlung der Treffermenge, Speichern einer initialen Such-URL |
|download| folder (Pfad zum Downloadordner), fileName (optionaler Dateiname, Standard "downloadSRU") | kein Rückgabewert | Herunterladen der XML-Daten in Paketen zu 500 Treffern in den Download-Ordner |
| make_url | maxRecords (optional, Standard 1), startRecord (optional, Standard1) | URL für den Download einer einzelnen Datei | - |

Eigenschaften:

- str filename: Dateiname für den Download
- str base: URL der abgefragten SRU-Schnittstelle ohne schließendes "/"
- str url: URL für den aktuellen Download
- str version: SRU-Version
- str query_pica: Suchbefehl in PICA-Kommandozeilensprache. Blanks bleiben erhalten, vor Suchschlüsseln steht jeweils "pica." Die verfügbaren Suchschlüssel sind auf der Startseite der SRU-Schnittstelle aufgeführt, s. z. B. http://sru.k10plus.de/k10plus?version=2.0
- str query_pica_enc: Suchbefehl in aufbereiteter Form für die Schnittstelle

Klasse **Request_K10plus**

Abgeleitete Klasse zur Nutzung der SRU-Schnittstelle des K10plus-Verbundkatalogs. Der Parameter "base" entfällt bei der Initialisierung, Methoden s. o.

Klasse **Request_VD17**

Abgeleitete Klasse zur Nutzung der SRU-Schnittstelle des VD17, Funktionsweise s. o.

Klasse **Request_VD18**

Abgeleitete Klasse zur Nutzung der SRU-Schnittstelle des VD18, Funktionsweise s. o.

Klasse **Request_HAB**

Abgeleitete Klasse zur Nutzung der SRU-Schnittstelle des lokalen OPAC der HAB, Funktionsweise s. o.

Beispiel: Herunterladen aller Katalogaufnahmen mit der Provenienz "Helmstedt" aus dem OPAC der HAB
```python
from lib import sru
folder = "downloads/helmstedt"
req = sru.Request_HAB()
req.prepare("pica.prn=Helmstedt and pica.bbg=A[af]*")
print(f"Datensätze: {req.numFound}")
req.download(folder)
```

---
### Modul table_winibw
Klasse zur Arbeit mit CSV-Dateien, die mit MS Excel erzeugt wurden (Zeichencodierung "cp1252", Trennzeichen ";"). Insbesondere mit der WinIBW erzeugte CSV-Tabellen (Funktion "Exceltabelle erzeugen") können so leicht verarbeitet werden.

Klasse **Table**
Repräsentiert eine Tabelle und enthält die Daten in der Property `content`, die Felder in der Property `fields`. Ist iterierbar und gibt einzelne Zeilen als OrdererdDict aus.

| Methode  | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | path | - | Lädt die Daten aus der Tabelle in die Property content. Die Feldnamen werden in fields gespeichert |
| getByField | field | Liste mit allen Werten der entsprechenden Spalte | - |
| getSelection | fields (Liste mit Feldnamen) | Liste, enthält für jede Zeile eine Liste mit den ausgewählten Feldern | - |
| addSortable | field (Feld, in dem eine Signatur der HAB steht. Standardwert ist "Signatur") | True bei Erfolg | Hinzufügen einer Spalte mit dem Namen "Sortierform", in dem eine von der Klasse SortableShelfmark im Modul shelfmark erzeugte Sortierform eingefügt wurde. Funktioniert nur für Signaturen der HAB |
| addParallels | fieldMan (Feld mit dem Identifier der Manifestation, Standardtwert ist "PPN"), fieldEx (Feld mit dem Identifier des Exemplars, Standardwert ist "Signatur") | True bei Erfolg | Anlegen einer neuen Spalte "Parallelexemplare", in dem die Identifier der Parallelexemplare für diese Ausgabe ausgegeben werden, mehrere getrennt durch ";" |
| save | fileName (Dateiname ohne Endung, Standardwert ist "myTable") | True bei Erfolg | Abspeichern der Tabelle als CSV-Datei unter dem angegebenen Dateinamen |
| toSQLite | fileName (Dateiname, Standardwert ist "exportTable") | True bei Erfolg | Gibt die Tabelle als SQLite-Datenbank mit einer einzelnen Tabelle aus, die unter fileName abgespeichert wird. |

Beispiel: Laden einer Tabelle mit Datensätzen und Einfügen einer Spalte mit der jeweiligen Sortierform, Abspeichern unter einem neuen Dateinamen.

```python
from lib import table_winibw as tw

tab = tw.table("records.csv")
tab.addSortable()
tab.save("records-sortable")
```

---
### Modul unapi
Beschreibung folgt

---
### Modul xmlreader
Extraktion wiederkehrender Knoten aus XML-Dokumenten. Die Knoten werden als Instanzen von xml.etree.ElementTree.Element (s. [Dokumentation](https://docs.python.org/3/library/xml.etree.elementtree.html#element-objects)) ausgegeben. Beim Auslesen eines Ordners werden alle darin enthaltenen XML-Dokumente berücksichtigt, beim Auslesen einer URL der darin enthaltene XML-Code.

Klasse **DownloadReader**

Reader zum Auslesen der XML-Dokumente in einem Ordner. 

| Methode  | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | path (Pfad des Ordners), tag (Elementname des auszugebenden Knotens), namespace (Namespace des auszugebenden Knotens) | Instanz von DownloadReader | - |

Objekte dieser Klasse sind iterierbar und geben Knoten als Instanzen von xml.etree.ElementTree.Element aus.

Beispiel: Auslesen der XML-Dokumente im Verzeichnis "downloads/helmstedt". Gesucht wird nach Elementen mit dem namen "record" und dem Namespace "info:srw/schema/5/picaXML-v1.0":
```python
from lib import xmlreader as xr
reader = xr.DownloadReader("downloads/helmstedt", "record", "info:srw/schema/5/picaXML-v1.0")
for node in reader:
	print(node)
```

Klasse **WebReader**

Reader zum Lesen von XML-Daten aus einer Webquelle. Wird initialisiert wie DownloadReader, statt eines Ordners wird aber eine Webadresse angegeben.

Klasse **OAIDownloadReader**

Abgeleitete Klasse von DownloadReader, voreingestellt für Downloads von einer OAI 2.0-Schnittstelle

Klasse **SRUDownloadReader**

Abgeleitete Klasse von DownloadReader, voreingestellt für Downloads von einer SRU-Schnittstelle

Klasse **UnAPIReader**

Reader zum Auslesen von Downloads aus einer unAPI


---
### Modul xmlserializer
Beschreibung folgt


> Written with [StackEdit](https://stackedit.io/).

