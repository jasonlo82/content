import unicodedata

import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

string = demisto.args()["value"]
normalized = unicodedata.normalize('NFKD', string)
res = ""
for caracter in normalized:
    if not unicodedata.combining(caracter):
        res += caracter
demisto.results(res)
