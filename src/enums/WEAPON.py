# -*- coding: utf-8 -*-

"""
Enumerazione delle categorie delle armi.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class WeaponElement(EnumElement):
    def __init__(self, name, description=""):
        super(WeaponElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE           = WeaponElement("Nessuna")
KNIFE          = WeaponElement("Coltello")
DIRK           = WeaponElement("Pugnale")
DAGGER         = WeaponElement("Daga")
SHORTSWORD     = WeaponElement("Spada Corta")
SWORD          = WeaponElement("Spada")
LONGSWORD      = WeaponElement("Spada Lunga")
BASTARD        = WeaponElement("Bastarda")
FALCHION       = WeaponElement("Falchion")
SCIMITAR       = WeaponElement("Scimitarra")
SICKLE         = WeaponElement("Falce")
KATANA         = WeaponElement("Katana")

KNUCKLE_DUSTER = WeaponElement("Pugno di Ferro")
AXE            = WeaponElement("Ascia")
BATTLEAXE      = WeaponElement("Ascia da Battaglia")
MACE           = WeaponElement("Mazza")
HAMMER         = WeaponElement("Martello")
STAFF          = WeaponElement("Bastone")
FLAIL          = WeaponElement("Flagello")
WHIP           = WeaponElement("Frusta")
EXOTIC         = WeaponElement("Esotica")

SPEAR          = WeaponElement("Lancia")
JAVELIN        = WeaponElement("Giavellotto")
PIKE           = WeaponElement("Picca")
POLEARM        = WeaponElement("Alabarda")
KNIGHT_LANCE   = WeaponElement("Lancia da Cavaliere")

SLING          = WeaponElement("Fionda")
LEATHER_STRAP  = WeaponElement("Cinghia da Lancio")
SHORTBOW       = WeaponElement("Arco Corto")
BOW            = WeaponElement("Arco")
LONGBOW        = WeaponElement("Arco Lungo")
COMPOSITEBOW   = WeaponElement("Arco Composito")
CROSSBOW       = WeaponElement("Balestra")
HEAVYCROSSBOW  = WeaponElement("Balestra Pesante")
BOLA           = WeaponElement("Bola")
SHURIKEN       = WeaponElement("Shuriken")

GUN            = WeaponElement("Fucile")
HANDGUN        = WeaponElement("Pistola")

#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
