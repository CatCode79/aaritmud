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

class AffectFlagElement(EnumElement):
    def __init__(self, name, description=""):
        super(AffectFlagElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = AffectFlagElement("Nessuna")
POSSESSION = AffectFlagElement("Possession", "Non serve indossare l'entità per far scattare gli affects, basta possederlo")  # (TD) da implementare
LAST_WIN   = AffectFlagElement("LastWin",    "L'ultimo affect dello stesso tipo 'uccide' gli altri che devono essere 'chiusi' prima che questo affect venga.")  # (TD) il last win è meglio che vi sia per tutti gli affect con valore di modifier assoluto
CUMULATIVE = AffectFlagElement("Cumulative", "Affect dello stesso tipo si accumulano nella durata anche se il valore utile è l'ultimo")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
