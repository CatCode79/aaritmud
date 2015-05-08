# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina dei crediti.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.web_resource import WebResource, send_audio


#= CLASSI ======================================================================

class CreditsPage(WebResource):
    """
    Pagina web riguardante i crediti del Mud.
    """
    TITLE = "Credits"

    PAGE_TEMPLATE = string.Template(open("src/views/credits.view").read())

    def render_GET(self, request, conn):
        mapping = {"credits_music" : send_audio(conn, "credits.mid"),
                   "game_name" : config.game_name}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
