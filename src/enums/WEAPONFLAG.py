# -*- coding: utf-8 -*-

"""
Enumerazione delle flag relative le armi.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class WeaponFlagElement(EnumElement):
    def __init__(self, name, description=""):
        super(WeaponFlagElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = WeaponFlagElement("nessuna")
ONE_HAND  = WeaponFlagElement("ad una mano")
TWO_HANDS = WeaponFlagElement("a due mani")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)

# (TD) possibile future (non hanno riferimento codose nelle risorse
# dei mud in C, sono solo da prendere come idee):
#define WEAPON_TAINTED
#define WEAPON_LIVING
#define WEAPON_SLAYER
#define WEAPON_SUCKLE
#define WEAPON_ENERVATE
#define WEAPON_ANNEALED
