# -*- coding: utf-8 -*-

"""
Enumerazione dei mesi di un anno rpg.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class MonthElement(EnumElement):
    def __init__(self, name, description=""):
        super(MonthElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE  = MonthElement("Nessuno")
ONE   = MonthElement("[white]Inverno del Lupo[close]",   "dell'[white]Inverno del Lupo[close]")
TWO   = MonthElement("[cyan]Gigante di Ghiaccio[close]", "del [cyan]Gigante di Ghiaccio[close]")
THREE = MonthElement("[blue]Arcano Passato[close]",      "dell'[blue]Arcano Passato[close]")
FOUR  = MonthElement("[green]Natura[close]",             "della [green]Natura[close]")
FIVE  = MonthElement("[red]Grande Lotta[close]",         "della [red]Grande Lotta[close]")
SIX   = MonthElement("[red]Dragone[close]",              "del [red]Dragone[close]")
SEVEN = MonthElement("[red]Battaglia[close]",            "della [red]Battaglia[close]")
EIGHT = MonthElement("[dimgray]Lunghe Ombre[close]",     "delle [dimgray]Lunghe Ombre[close]")
NINE  = MonthElement("[blue]Antica Oscurità[close]",     "dell'[blue]Antica Oscurità[close]")
TEN   = MonthElement("[dimgray]Grande Male[close]",      "del [dimgray]Grande Male[close]")

#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
