#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import geo

class Isil:
    bibList = {
        "DE-01" : { "bib" : "Staatsbibliothek zu Berlin - Preußischer Kulturbesitz", "place" : "Berlin", "gettyPlace" : "7003712", "long" : "13.391458121223913", "lat" : "52.51842556249303" },
        "DE-3" : { "bib" : "Universitäts- und Landesbibliothek Sachsen-Anhalt", "place" : "Halle (Saale)", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-7" : { "bib" : "Niedersächsische Staats- und Universitätsbibliothek Göttingen", "place" : "Göttingen", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-8" : { "bib" : "Universitätsbibliothek Kiel, Zentralbibliothek", "place" : "Kiel", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-9" : { "bib" : "Universitätsbibliothek Greifswald", "place" : "Greifswald", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-11" : { "bib" : "Humboldt-Universität zu Berlin, Universitätsbibliothek, Jacob-und-Wilhelm-Grimm-Zentrum", "place" : "Berlin", "gettyPlace" : "", "long" : "13.391036067895548", "lat" : "52.52045224835106"  },        
        "DE-12" : { "bib" : "Bayerische Staatsbibliothek", "place" : "München", "gettyPlace" : "", "long" : "11.580306358647174", "lat" : "48.14747719682253"  },
        "DE-14" : { "bib" : "Sächsische Landesbibliothek - Staats- und Universitätsbibliothek Dresden", "place" : "Dresden", "gettyPlace" : "", "long" : "", "lat" : ""  },        
        "DE-15" : { "bib" : "Universitätsbibliothek Leipzig", "place" : "Leipzig", "gettyPlace" : "", "long" : "12.368251884324346", "lat" : "51.332328960034026"  },        
        "DE-16" : { "bib" : "Universitätsbibliothek Heidelberg", "place" : "Heidelberg", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-17" : { "bib" : "TU Darmstadt, Universitäts- und Landesbibliothek", "place" : "Darmstadt", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-18" : { "bib" : "Staats- und Universitätsbibliothek Hamburg Carl von Ossietzky", "place" : "Hamburg", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-19" : { "bib" : "Universitätsbibliothek der LMU München", "place" : "München", "gettyPlace" : "", "long" : "11.580671001416981", "lat" : "48.15012119792592"  },
        "DE-21" : { "bib" : "Universitätsbibliothek der Eberhard Karls Universität", "place" : "Tübingen", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-31" : { "bib" : "Badische Landesbibliothek", "place" : "Karlsruhe", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-23" : { "bib" : "Herzog August Bibliothek Wolfenbüttel", "place" : "Wolfenbüttel", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-24" : { "bib" : "Württembergische Landesbibliothek", "place" : "Stuttgart", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-27" : { "bib" : "Thüringer Universitäts- und Landesbibliothek", "place" : "Jena", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-28" : { "bib" : "Universitätsbibliothek Rostock", "place" : "Rostock", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-29" : { "bib" : "Universitätsbibliothek Erlangen-Nürnberg", "place" : "Erlangen", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-30" : { "bib" : "Universitätsbibliothek J. C. Senckenberg, Zentralbibliothek", "place" : "Frankfurt am Main", "gettyPlace" : "", "long" : "8.652997404383951", "lat" : "50.12051692359684"  },
        "DE-32" : { "bib" : "Klassik Stiftung Weimar / Herzogin Anna Amalia Bibliothek", "place" : "Weimar", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-33" : { "bib" : "Landesbibliothek Mecklenburg-Vorpommern Günther Uecker im Landesamt für Kultur und Denkmalpflege", "place" : "Schwerin", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-35" : { "bib" : "Gottfried Wilhelm Leibniz Bibliothek - Niedersächsische Landesbibliothek", "place" : "Hannover", "gettyPlace" : "", "long" : "9.731263015245261", "lat" : "52.36528860983751"  },
        "DE-36" : { "bib" : "Wissenschaftliche Stadtbibliothek", "place" : "Mainz", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-39" : { "bib" : "Forschungsbibliothek Gotha", "place" : "Gotha", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-56" : { "bib" : "Stadtbibliothek Braunschweig", "place" : "Braunschweig", "gettyPlace" : "7004434", "long" : "", "lat" : ""  },
        "DE-69" : { "bib" : "Stadtbibliothek Koblenz", "place" : "Koblenz", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-70" : { "bib" : "Landesbibliothek Coburg", "place" : "Coburg", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-75" : { "bib" : "Stadtbibliothek im Bildungscampus Nürnberg", "place" : "Nürnberg", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-824" : { "bib" : "Universitätsbibliothek Eichstätt-Ingolstadt", "place" : "Eichstätt", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-107" : { "bib" : "Landesbibliothekszentrum Rheinland-Pfalz / Pfälzische Landesbibliothek", "place" : "Speyer", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-115" : { "bib" : "Stadtbibliothek Hannover", "place" : "Hannover", "gettyPlace" : "", "long" : "9.745171688891093", "lat" : "52.36686472961998"  },
        "DE-125" : { "bib" : "Ratsschulbibliothek, Wissenschaftliche Bibliothek", "place" : "Zwickau", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-155" : { "bib" : "Staatliche Bibliothek Regensburg", "place" : "Regensburg", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-211" : { "bib" : "Erzbischöfliche Akademische Bibliothek Paderborn", "place" : "Paderborn", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-294" : { "bib" : "Ruhr-Universität Bochum, Universitätsbibliothek", "place" : "Bochum", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-384" : { "bib" : "Universitätsbibliothek Augsburg", "place" : "Augsburg", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-547" : { "bib" : "Forschungsbibliothek Gotha", "place" : "Gotha", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-2863" : { "bib" : "Kirchenbibliothek Pegau", "place" : "Pegau", "gettyPlace" : "7012856", "long" : "12.25308983449468", "lat" : "51.16682363316249"  },
        "DE-Em2" : { "bib" : "Johannes a Lasco Bibliothek Große Kirche Emden", "place" : "Emden", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-Hel1" : { "bib" : "Ehemalige Universitätsbibliothek", "place" : "Helmstedt", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "DE-B791" : { "bib" : "Bundesverwaltungsgericht, Bibliothek", "place" : "Leipzig", "gettyPlace" : "", "long" : "12.369873117352697", "lat" : "51.33310473527676"  },
        "DE-F42" : { "bib" : "Philosophisch-Theologische Hochschule Sankt Georgen, Bibliothek", "place" : "Frankfurt am Main", "gettyPlace" : "", "long" : "8.713434525842262", "lat" : "50.0991122102516"  },
        "DE-MUS-621612" : { "bib" : "Bibliothek der St. Nikolai-Kirche Spandau", "place" : "Berlin-Spandau", "gettyPlace" : "7097050", "long" : "13.205180697609013", "lat" : "52.53834514899271"  },
        "AT-HBTL" : { "bib" : "Diözesan- und Universitätsbibliothek der Katholischen Privatuniversität Linz", "place" : "Linz", "gettyPlace" : "", "long" : "14.29172291838839", "lat" : "48.30390431698453"  },        
        "AT-OeNB" : { "bib" : "Österreichische Nationalbibliothek", "place" : "Wien", "gettyPlace" : "", "long" : "16.366962289591015", "lat" : "48.206343754822974"  },
        "VD17R" : { "bib" : "VD17-Redaktion", "place" : "Verschiedene", "gettyPlace" : "", "long" : "", "lat" : ""  },
        "5113" : { "bib" : "Kirchenbibliothek Röhrsdorf", "place" : "Röhrsdorf", "gettyPlace" : "7111557", "long" : "13.52494135718249", "lat" : "51.095493363877786"  },        
        "5119" : { "bib" : "Spezialbibliothek der Bundeswehr", "place" : "Verschiedene", "gettyPlace" : "", "long" : "", "lat" : ""  },        
        "5120" : { "bib" : "Geistliches Ministerium Greifswald", "place" : "Greifswald", "gettyPlace" : "", "long" : "", "lat" : ""  }        
    }
    corrVD17 = {
        "0001" : "DE-1",
        "0056" : "DE-56",
        "0824" : "DE-824",
        "0028" : "DE-28",
        "0017" : "DE-17",
        "0014" : "DE-14",
        "5002" : "DE-MUS-621612",
        "3703" : "DE-Em2",
        "KALB" : "DE-31",
        "0024" : "DE-24",
        "4369" : "DE-4369",
        "TUUB" : "DE-21",
        "0069" : "DE-69",
        "5007" : "AT-HBTL",
        "0027" : "DE-27",
        "0115" : "DE-115",
        "0003" : "DE-3",
        "0031" : "DE-31",
        "DDSU" : "DE-14",
        "9511" : "AT-OeNB",
        "0007" : "DE-7",
        "0029" : "DE-29",
        "2028" : "DE-32",
        "0107" : "DE-107",
        "0070" : "DE-70",
        "0023" : "DE-23",
        "5119" : "5119",
        "L1PGKB" : "DE-2863",
        "0294" : "DE-294",
        "0019" : "DE-19",
        "0011" : "DE-11",
        "0030" : "DE-30",
        "3614" : "DE-F42",
        "0016" : "DE-16",
        "1999" : "VD17R",
        "0075" : "DE-75",
        "L1BV" : "DE-B791",
        "0033" : "DE-33",
        "0384" : "DE-384",
        "0012" : "DE-12",
        "5113" : "5113",
        "0015" : "DE-15",
        "3122" : "DE-Hel1",
        "0009" : "DE-9",
        "5120" : "5120",
        "0008" : "DE-8",
        "4620" : "VD17R",
        "0039" : "DE-39",
        "0018" : "DE-18",
        "0035" : "DE-35",
        "0547/0039" : "DE-537",
        "0125" : "DE-125",
        "0036" : "DE-36",
        "L1UB" : "DE-15",
        "0155" : "DE-155",
        "0021" : "DE-21",
        "0547" : "DE-547",
        "0032" : "DE-32",
        "5051" : "DE-B791",
        "HDUB" : "DE-16", 
        "0211" : "DE-211" 
    }    
def getBib(code, vd17 = True):
    if vd17 == True:
        try:
            Isil.code = corrVD17(code)
        except:
            pass
    try:
        return(Isil.bibList[code])
    except:
        return(False)