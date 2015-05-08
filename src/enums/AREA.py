# -*- coding: utf-8 -*-

"""
Enumerazione delle flag di area.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class AreaElement(EnumElement):
    def __init__(self, name, description=""):
        super(AreaElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = AreaElement("Nessuna")
RENTABLE   = AreaElement("Rentable",  "Nell'area si può rentare quittando")
DONT_LIST  = AreaElement("DontList",  "L'area non viene visualizzata nella lista delle aree")
MAZE       = AreaElement("Maze",      "L'area vienegenerata come labirinto")
WUMPUS     = AreaElement("Wumpus",    "L'area viene wumpizzata")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
