# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di negozio.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class ShopElement(EnumElement):
    def __init__(self, name, description=""):
        super(ShopElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = ShopElement("Nessuno")
NORMAL    = ShopElement("Normal",       "Il negoziante normale, vende oggetti o creature")
DISPENSER = ShopElement("Distributore", "Il negoziante è in realtà un distributore, per il resto funziona come un venditore normale")
REPAIR    = ShopElement("Repair",       "Il negoziante ripara armi e armature o altri oggetti rovinati")
RECHARGE  = ShopElement("Recharge",     "Il negoziante ricarica oggetti magici scarichi")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
