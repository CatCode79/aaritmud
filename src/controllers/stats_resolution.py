# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che visualizza le statistiche relative
l'utilizzo delle risoluzioni del monitor usate per visualizzare l'interfaccia
di gioco.
"""


#= IMPORT ======================================================================

import json
import string

from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class StatsResolutionPage(WebResource):
    """
    Pagina web per tutte le statistiche relative alle risoluzioni.
    """
    TITLE = "Statistiche Risoluzioni"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/stats_resolution.view").read())

    def render_GET(self, request, conn):
        resolutions = {}
        for account in database["accounts"].itervalues():
            if account.resolution_width <= 0 or account.resolution_height <= 0:
                continue
            code = "%d x %d" % (account.resolution_width, account.resolution_height)
            if code in resolutions:
                resolutions[code] += 1
            else:
                resolutions[code] = 1

        data = list(reversed(sorted(resolutions.items(), key=lambda x: x[1])))

        mapping = {"data" : json.dumps(data, separators=(',',':'))}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
