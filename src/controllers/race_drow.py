# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina riguardante la razza dei drow.
"""


#= IMPORT ======================================================================

import string

from src.web_resource import WebResource


#= CLASSI ======================================================================

class RaceDrowPage(WebResource):
    TITLE = "Drow"

    PAGE_TEMPLATE = string.Template(open("src/views/race_drow.view").read())

    def render_GET(self, request, conn):
        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
