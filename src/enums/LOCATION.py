# -*- coding: utf-8 -*-

"""
Enumerazione delle locazioni, solitamente utilizzate nel codice nelle funzioni
di ricerca delle entità.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class LocationElement(EnumElement):
    def __init__(self, name, description=""):
        super(LocationElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE = LocationElement("Nessuna")
HERE = LocationElement("Qui",    "Locazione attuale, potrebbe essere dentro un contenitore piuttosto che lo stomaco di una creatura oppure una semplice stanza")
ROOM = LocationElement("Stanza", "Stanza in cui ci si trova attualmente")
AREA = LocationElement("Area",   "Area in cui ci si trova attualmente")
MUD  = LocationElement("Mud",    "Tutto il Mud")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
