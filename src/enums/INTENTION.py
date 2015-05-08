# -*- coding: utf-8 -*-

"""
Enumerazione delle intenzioni relativi ai social e alle skill.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class IntentionElement(EnumElement):
    def __init__(self, name, description=""):
        super(IntentionElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = IntentionElement("Nessuna")
AGGRESSIVE = IntentionElement("Aggressiva")
NEUTRAL    = IntentionElement("Neutrale")
FRIENDLY   = IntentionElement("Amichevole")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
