# -*- coding: utf-8 -*-

"""
Enumerazione delle skill.
(TD) Non mi convince la struttura enumerativa , penso che debba fare una
cartella tipo di data/socials
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class SkillElement(EnumElement):
    def __init__(self, name, description=""):
        super(SkillElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE             = SkillElement("Nessuna")
KICK             = SkillElement("calcio")
HISSING_VOICE    = SkillElement("voce tonante")
THUNDERING_VOICE = SkillElement("voce sibilante")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
