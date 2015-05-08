# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagine
"""


#= IMPORT ======================================================================

from src.web_resource import EnumResource


#= CLASSI ======================================================================

class ConstellationsPage(EnumResource):
    """
    Pagina web riguardante le costellazioni.
    """
    TITLE = "Constellations"

    enum_name = "CONSTELLATION"
    h3_title = "LISTA DELLE COSTELLAZIONI DI NAKILEN"
    first_th = "Costellazione"
