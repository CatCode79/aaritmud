# -*- coding: utf-8 -*-

"""
Modulo per tutto quello che viene posizionato sotto il menù a sinistra.
"""


#= IMPORT ======================================================================

import string

from src.log          import log
from src.web_resource import WebResource


#= COSTANTI ====================================================================

ADDITIONAL_HEADER = """<meta name="robots" content="noindex" />"""


#= CLASSI ======================================================================

class BelowMenuPage(WebResource):
    """
    Pagina utilizzata per gestire tutto ciò che si trova sotto il menù del sito.
    """
    TITLE = "Below Menù"

    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = True

    PAGE_TEMPLATE = string.Template(open("src/views/below_menu.view").read())

    NEW_PAGE = True

    def create_additional_header(self, request, conn):
        return ADDITIONAL_HEADER
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
        mapping = {}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        pass
        return ""
    #- Fine Metodo -
