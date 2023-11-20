#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

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
    def __str__(self):
        ret = "fDataset:\n {'\n'.join([entry for entry in self.content])}"

class Entry:
    def __init__(self, value, lang = None, auth_sys = None, auth_id = None):
        print(f"{value} {lang} {auth_sys} {auth_id}" )
        if value == None:
            self.value = "" 
        self.value = value
        if lang == None:
            self.language = ""         
        self.language = lang
        if auth_sys == None:
            self.auth_sys = ""         
        self.auth_sys = auth_sys
        if auth_id == None:
            self.auth_id = ""         
        self.auth_id = auth_id
    def __str__(self):
        ret = self.value
        if self.language != "":
            ret = ret + "@" + self.language
        if self.auth_sys and self.auth_id:
            ret = ret + "#" + self.auth_sys + "_" + self.auth_id
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