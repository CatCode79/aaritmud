# -*- coding: utf-8 -*-

"""
Modulo per la gestione della connessione alla pagina di gioco di output
tramite ajax, questa è la tipologia di connessione al gioco standard.
"""


#= IMPORT ======================================================================

import urllib

from src.config       import config
from src.enums        import OPTION
from src.interpret    import send_input
from src.web_resource import WebResource


#= CLASSI ======================================================================

class GameConnectionAjaxPage(WebResource):
    """
    Pagina web per inviare l'output del Mud.
    """
    TITLE = "__game_connection_ajax__"

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
        # Si salva la richiesta per utilizzarla come richiesta di gioco
        conn.player.game_request = request

        if "first" in request.args and request.args["first"][0] == "1":
            # Prepara l'entrata la giocatore
            conn.player.enter_in_game()
            conn.player.send_prompt()

        # Resetta il tempo di idling
        conn.player.idle_seconds = 0

        # Se il pg ha quittato allora termina la sessione di gioco
        if conn.stop_buffering and not conn.already_closed:
            conn.close_game_request()
            conn.already_closed = True

        buffer = conn.buffer
        conn.buffer = ""
        return buffer
    #- Fine Metodo -

    def render_POST(self, request, conn):
        input = ""
        if "input_content" in request.args:
            input = request.args["input_content"][0]

        if input:
            input = urllib.unquote(input).strip()

            if OPTION.ITALIAN in conn.account.options:
                send_input(conn.player, input, "it")
            else:
                send_input(conn.player, input, "en")
        else:
            conn.player.last_input = ""
            conn.player.send_prompt()

        return "1"
    #- Fine Metodo -
