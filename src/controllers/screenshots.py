# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina con gli screenshots.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ScreenshotsPage(WebResource):
    """
    Pagina web da dove scaricare file.
    """
    TITLE = "Screenshots"

    PAGE_TEMPLATE = string.Template(open("src/views/screenshots.view").read())

    def render_GET(self, request, conn):
        mapping = {"game_name" : config.game_name}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
