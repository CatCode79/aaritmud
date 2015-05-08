# -*- coding: utf-8 -*-

"""
Enumerazione dei tipi d'intenzioni per social e skill.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class ApplyElement(EnumElement):
    def __init__(self, name, description=""):
        super(ApplyElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = ApplyElement("Nessuno",   "Apply temporaneo")
RACE      = ApplyElement("Race",      "Apply che uno ha dalla nascita grazie alla sua razza")
WAY       = ApplyElement("Way",       "Apply che uno possiede grazia alla scelta della classe")
KNOWLEDGE = ApplyElement("Knowledge", "Apply a skill e spell e simili, mi sa che qui va bene il temporaneo, ma no.. mettiamo il nome della skill o spell che ha dato gli affect")
ROOM      = ApplyElement("Room",      "Apply donato dalla stanza in cui si trova attualmente l'entità")
MORPH     = ApplyElement("Morph",     "Apply relativo alle metamorfosi, ci saranno skill apprendibili solo dai morpher")
DISEASE   = ApplyElement("Disease",   "Apply relativo a malattie, il type qui è il nome della malattia")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
