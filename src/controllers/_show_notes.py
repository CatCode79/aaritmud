# -*- coding: utf-8 -*-

"""
Modulo per la pagina web che serve a visualizzare la lista di typo, bug e idea.
"""


#= IMPORT ======================================================================

import string

from src.database     import database
from src.enums        import TRUST
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ShowNotesPage(WebResource):
    """
    Visualizza una lista di typo, bug o idea a seconda del parametro GET passato.
    """
    TITLE = "Show Notes"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    def render_GET(self, request, conn):
        page = ""

        type = "bugs"
        if "type" in request.args:
            type = request.args["type"][0]

        if type != "bugs" and type != "typos" and type != "ideas":
            type = "bugs"

        self.bugs     = []
        self.typos    = []
        self.ideas    = []

        discovered = False

        page = ""
        for account in database["accounts"].itervalues():
            notices = getattr(account, type)
            if not notices:
                continue
            discovered = True
            page += '''<h3>Lista di %s di %s:</h3>''' % (type.capitalize(), account.name)
            for notice in notices:
                # (TD) in futuro dare la possibilità anche di cancellarli
                #page += '''%s <input type="submit" name="%s" id="%s" value="Delete"><br>''' % (notice.subject, id(notice), id(notice))
                page += '''%s<br>''' % notice.subject
                page += '''%s<br><br>''' % notice.text

        if not discovered:
            page += '''Nessun %s segnalato da parte dei giocatori.''' % type.capitalize()

        return page
    #- Fine Metodo -
