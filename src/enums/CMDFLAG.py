# -*- coding: utf-8 -*-

"""
Enumerazione delle flag di comando.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class CmdflagElement(EnumElement):
    def __init__(self, name, description=""):
        super(CmdflagElement, self).__init__(name, description)
    #- Fine Inizializzazione -

    
#-------------------------------------------------------------------------------

NONE          = CmdflagElement("Nessuna")
GDR           = CmdflagElement("Gdr",         "Relativo al gdr")
INTERACT      = CmdflagElement("Interact",    "Interagisce con il mondo interrompendo eventuali altre azioni")
POSSESS       = CmdflagElement("Possess",     "Non può essere inviato se il pg è posseduto da qualcun'altro")
TYPE_ALL      = CmdflagElement("TypeAll",     "Deve essere digitato tutto per essere utilizzato")
LOG           = CmdflagElement("Log",         "Logga l'avvenuta esecuzione del comando")
PRIVATE       = CmdflagElement("Private",     "Evita di loggare in qualsiasi maniera il comando")
NO_LAST_INPUT = CmdflagElement("NoLastInput", "Evita di salvare il comando come ultimo input inviato dal giocatore")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
