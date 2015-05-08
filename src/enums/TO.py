# -*- coding: utf-8 -*-

"""
Enumerazione riguardante gli obiettivi della funzione act.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class ToElement(EnumElement):
    def __init__(self, name, description=""):
        super(ToElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE     = ToElement("Nessuno")
ENTITY   = ToElement("Entity", "Il messaggio di act viene inviato alla entità soggetto")
TARGET   = ToElement("Target", "Il messaggio di act viene inviato al bersaglio dell'azione")
OTHERS   = ToElement("Others", "Il messaggio di act viene inviato a tutti tranne all'entità soggetto")
ADMINS   = ToElement("Admins", "Il messaggio di act viene inviato a tutti gli amministratori nella stanza, tranne il soggetto")
AREA     = ToElement("Area",   "Il messaggio di act viene inviato a tutti nell'area tranne l'entità soggetto")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
