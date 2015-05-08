# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina riguardante la razza degli arial.
"""


#= IMPORT ======================================================================

import string

from src.web_resource import WebResource


#= CLASSI ======================================================================

class RaceArialPage(WebResource):
    TITLE = "Arial"

    PAGE_TEMPLATE = string.Template(open("src/views/race_arial.view").read())

    def render_GET(self, request, conn):
        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
