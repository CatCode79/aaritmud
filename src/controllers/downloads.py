# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina con i file da scaricare.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.web_resource import WebResource


#= CLASSI ======================================================================

class DownloadsPage(WebResource):
    """
    Pagina web da dove scaricare file.
    """
    TITLE = "Downloads"

    PAGE_TEMPLATE = string.Template(open("src/views/downloads.view").read())

    def render_GET(self, request, conn):
        mapping = {"game_name" : config.game_name}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
