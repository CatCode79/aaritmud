# -*- coding: utf-8 -*-

"""
Enumerazione delle flag per la gestione di alcune funzioni nel modulo grammar.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class GrammarElement(EnumElement):
    def __init__(self, name, description=""):
        super(GrammarElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE           = GrammarElement("Nessuno")
MASCULINE      = GrammarElement("Maschile",        "Indica il genere maschile")
FEMININE       = GrammarElement("Femminile",       "Indica il genere femminile")
SINGULAR       = GrammarElement("Singolare",       "Indica il numero singolare")
PLURAL         = GrammarElement("Plurale",         "Indica il numero plurale plurale")
DETERMINATE    = GrammarElement("Determinato",     "Indica un articolo determinato")
INDETERMINATE  = GrammarElement("Indeterminativo", "Indica un articolo indeterminato")
POSSESSIVE     = GrammarElement("Possessivo",      "Indica un aggettivo o un pronome possessivo")
PREPOSITION_IN = GrammarElement("Preposizione In", "Indica la preposizione articolata 'in'")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
