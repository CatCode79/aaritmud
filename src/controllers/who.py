# -*- coding: utf-8 -*-

"""
Modulo per la pagina relativa alla visualizzazione di tutti i giocatori
attualmente online in Aarit.
"""


#= IMPORT ======================================================================

from src.log          import log
from src.web_resource import WebResource

from src.commands.command_who import create_who_interface


#= CLASSI ======================================================================

class WhoPage(WebResource):
    TITLE = "Who"

    def render_GET(self, request, conn):
        page = "<center><h3>CHI STA GIOCANDO?</h3></center>"
        page += create_who_interface(conn) + "<br>"
        return  page
    #- Fine Metodo -
