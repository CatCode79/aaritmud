# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina principale della libreria.
"""


#= IMPORT ======================================================================

import string

from src.web_resource import WebResource


#= CLASSI ======================================================================

class LibraryPage(WebResource):
    """
    Pagina web riguardante la biblioteca per le risorse di Background.
    """
    TITLE = "Library"

    PAGE_TEMPLATE = string.Template(open("src/views/library.view").read())

    def render_GET(self, request, conn):
        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
