# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che serve a salvare i dati di
persistenza del mondo del gioco.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class SaveTheWorldPage(WebResource):
    """
    Serve a forzare un backup di tutta la cartella data.
    """
    TITLE = "Save the World"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE         = string.Template(open("src/views/save_the_world.view").read())
    not_template          = string.Template(open("src/views/save_the_world_not.view").read())
    after_submit_template = string.Template(open("src/views/save_the_world_after_submit.view").read())

    def render_GET(self, request, conn):
        if not config.save_persistence:
            mapping = {}
            return self.not_template.safe_substitute(mapping)

        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if "save_the_world" not in request.args:
            return "Errore nella richiesta di salvataggio delle persistenze. (1)"
        if request.args["save_the_world"][0] != "1":
            return "Errore nella richiesta di salvataggio delle persistenze. (2)"
        database.save()
        # (bb) non invia il messaggio perché il save è lento ed abbisognerà
        # di una NOT_READY_YET
        return "[green]Salvataggio della persistenza di tutto il gioco avvenuta con successo.[close]"
    #- Fine Metodo -
