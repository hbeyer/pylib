# PyLib: Sammlung von Python-Modulen für die Arbeit mit bibliographischen Daten
Das Repositorium enthält Module, die für die Arbeit mit bibliographischen Daten an der Herzog August Bibliothek Wolfenbüttel mit dem Schwerpunkt Alte Drucke entwickelt wurden. Sie sind optimiert für die Arbeit mit dem PICA-Format, den SRU-Schnittstellen des GBV und K10plus, der WinIBW 3 und das Signaturensystem der HAB. Die Module werden laufend erweitert und angepasst, bei der Verwendung von älterem Client Code kann es daher zu Problemen kommen.
## Installation
Herunterladen des Repositoriums in ein beliebiges Verzeichnis. Im Wurzelverzeichnis der Anwendung (in der Regel "pylib") können Skripte mit Python 3 (getestet mit Python 3.7.0) ausgeführt werden. Die einzelnen Module liegen im Ordner "lib". Sie können folgendermaßen geladen werden:
```python
from lib import {modul} as {namespace}
```
{modul} ist dabei der Name einer im Ordner "lib" liegenden Python-Datei ohne Endung. {namespace} ist ein frei wählbares Kürzel, die Verwendung ist optional.
## Beschreibung der Module
Unvollständige oder obsolete Module werden ausgelassen.

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
Beschreibung folgt
### Modul portapp
Beschreibung folgt
### Modul shelfmark
Beschreibung folgt
### Modul sru
Das Modul ermöglicht den Zugriff auf SRU-Schnittstellen zum Download bibliographischer Daten

Klasse **Request_SRU**
Initialisierung mit den Parametern "base" für die URL einer SRU-Schnittstelle (z. B. "http://sru.k10plus.de/k10plus") sowie optional "version" für die SRU-Version
Methoden:
| Name | Parameter | Rückgabewert | Effekt |
|--|--|--|--|
| \_\_init\_\_ | base (URL SRU-Schnittstelle), version (optional, Standard ist "2.0") | Objekt vom Typ SRU_Request | - |
|prepare|query_pica (Suchbefehl in PICA-Kommandozeilensprache), format (optional, Standard "picaxml")|Anzahl der gefundenen Treffer|  Ermittlung der Treffermenge, Speichern einer initialen Such-URL |
|download| folder (Pfad zum Downloadordner), fileName (optionaler Dateiname, Standard "downloadSRU") | kein Rückgabewert | Herunterladen der XML-Daten in Paketen zu 500 Treffern in den Download-Ordner |
| make_url | maxRecords (optional, Standard 1), startRecord (optional, Standard1) | URL für den Download einer einzelnen Datei | - |

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
### Modul xsmlreader
Beschreibung folgt
### Modul xmlserializer
Beschreibung folgt


> Written with [StackEdit](https://stackedit.io/).
