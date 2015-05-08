# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di help.
"""

from src.element import EnumElement, finalize_enumeration
from src.enums import TRUST


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class HelpElement(EnumElement):
    def __init__(self, name, description=""):
        super(HelpElement, self).__init__(name, description)
        self.trust = TRUST.PLAYER
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE     = HelpElement("Nessuna")
GENERIC  = HelpElement("Generico",      "Aiuto di argomento generale")
MOVEMENT = HelpElement("Movimento",     "Tipologia di aiuto relativo il movimento e all'interazione con le uscite")
CHANNEL  = HelpElement("Canali",        "Tipologia di aiuto relativo la comunicazione, rpg e non, e impostazione dei canali")
INFO     = HelpElement("Informazione",  "Tipologia di aiuto relativo i comandi che danno informazioni su qualcosa")
ITEM     = HelpElement("Oggetti",       "Tipologia di aiuto relativo ai comandi che manipolano o usano oggetti")
COMBAT   = HelpElement("Combattimento", "Tipologia di aiuto riguardante il combattimento")
GROUP    = HelpElement("Gruppo",        "Tipologia di aiuto riguardante il gruppo")
SETTING  = HelpElement("Impostazioni",  "Tipologia di aiuto relativa alle opzioni e impostazioni dell'account e del personaggio")
CLAN     = HelpElement("Clan",          "Tipologia di aiuto riguardante i clan")
STAT     = HelpElement("Statistiche",   "Tipologia di aiuto riguardante le statistiche e gli attributi del personaggio")
KIT      = HelpElement("Classi",        "Tipologia di aiuto riguardante le classi")
SKILL    = HelpElement("Abilità",       "Tipologia di aiuto riguardante le skill")
SPELL    = HelpElement("Incantesimi",   "Tipologia di aiuto riguardante gli spell")
ADMIN    = HelpElement("Admin",         "Tipologia di aiuto per gli admin")
BUILD    = HelpElement("Builder",       "Tipologia di aiuto relativa la costruzione di aree")

ADMIN.trust = TRUST.MASTER
BUILD.trust = TRUST.BUILDER


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
