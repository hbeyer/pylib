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
Beschreibung folgt
### Modul csvt
Beschreibung folgt
### Modul dataset
Beschreibung folgt
### Modul geo
Beschreibung folgt
### Modul gnd
Beschreibung folgt
### Modul html
Beschreibung folgt
### Modul incunabula
Beschreibung folgt
### Modul isil
Beschreibung folgt
### Modul language
Beschreibung folgt
### Modul lido
Beschreibung folgt
### Modul localsql
Beschreibung folgt
### Modul maps
Beschreibung folgt
### Modul mets
Beschreibung folgt
### Modul oai
Beschreibung folgt
### Modul opac
Beschreibung folgt
### Modul pica
Auslesen von bibliographischen Daten in PICA-XML. Jeder Datensatz wird in eine objektförmige Struktur mit sprechenden Feldnamen und intuitiven hierarchischen Beziehungen umgewandelt. Die Daten können in JSON oder XML abgespeichert werden.

Klasse **Record**
Objekt zur Repräsentation eines bibliographischen Datensatzes. Zur gemeinsamen Benutzung mit xmlreader.DownloadReader

Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | node (xml.etree.ElementTree.Element) | Objekt vom Typ Record | - |
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

### Modul portapp
Beschreibung folgt
### Modul shelfmark
Beschreibung folgt
### Modul sru
Das Modul ermöglicht den Zugriff auf SRU-Schnittstellen zum Download bibliographischer Daten

Klasse **Request_SRU**

Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | base (URL SRU-Schnittstelle), version (optional, Standard ist "2.0") | Objekt vom Typ SRU_Request | - |
|prepare|query_pica (Suchbefehl in PICA-Kommandozeilensprache), format (optional, Standard "picaxml")|Anzahl der gefundenen Treffer|  Ermittlung der Treffermenge, Speichern einer initialen Such-URL |
|download| folder (Pfad zum Downloadordner), fileName (optionaler Dateiname, Standard "downloadSRU") | kein Rückgabewert | Herunterladen der XML-Daten in Paketen zu 500 Treffern in den Download-Ordner |
| make_url | maxRecords (optional, Standard 1), startRecord (optional, Standard1) | URL für den Download einer einzelnen Datei | - |

Parameter:

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
### Modul table_winibw
Beschreibung folgt
### Modul unapi
Beschreibung folgt
### Modul xmlreader
Extraktion wiederkehrender Knoten aus XML-Dokumenten. Die Knoten werden als Objekte vom Typ xml.etree.ElementTree.Element (s. [Dokumentation](https://docs.python.org/3/library/xml.etree.elementtree.html#element-objects)) ausgegeben. Beim Auslesen eines Ordners werden alle darin enthaltenen XML-Dokumente berücksichtigt, beim Auslesen einer URL der darin enthaltene XML-Code.

Klasse **DownloadReader**

Reader zum Auslesen der XML-Dokumente in einem Ordner. 

| Methode  | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | path (Pfad des Ordners), tag (Elementname des auszugebenden Knotens), namespace (Namespace des auszugebenden Knotens) | Objekt vom Typ DownloadReader | - |

Objekte dieser Klasse sind iterierbar und geben Knoten als Objekte vom Typ xml.etree.ElementTree.Element aus.

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

### Modul xmlserializer
Beschreibung folgt


> Written with [StackEdit](https://stackedit.io/).
