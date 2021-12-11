#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Dataset:
    def __init__(self):
        self.fields = {}
    def add_entry(self, field, entry):
        try:
            self.fields[field].append(entry)
        except:
        	logging.error(f"Feld {field} ist nicht definiert")
    def get_entries(self, field):
        try:
            return(self.fields[field])
        except:
            return(None)
    def to_dict(self):
        ret = {}
        for name in self.fields:
            ret[name] = ";".join([str(entry) for entry in self.fields[name]])
        return(ret)
    def to_list(self):
        ret = []
        for name in self.fields:
            for entry in self.fields[name]:
                ret.append({name : str(entry)})
        return(ret)

class Entry:
    def __init__(self, value, lang = None, authSys = "", authID = ""):
        self.value = value
        self.language = lang
        self.authSys = authSys
        self.authID = authID
    def __str__(self):
        ret = self.value
        if self.language != None:
            ret = ret + "@" + self.language
        if self.authSys and self.authID:
            ret = ret + "#" + self.authSys + "_" + self.authID
        return(ret)

class DatasetDC(Dataset):
    def __init__(self):
        super().__init__()
        self.fields = {
            "dc.identifier" : [],
            "dc.identifier.urn" : [],
            "dc.format" : [],
            "dc.type" : [],
            "dc.language" : [],
            "dc.title" : [],
            "dc.subject" : [],
            "dc.coverage" : [],
            "dc.description" : [],
            "dc.creator" : [],
            "dc.contributor" : [],
            "dc.publisher" : [],
            "dc.rights" : [],
            "dc.rights.uri" : [],
            "dcterms.rightsHolder" : [],
            "dc.source" : [],
            "dc.relation" : [],
            "dc.date" : [],
            "dc.date.embargo" : [],
            "dcterms.extent" : [],
            "dcterms.isPartOf" : [],
            "dc.date.embargo" : [],
        }