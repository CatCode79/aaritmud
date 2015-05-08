# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di logout.
"""


#= IMPORT ======================================================================

from src.enums        import LOG
from src.log          import log
from src.web_resource import WebResource


#= CLASSI ======================================================================

class LogoutPage(WebResource):
    """
    Pagina utilizzata per eseguire il logout dall'account.
    """
    TITLE = "Logout"

    ACCOUNT_MUST_EXIST_IN_GET = True

    def render_GET(self, request, conn):
        log.conn("Logout dall'account %s" % conn.account.name)

        conn.account = None
        if conn.player:
            if conn.player.game_request:
                conn.player.game_request.finish()
            conn.player = None

        request.redirect("login.html")
        return ""
    #- Fine Metodo -
