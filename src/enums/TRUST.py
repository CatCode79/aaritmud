# -*- coding: utf-8 -*-

"""
Enumerazione relativa alla tipologie di fiducia.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class TrustElement(EnumElement):
    def __init__(self, name, description=""):
        super(TrustElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE        = TrustElement("Nessuna")
PLAYER      = TrustElement("Giocatore",               "Fiducia concessa ai normali giocatori")
MASTER      = TrustElement("[yellow]Master[close]",   "Questa fiducia concede i comandi avanzati per gestire le quest e il GDR")
BUILDER     = TrustElement("[green]Builder[close]",   "Questa fiducia concede i comandi per creare entità delle aree")
IMPLEMENTOR = TrustElement("[red]Implementor[close]", "Questa fiducia dà pieni poteri su tutti i comandi del Mud")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
