# -*- coding: utf-8 -*-

"""
Modulo per la gestione della connessione alla pagina di gioco di output
con browser tipo Internet Explorer che non supporato il refresh continuo
della connessione comet-like.
"""


#= IMPORT ======================================================================

import string

from twisted.web.server import NOT_DONE_YET

from src.config       import config
from src.web_resource import WebResource


#= CLASSI ======================================================================

class GameConnectionIframePage(WebResource):
    """
    Pagina web per inviare l'output del Mud.
    """
    TITLE = "__game_connection_iframe__"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True
    PLAYER_MUST_EXIST_IN_GET   = True
    PLAYER_MUST_EXIST_IN_POST  = True

    CONNECTION_IFRAME_TEMPLATE = string.Template(open("src/views/game_connection_iframe.view").read())

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
        # Si salva la richiesta per inviare in continuazione dati a questa pagina
        conn.player.game_request = request

        # Si prepara la deferred relativa alla terminazione della richiesta
        conn.defer_exit_from_game = request.notifyFinish()
        # La callback normale non capita perché quando un pg chiude la pagina
        # questo evento genera un'eccezione che fa scatenare invece la errback
        # per questo sono tutte e due uguali
        conn.defer_exit_from_game.addCallback(conn.player.exit_from_game)
        conn.defer_exit_from_game.addErrback(conn.player.exit_from_game)

        # La pagina non chiude volutamente i tag </body> e </html>
        mapping = {"game_name" : config.game_name}
        page = self.CONNECTION_IFRAME_TEMPLATE.safe_substitute(mapping)

        # Invia tramite il metodo send_output così da convertire i colori
        conn.player.send_output(page, True, False)
        conn.player.enter_in_game()
        conn.player.send_prompt()

        return NOT_DONE_YET
    #- Fine Metodo -
