# -*- coding: utf-8 -*-

"""
Enumerazione delle flag relative alle flag dei vestiti.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class WearElement(EnumElement):
    def __init__(self, name, description=""):
        super(WearElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = WearElement("nessuna")
LAYERABLE  = WearElement("Layerable", "Indumento collocabile in uno slot già occupato")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
