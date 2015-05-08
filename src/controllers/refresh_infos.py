# -*- coding: utf-8 -*-

"""
Modulo per la lettura e l'invio dei messaggi sulla Piazzetta.
"""


#= IMPORT ======================================================================

import pprint

from src.config       import config
from src.color        import convert_colors
from src.log          import log
from src.utility      import is_number
from src.web_resource import WebResource

from src.controllers.square import SquarePage, create_square_message

if config.reload_commands:
    reload(__import__("src.commands.command_who", globals(), locals(), [""]))
from src.commands.command_who import get_who_players


#= CLASSI ======================================================================

class RefreshInfosPage(WebResource):
    """
    TITLE = "__refresh_infos__"

    Pagina utilizzata per aggiornare parti dinamiche comuni a tutte le pagine.
    """
    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = False

    NEW_PAGE = True

    # Il metodo GET non è supportato volutamente

    def render_POST(self, request, conn):
        if not conn:
            return ""

        response = {}
        if "refresh_who_counter" in request.args:
            who_players = get_who_players()
            if who_players:
                response["who_counter"] = len(who_players)
            else:
                response["who_counter"] = 0

        if "last_refresh_id" in request.args:
            if is_number(request.args["last_refresh_id"][0]):
                last_refresh_id = int(request.args["last_refresh_id"][0])
                if len(SquarePage.SQUARE_MESSAGES_LIST) > last_refresh_id:
                    square_line = SquarePage.SQUARE_MESSAGES_LIST[last_refresh_id]
                    if "[" in square_line:
                        square_line = convert_colors(square_line)
                    response["last_square_message"] = create_square_message(square_line, conn, last_refresh_id + 1, use_quote=True)
                else:
                    response["last_square_message"] = ""
            else:
                log.bug("last_refresh_id non è un numero: " % request.args["last_refresh_id"][0])

        return pprint.pformat(response, indent=0)
    #- Fine Metodo -
