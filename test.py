#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import requests
logging.basicConfig(level=logging.INFO)

class Uploader():
    def __init__(self, user, password, rest_url, collection):
        with requests.Session() as s:
            resp = s.get(rest_url)
            cookie = resp.cookies.get("DSPACE-XSRF-COOKIE")
        print(cookie)
        with requests.Session() as s:
            p = s.post(rest_url + f"authn/login?user={user}&password={password}", data={ "user":user, "password":password  }, headers={ "X-XSRF-TOKEN":cookie })
        print(p)

upl = Uploader("beyer@hab.de", "admin", "http://localhost:8080/server/api/", "Digitalisierte Inkunabeln")