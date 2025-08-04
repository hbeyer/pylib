#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
import os
import json
import functools
logging.basicConfig(level=logging.INFO)

class Manifest:
    def __init__(self, ressource):
        self.res = ressource
        self.content = { 
            "@context" : "http://iiif.io/api/presentation/3/context.json",
            "id" : ressource,
            "type" : "Manifest",
            "label" : {},
            "metadata" : [],
            "items" : []
            }
    def add_label(self, label, lang = None):
        if lang == None:
            lang = "de"
            self.content["label"][lang] = [label]
    def add_metadata_property(self, field_ger, value_ger, field_eng = None, value_eng = None):
        if field_eng and value_eng:
            self.content["metadata"].append({ "label" : [ { "language" : "de", "value" : field_ger }, { "@language" : "en", "@value" : field_eng } ], "value" : [ { "@language" : "de", "@value" : value_ger }, { "@language" : "en", "@value" : value_eng } ] })
            return
        if field_eng:
            self.content["metadata"].append({ "label" : [ { "@language" : "de", "@value" : field_ger }, { "@language" : "en", "@value" : field_eng } ], "value" : [ { "@language" : "de", "@value" : value_ger }, { "@language" : "en", "@value" : value_ger } ] })
            return
        self.content["metadata"].append({ "label" : [ { "@language" : "de", "@value" : field_ger }, { "@language" : "en", "@value" : field_eng } ]})
    def add_homepage(self, label_de, label_en, url):
        self.content["homepage"] = { "id" : url, "type" : "Text", "label" : { "de" : [label_de], "en" : [label_en] } }
        return
    def add_canvas(self, canvas):
        self.content["items"].append(canvas.content)
    def add_page_lazily(self, base_do, base_api, number, height, width, format):
        annotation = Annotation(f"{base_do}-{number}/annotation", base_api, f"{base_do}-{number}/canvas", height, width, format)
        annotation_page = AnnotationPage(f"{base_do}-{number}/page")
        annotation_page.add_annotation(annotation)
        canvas = Canvas(f"{base_do}-{number}/canvas", height, width)
        canvas.add_label(f"Image {number}")
        canvas.add_page(annotation_page)
        id_thumb = f"{base_api}full/150,/0/default.{get_extension(format)}"
        canvas.add_thumbnail(id_thumb, format)
        self.add_canvas(canvas)
        return
    def add_structures(self, base_do, ranges):
        items = []
        for range_num, range in enumerate(ranges):
            canvases = []
            for page in range.pages:
                image_number, num = page
                canvases.append({ "id" : f"{base_do}-{image_number}/canvas", "type" : "Canvas" })
            items.append({ "id" : f"{base_do}-{image_number}/range/{range_num}", "type" : "Range", "label" : { "de" : [ range.heading ] }, "items" : canvases })
        self.content["structures"] = [ {"id" : f"{base_do}range/toc", "type" : "Range", "label" : { "de" : [ "Inhaltsverzeichnis" ] }, "items" : items } ]
        return
    def serialize(self):
        self.content_json = json.dumps(self.content)
        return(self.content_json)
        
class Canvas:
    def __init__(self, ressource, height, width):
        self.res = ressource
        self.height = height
        self.width = width
        self.content = {
            "id" : self.res,
            "type" : "Canvas",
            "width" : int(self.width),            
            "height" : int(self.height),
            "items" : []
        }
    def add_page(self, page):
        self.content["items"].append(page.content)
    def add_label(self, label):
        self.content["label"] = { "en" : [label] }
    def add_thumbnail(self, ressource, format_thumb, width_thumb = None):
        if width_thumb == None:
            width_thumb = 150
        height_thumb = get_height_thumb(int(self.width), int(self.height), width_thumb)
        self.content["thumbnail"] = [ { "id" : ressource, "type" : "Image", "format" : format_thumb, "width" : width_thumb, "height" : height_thumb } ]
        
class AnnotationPage:
    def __init__(self, ressource):
        self.res = ressource
        self.content = {
            "id" : self.res,
            "type" : "AnnotationPage",
            "items" : []
        }
    def add_annotation(self, annotation):
        self.content["items"].append(annotation.content)
        
class Annotation:
    def __init__(self, ressource, image_api, target_canvas, height, width, format = None):
        if format == None:
            format = "image/jpeg"
        self.res = ressource
        ext = get_extension(format)
        self.im_res = f"{image_api}/full/max/0/default.{ext}"
        self.service = image_api
        self.content = {
            "id" : self.res,
            "type" : "Annotation",
            "motivation" : "painting",
            "body" : {
                "id" : self.im_res,
                "type" : "Image",
                "format" : format,
                "width" : int(width),                
                "height" : int(height),
                "service" : [
                    { 
                    "id" : self.service,
                    "profile" : "level1",
                    "type": "ImageService3"
                    }
                ]
            },
            "target" : target_canvas
        }

def get_extension(format):
    conc = { "image/jpeg" : "jpg", "image/jp2" : "jp2", "image/png" : "png" }
    try:
        return(conc[format])
    except:
        return("jpg")

@functools.lru_cache(maxsize=10000)        
def get_height_thumb(width_orig, height_orig, width_thumb):
    ratio = height_orig / width_orig
    height_thumb = width_thumb * ratio
    height_thumb = int(round(height_thumb))
    return(height_thumb)