# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina con tutte le divinità.
"""


#= IMPORT ======================================================================

from src.web_resource import EnumResource


#= CLASSI ======================================================================

class VirtuesPage(EnumResource):
    """
    Pagina web riguardante le divinità.
    """
    TITLE = "Virtues"

    enum_name = "VIRTUE"
    h3_title = "LISTA DELLE VIRTÙ DI NAKILEN"
    first_th = "Virtù"
