#!/usr/bin/python3
# -*- coding: utf-8 -*-

import httpx
import os
import os.path as op

class RequestUnAPI:
    def __init__(self, base="http://unapi.k10plus.de/"):
        self.folder = "downloads/unapi"
        self.base = base
        self.ppn = None
        self.format = None
        self.url = None
        os.makedirs(self.folder, exist_ok=True)
    def prepare(self, ppn, format= "picaxml"):
        self.ppn = ppn
        self.format = format
        self.params = { "id": f"gvk:ppn:{ppn}", "format": format }
    def download(self):
        if not self.ppn or not self.format:
            raise ValueError("prepare() muss vor download() aufgerufen werden")
        path = op.join(self.folder, f"{self.ppn}-{self.format}.xml")
        if op.exists(path):
            return True
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base, params=self.params)
                # wirft Exception bei HTTP-Fehlern (z.B. 400)
                response.raise_for_status()
                with open(path, "wb") as f:
                    f.write(response.content)
            return True
        except httpx.HTTPStatusError as e:
            print(f"HTTP-Fehler: {e.response.status_code} für {e.request.url}")
        except httpx.RequestError as e:
            print(f"Netzwerkfehler: {e}")
        except Exception as e:
            print(f"Unbekannter Fehler: {e}")
        return False