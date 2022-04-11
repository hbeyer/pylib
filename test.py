#!/usr/bin/python3
# -*- coding: utf-8 -*-


from lib import evalpdf as ep

#ev = ep.Evaluation("source/kataloge/Reiss-208.pdf", ["processionarium", "künrath"], [("Inkunabeln", "14\d\d")])
ev = ep.EvaluationSDD("source/kataloge/Reiss-208.pdf")
ev.eval()
print(ev)

"""
import pdfplumber
import PyPDF2
import logging
logging.basicConfig(level=logging.INFO)

with pdfplumber.open("source/kataloge/Reiss-209.pdf") as pdf:
    first_page = pdf.pages[23]
    print(first_page.extract_text())
"""

# Dokumentation: https://github.com/jsvine/pdfplumber

