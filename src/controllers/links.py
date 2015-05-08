# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di gestione dei link.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.web_resource import WebResource


#= CLASSI ======================================================================

class LinksPage(WebResource):
    """
    Controller della pagina relativi i link esterni.
    """
    TITLE = "Links"

    PAGE_TEMPLATE = string.Template(open("src/views/links.view").read())

    def render_GET(self, request, conn):
        mapping = {"game_name" : config.game_name}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
