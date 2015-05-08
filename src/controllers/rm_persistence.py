# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che serve a rimuovere i dati di
persistenza del mondo del Gioco.
"""


#= IMPORT ======================================================================

import string

from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class RmPersistencePage(WebResource):
    """
    Serve a rimuovere alcune o tutte le cartelle relative alla persistenza.
    """
    TITLE = "Rm Persistence"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE         = string.Template(open("src/views/rm_persistence.view").read())
    after_submit_template = string.Template(open("src/views/rm_persistence_after_submit.view").read())

    def render_GET(self, request, conn):
        if "message" in request.args:
            folders = []
            if "rooms" in request.args:
                folders.append("rooms")
            if "mobs" in request.args:
                folders.append("mobs")
            if "items" in request.args:
                folders.append("items")
            message = request.args["message"][0]
            database.remove_area_persistence(folders, message)
            mapping = {"folders" : message}
            return self.after_submit_template.safe_substitute(mapping)

        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
