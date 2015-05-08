# -*- coding: utf-8 -*-

"""
Enumerazioni delle costellazioni visibili in cielo.
"""

from src.element import EnumElement, finalize_enumeration
from src.enums   import MONTH


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class ConstellationElement(EnumElement):
    def __init__(self, name, description=""):
        super(ConstellationElement, self).__init__(name, description)
        self.month = MONTH.NONE
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE       = ConstellationElement("Nessuna")
WARRIOR    = ConstellationElement("[red]Guerriero[close]",       "Bonus +10 a Forza e +10 alla Resistenza")
RITUAL     = ConstellationElement("[cyan]Rituale[close]",        "Guarisce 200 punti vita istantaneamente, utilizzabile una volta al giorno. Fa fuggire i non-morti per 30 secondi anch'essa utilizzabile una volta al giorno")
STEED      = ConstellationElement("[brown]Cavallo[close]",       "Bonus +20 alla Velocità")
SHADOW     = ConstellationElement("[darkslategray]Ombra[close]", "Invisibilità per 60 secondi, utilizzabile una volta al giorno")
TOWER      = ConstellationElement("[gray]Torre[close]",          "Apri magicamente le serrature di media complessità, utilizzabile una volta al giorno. Riflette il danno di 5 punti per colpo per 120 secondi, utilizzabile una volta al giorno.")
LOVER      = ConstellationElement("[hotpink]Amante[close]",      "Paralizza il nemico per 10 secondi al costo di 120 di Fatica, utilizzabile una volta al giorno")
THIEF      = ConstellationElement("[orange]Ladro[close]",        "Bonus +10 all'Agilità, +10 alla Velocità e +10 alla Fortuna")
MAGE       = ConstellationElement("[royalblue]Mago[close]",      "Bonus di 50 punti di Mana")
SERPENT    = ConstellationElement("[green]Serpente[close]",      "Infligge un veleno che toglie 3 punti Vita al secondo per 20 secondi, allo stesso tempo esegue un Dispel del 90% e cura dell'eventuale veleno su sé stessi, utilizzabile una volta al giorno al costo di 100 punti di Fatica.")
LADY       = ConstellationElement("[blueviolet]Regina[close]",   "Bonus +10 a Volontà e +10 alla Resistenza")
LORD       = ConstellationElement("[yellow]Re[close]",           "Rigenera 6 punti Vita al secondo per 15 secondi una volta al giorno, ha una debolezza innata al fuoco del 25%")
ATRONACH   = ConstellationElement("[orangered]At[skyblue]ro[sienna]na[royalblue]ch[close]", "Bonus di 150 di Mana iniziali, ma non è possibile rigenerarli naturalmente o riposando, solo dormendo. Inoltre si ha un bonus innato di +50 all'incantesimo di 'Assorbi Mana'")
APPRENTICE = ConstellationElement("[olive]Apprendista[close]",    "Bonus di 100 punti di Mana iniziali, debolezza del 100% al Mana")


WARRIOR.month    = MONTH.ONE
RITUAL.month     = MONTH.ONE
STEED.month      = MONTH.TWO
SHADOW.month     = MONTH.THREE
TOWER.month      = MONTH.FOUR
LOVER.month      = MONTH.FIVE
THIEF.month      = MONTH.FIVE
MAGE.month       = MONTH.SIX
SERPENT.month    = MONTH.SIX
LADY.month       = MONTH.SEVEN
LORD.month       = MONTH.EIGHT
ATRONACH.month   = MONTH.NINE
APPRENTICE.month = MONTH.TEN


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
