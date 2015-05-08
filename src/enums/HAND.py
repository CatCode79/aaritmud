# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di mano, cioè di quale mano un'entità utilizza
piuttosto di un'altra.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class HandElement(EnumElement):
    def __init__(self, name, description=""):
        super(HandElement, self).__init__(name, description)
        self.reverse = None
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE  = HandElement("nessuna")
RIGHT = HandElement("destra",   "Destra")
LEFT  = HandElement("sinistra", "Sinistra")

RIGHT.reverse = LEFT
LEFT.reverse  = RIGHT


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
