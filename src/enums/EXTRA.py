# -*- coding: utf-8 -*-

"""
Enumerazione delle flag per le descrizioni extra.
(TD) possibilmente queste le abbandono integrandole nel sistema ad
oggetti-al-posto-delle-extra che ho in mente
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class ExtraElement(EnumElement):
    def __init__(self, name, description=""):
        super(ExtraElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE             = ExtraElement("Nessuna")
DAY_ONLY         = ExtraElement("DayOnly",         "La descrizione extra viene visualizza solo di giorno")
NIGHT_ONLY       = ExtraElement("NightOnly",       "La descrizione extra viene visualizza solo di notte")
READABLE         = ExtraElement("Readable",        "La descrizione extra viene mostrata ANCHE con il comando read (solo per oggetti e mob, per gli oggetti in alcuni casi è meglio creare un TypeBook)")
INSIDE_CONTAINER = ExtraElement("InsideContainer", "La descrizione è leggibile solo se il contenitore è aperto")
NO_LOOK_ACT      = ExtraElement("NoLookAct",       "La descrizione extra se chiamata con un comando sensoriale non produce messaggio alle altre persone nella stanza")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
