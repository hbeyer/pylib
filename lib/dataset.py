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
        ret = "Dataset:\n"
        dict_rep = self.to_dict()
        for key, val in dict_rep.items():
            if val == "":
                continue
            ret += f"{key}: {val};"
        return(ret)

class Entry:
    def __init__(self, value, lang = None, auth_sys = None, auth_id = None):
        self.value = value        
        if value == None:
            self.value = "" 
        self.language = lang
        if lang == None:
            self.language = ""         
        self.auth_sys = auth_sys            
        if auth_sys == None:
                self.auth_sys = ""
        self.auth_id = auth_id                
        if auth_id == None:
            self.auth_id = ""         
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
            "dc.title" : [] ,
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