# -*- coding: utf-8 -*-

"""
Enumerazione degli stili di combattimento.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class StyleElement(EnumElement):
    def __init__(self, name, description=""):
        super(StyleElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = StyleElement("Nessuno")
QUICK      = StyleElement("[yellow]Veloce[close]",     "Sei pronto a combattere contro nemici veloci")
DEFENSIVE  = StyleElement("[green]Difensivo[close]",   "Così ti difenderai dai colpi avversari")
NORMAL     = StyleElement("Normale",                   "Non hai nessun stile di combattimento")
AGGRESSIVE = StyleElement("[red]Aggressivo[close]",    "Hai intenzione di picchiare duramente il nemico")
HEAVY      = StyleElement("[royalblue]Pesante[close]", "Sei pronto a combattere contro nemici grossi")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
