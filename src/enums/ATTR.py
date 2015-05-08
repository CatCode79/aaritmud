# -*- coding: utf-8 -*-

"""
Enumerazione degli attributi del gioco.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class AttrElement(EnumElement):
    def __init__(self, name, description=""):
        super(AttrElement, self).__init__(name, description)
        self.attr_name = ""
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE         = AttrElement("Nessuno")
STRENGTH     = AttrElement("[red]Forza[close]",              "La forza del tuo personaggio, con essa potrai trasportare di più ed avrai maggiori punti vita ad ogni passaggio di livello.")
ENDURANCE    = AttrElement("[darkred]Resistenza[close]",     "La resistenza fisica del tuo personaggio, con essa riuscirai a resistere nelle situazioni più difficili ed avrai maggiori punti di vigore ad ogni passaggio di livello.")
AGILITY      = AttrElement("[green]Agilità[close]",          "L'agilità del tuo personaggio serve a sgusciare da situazioni pericolose o serve per utilizzare abilità particolari come lo scassinare e molte altre.")
SPEED        = AttrElement("[lightgreen]Velocità[close]",    "La velocità del tuo personaggio serve principalmente a calcolare il tempo dei turni di combattimento.")
INTELLIGENCE = AttrElement("[royalblue]Intelligenza[close]", "L'intelligenza serve per pronunciare correttamente incantesimi ed a imparare nuove abilità.")
WILLPOWER    = AttrElement("[cyan]Volontà[close]",           "La volontà è la resistenza magica e con essa avrai inoltre maggiori punti mana ad ogni passaggio di livello")
PERSONALITY  = AttrElement("[orange]Personalità[close]",     "La personalità è la capacità di presentarsi alle persone, è un misto di carisma, comando e bellezza, a seconda della situazione.")
LUCK         = AttrElement("[yellow]Fortuna[close]",         "La fortuna governa di un poco tutte le azioni che lo richiedono.")

STRENGTH.attr_name     = "strength"
ENDURANCE.attr_name    = "endurance"
AGILITY.attr_name      = "agility"
SPEED.attr_name        = "speed"
INTELLIGENCE.attr_name = "intelligence"
WILLPOWER.attr_name    = "willpower"
PERSONALITY.attr_name  = "personality"
LUCK.attr_name         = "luck"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
