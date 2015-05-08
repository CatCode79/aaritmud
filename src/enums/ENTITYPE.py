# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie degli oggetti.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class EntitypeElement(EnumElement):
    def __init__(self, name, description=""):
        super(EntitypeElement, self).__init__(name, description)
        self.icon = ""
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = EntitypeElement("Nessuna")
CONTAINER  = EntitypeElement("Contenitore")
CORPSE     = EntitypeElement("Cadavere")
DOOR       = EntitypeElement("Porta")
DRINK      = EntitypeElement("Bevanda")
FISHING    = EntitypeElement("Pesca")
FOOD       = EntitypeElement("Cibo")
FLOWER     = EntitypeElement("Fiore")
FRUIT      = EntitypeElement("Frutto")
GROUND     = EntitypeElement("Terreno")
INSTRUMENT = EntitypeElement("Strumento")
KEY        = EntitypeElement("Chiave")
KEYRING    = EntitypeElement("Portachiavi")
MENHIR     = EntitypeElement("Menhir")
MONEY      = EntitypeElement("Moneta")
PLANT      = EntitypeElement("Pianta")
PORTAL     = EntitypeElement("Portale")
READABLE   = EntitypeElement("Leggibile")
SEED       = EntitypeElement("Seme")
#SHEATH     = EntitypeElement("Fodero")
WEAR       = EntitypeElement("Abbigliamento")
WEAPON     = EntitypeElement("Arma")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
