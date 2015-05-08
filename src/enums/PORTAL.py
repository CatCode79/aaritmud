# -*- coding: utf-8 -*-

"""
Enumerazione delle flag di portale.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class PortalElement(EnumElement):
    def __init__(self, name, description=""):
        super(PortalElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE             = PortalElement("Nessuna")
NO_MOB           = PortalElement("NoMob",           "Il portale non è praticabile dai mob")
NO_ITEM          = PortalElement("NoItem",          "Il portale non è praticabile dagli oggetti")
NO_ROOM          = PortalElement("NoRoom",          "Il portale non è praticabile dalle stanze")
NO_PLAYER        = PortalElement("NoPlayer",        "Il portale non è praticabile dai giocatori, neppure da quelli che seguono un'altro tipo di entità.")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
