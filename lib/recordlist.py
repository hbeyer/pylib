#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import pica
from lib import xmlserializer as xs
import json

class RecordList():
    def __init__(self, content = None):
        self.content = []
        if content != None:
            for obj in content:
                if isinstance(obj, pica.Record):
                    pass
                else:
                    raise TypeError("Recordlist darf nur Objekte vom Typ pica.Record enthalten")
            self.content = content
    def to_json(self, file_name):
        with open(file_name + ".json", "w") as fp:
            json.dump(self.content, fp, skipkeys=False, ensure_ascii=False, check_circular=True, allow_nan=True, cls=None, indent=1, separators=[',', ':'], default=convert_record, sort_keys=False)
    def to_libreto(self, file_name, metadata, prov = ""):
        ser = xs.Serializer(file_name, "collection")
        ser.add_nested("metadata", metadata)
        for count, rec in enumerate(self.content):
            itemNode = rec.to_libreto(prov)
            ser.add_node(itemNode)
        ser.save()
    
def convert_record(record):
    return(record.to_dict())

