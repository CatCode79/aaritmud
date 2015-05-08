# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di capelli.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class HairtypeElement(EnumElement):
    def __init__(self, name, description=""):
        super(HairtypeElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

#http://www.gamebanshee.com/fable/equipment/hair.php
NONE    = HairtypeElement("Nessuno")
BALD    = HairtypeElement("calvo")
SLEEK   = HairtypeElement("lisci")
WAVY    = HairtypeElement("mossi")  # oppure ondulati (tramite sinonimo)
CURLY   = HairtypeElement("ricci")
FRIZZY  = HairtypeElement("crespi")
RUFFLED = HairtypeElement("arruffati")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
