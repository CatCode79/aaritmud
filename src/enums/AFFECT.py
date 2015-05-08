# -*- coding: utf-8 -*-

"""
Enumerazione degli effetti (o chiamati anche affezioni).
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class AffectElement(EnumElement):
    def __init__(self, name, description=""):
        super(AffectElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE         = AffectElement("Nessuno")
SELF         = AffectElement("Self")
CONTAINED_BY = AffectElement("ContainedBy")
ROOM         = AffectElement("Room")
ENTITY       = AffectElement("Entity")
ITEM         = AffectElement("Item")
ACTOR        = AffectElement("Actor")
MOB          = AffectElement("Mob")
PLAYER       = AffectElement("Player")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
