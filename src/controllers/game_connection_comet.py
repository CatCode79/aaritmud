# -*- coding: utf-8 -*-

"""
Modulo per la gestione della connessione al gioco con tecnologia simil-comet.
"""


#= IMPORT ======================================================================

from twisted.web.server import NOT_DONE_YET

from src.web_resource import WebResource


#= CLASSI ======================================================================

class GameConnectionCometPage(WebResource):
    """
    Controller della connessione al gioco.
    """
    TITLE = "__game_connection_comet__"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True
    PLAYER_MUST_EXIST_IN_GET   = True
    PLAYER_MUST_EXIST_IN_POST  = True

    def create_header(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_menu(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_square(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_footer(self, request, conn):
        return ""
    #- Fine Metodo -

    def render_GET(self, request, conn):
        conn.player.game_request = request

        # Si prepara la deferred relativa alla terminazione della richiesta
        conn.defer_exit_from_game = request.notifyFinish()
        # La callback normale non capita perché quando un pg chiude la pagina
        # questo evento genera un'eccezione che fa scatenare invece la errback
        # per questo sono tutte e due uguali
        conn.defer_exit_from_game.addCallback(conn.player.exit_from_game)
        conn.defer_exit_from_game.addErrback(conn.player.exit_from_game)

        conn.player.enter_in_game()
        conn.player.send_prompt()

        return NOT_DONE_YET
    #- Fine Metodo -
