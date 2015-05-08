# -*- coding: utf-8 -*-

"""
Enumerazione delle parti del corpo.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class PartFlagElement(EnumElement):
    def __init__(self, name, description=""):
        super(PartFlagElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE          = PartFlagElement("Nessuna")
LEFT          = PartFlagElement("Sinistra",    "Una parte del corpo simmetrica che si trova a sinistra")
RIGHT         = PartFlagElement("Destra",      "Una parte del corpo simmetrica che si trova a destra")
INTERNAL      = PartFlagElement("Internal",    "Serve alle parti del corpo relative agli organi interni")
NO_EQUIP_LIST = PartFlagElement("NoEquipList", "Serve a non visualizzare nella lista di equip alcune parti del corpo speciali, come l'hold e il wield")
# La mancanza delle flag left o right significa che la parte si trova al centro


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
