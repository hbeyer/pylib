#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import re
from lib import csvt
from lib import geo
from lib import pica

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

#pages = "[2] Bl., S. 79 - 154"
pages = "[52], [1] Bl., 78 S., [2] Bl., S. 79 - 154, [2] Bl., S 155 - 230, [2] Bl., S. 233 - 308 S., [2] Bl., 309 - 416, [2] Bl., S. 417 - 522, [2] Bl., S. 523 - 598, [2] Bl., S. 599 - 686, [2] Bl., S. 687 - 806, [1] Bl., S. 807 - 926, [1] Bl., S. 927 - 1014, [2] Bl., S. 1018 - 1164, [1] Bl"
test = pica.get_norm_p(pages)
print(str(test))
