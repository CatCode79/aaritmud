# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che visualizza le statistiche relative
l'utilizzo dei browser per connettersi tramite account.
"""


#= IMPORT ======================================================================

import json
import string

from src.connection   import get_browser_from_ua
from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class StatsBrowserPage(WebResource):
    """
    Pagina web per la visualizzazione delle stastistiche dei browser utilizzati
    dai giocatori.
    """
    TITLE = "Statistiche Browser"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/stats_browser.view").read())

    def render_GET(self, request, conn):
        detailed_browsers = {}
        for account in database["accounts"].itervalues():
            if not account.user_agents:
                continue
            code = get_browser_from_ua(account.user_agents[-1])
            if code == "???":
                code = "Altro"
            if code in detailed_browsers:
                detailed_browsers[code] += 1
            else:
                detailed_browsers[code] = 1

        general_browser = {}
        for browser, use in detailed_browsers.iteritems():
            if "_" in browser:
                code = browser.split("_")[0]
            else:
                code = browser
            if code in general_browser:
                general_browser[code] += use
            else:
                general_browser[code] = use

        general_data  = list(reversed(sorted(general_browser.items(), key=lambda x: x[1])))
        detailed_data = list(reversed(sorted(detailed_browsers.items(), key=lambda x: x[1])))

        mapping = {"general_data"  : json.dumps(general_data, separators=(',',':')),
                   "detailed_data" : json.dumps(detailed_data, separators=(',',':'))}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
