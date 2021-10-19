#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import mets

#builder = mets.METSBuilder("ed000246", "Andreas Karlstadt, Johannes Agricola und Philipp Melanchthon an Bischof Johann von Meißen Wittenberg, 1521, 18. Juli")
builder = mets.METSBuilder("ed000181", "D. Andr. Carolstads Sermon am Lichtmeß-Tag. A. 1518. zu Wittenberg gehalten/ ex MSto., ed. Löscher, 1703", "varia/selecta")
builder.build()