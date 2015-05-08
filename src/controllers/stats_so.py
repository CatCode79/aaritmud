# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che visualizza le statistiche relative
l'utilizzo dei sistemi operativi utilizzati dal client per giocare.
"""


#= IMPORT ======================================================================

import json
import string

from src.config       import config
from src.connection   import get_os_from_ua
from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class StatsSoPage(WebResource):
    """
    Pagina web per la visualizzazione delle stastistiche dei sistemi operativi
    utilizzati dai giocatori.
    """
    TITLE = "Statistiche Sistemi Operativi"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/stats_so.view").read())

    def render_GET(self, request, conn):
        detailed_systems = {}
        for account in database["accounts"].itervalues():
            if not account.user_agents:
                continue
            so = get_os_from_ua(account.user_agents[-1])
            if so in detailed_systems:
                detailed_systems[so] += 1
            else:
                detailed_systems[so] = 1

        general_systems = {}
        for so, use in detailed_systems.iteritems():
            if "_" in so:
                code = so.split("_")[0]
            else:
                code = so
            if code in general_systems:
                general_systems[code] += use
            else:
                general_systems[code] = use
        
        general_systems  = list(reversed(sorted(general_systems.items(), key=lambda x: x[1])))
        detailed_systems = list(reversed(sorted(detailed_systems.items(), key=lambda x: x[1])))

        mapping = {"general_systems"  : json.dumps(general_systems, separators=(',',':')),
                   "detailed_systems" : json.dumps(detailed_systems, separators=(',',':'))}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
