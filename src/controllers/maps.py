# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina per la visualizzazione delle wild.
"""

#= IMPORT ======================================================================

import string

from src.web_resource import WebResource


#= CLASSI ======================================================================

class MapsPage(WebResource):
    """
    Pagina web riguardante le mappe e le wilderness del Mud.
    """
    TITLE = "Maps"

    PAGE_TEMPLATE = string.Template(open("src/views/maps.view").read())

    def render_GET(self, request, conn):
        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
