# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di reset.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class ResetElement(EnumElement):
    def __init__(self, name, description=""):
        super(ResetElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE     = ResetElement("Nessuno")
PUT      = ResetElement("Put",      "Inserisce l'entità nella locazione voluta, se l'entità già esiste non ne inserisce una nuova")
ADD      = ResetElement("Add",      "Viene aggiunta l'entità in quella locazione")
REPLACE  = ResetElement("Replace",  "Inserisce l'entità nella locazione voluta, se l'entità già esiste viene sostituita con una nuova istanza")
REMOVE   = ResetElement("Remove",   "Rimuove un'entità in quell'area, coordinate e locazione")
BURIED   = ResetElement("Buried",   "Aggiunge un'entità sepolta nella locazione")
GROWING  = ResetElement("Planting", "Aggiunge un'entità come se fosse stato piantato nella locazione")
HIDE     = ResetElement("Hide",     "Come put, ma nasconde l'entità nel posto in cui viene resettato")
DOOR     = ResetElement("Door",     "Come put per un oggetto, ma inserisce una porta nella location relativa ad una direzione (vedere la lista degli elementi DIR)")
TRAP     = ResetElement("Trap",     "Come put per un oggetto, ma inserisce la trappola nell'oggetto stesso")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
