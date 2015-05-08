# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di comandi.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class CmdtypeElement(EnumElement):
    def __init__(self, name, description=""):
        super(CmdtypeElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE        = CmdtypeElement("Nessuno")
MOVEMENT    = CmdtypeElement("Movimento",     "Comandi relativi ai movimenti e posizioni")
CHANNEL     = CmdtypeElement("Comunicazione", "Comandi relativi ai canali di comunicazione")
INFORMATION = CmdtypeElement("Informazione",  "Comandi relativi alle informazioni generiche o dell'avventuriero")
ITEM        = CmdtypeElement("Oggetti",       "Comandi relativi alla interazione con gli oggetti")
COMBAT      = CmdtypeElement("Combattimento", "Comandi relativi al combattimento")
SKILL       = CmdtypeElement("Abilità",       "Comandi relativi alle skill")
SOCIAL      = CmdtypeElement("Sociale",       "Comandi relativi ai social")
GROUPING    = CmdtypeElement("Gruppo",        "Comandi relativi al gruppo di avventurieri")
CLAN        = CmdtypeElement("Clan",          "Comandi relativi alla gestione e informazioni del Clan")
GAMING      = CmdtypeElement("Gioco",         "Comandi relativi al gioco in generale")
SETTING     = CmdtypeElement("Impostazioni",  "Comandi relativi alla configurazione e alle opzioni di gioco")
ADMIN       = CmdtypeElement("Admin",         "Comandi d'Amministratore relativi alla interazione con i giocatori")
BUILDING    = CmdtypeElement("Costruzione",   "Comandi d'Amministratore relativi alla creazione di aree")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
