# -*- coding: utf-8 -*-

"""
Enumerazione delle flag relativi ai libri.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class ReadableElement(EnumElement):
    def __init__(self, name, description=""):
        super(ReadableElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE    = ReadableElement("Nessuno")
NUMBERS = ReadableElement("Numbers", "Indica se far visualizzare le pagine di un libro o altro oggetto leggibile")
CENTER  = ReadableElement("Center",  "Indica di allineare l'output delle pagine in maniera centrata")
RIGHT   = ReadableElement("Right",   "Indica di allineare l'output delle pagine verso destra")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
