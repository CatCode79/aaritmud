# -*- coding: utf-8 -*-

"""
Enumerazioni della sessualità.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class SexElement(EnumElement):
    def __init__(self, name, description=""):
        super(SexElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE    = SexElement("Nessuno")
MALE    = SexElement("[royalblue]Maschile[close]", "[royalblue]Maschio[close]")
FEMALE  = SexElement("[deeppink]Femminile[close]", "[deeppink]Femmina[close]")
NEUTRAL = SexElement("Neutrale",                   "Neutrale")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
