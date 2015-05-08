# -*- coding: utf-8 -*-

"""
Enumerazione dei giorni di una settimana nel calendario del Mud.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class WeekdayElement(EnumElement):
    def __init__(self, name, description=""):
        super(WeekdayElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE  = WeekdayElement("Nessuno")
ONE   = WeekdayElement("[darkcyan]Tuono[close]",   "del [darkcyan]Tuono[close]")
TWO   = WeekdayElement("[yellow]Sole[close]",      "del [yellow]Sole[close]")
THREE = WeekdayElement("[red]Toro[close]",         "del [red]Toro[close]")
FOUR  = WeekdayElement("[dimgray]Inganno[close]",  "dell'[dimgray]Inganno[close]")
FIVE  = WeekdayElement("[white]Luna[close]",       "della [white]Luna[close]")
SIX   = WeekdayElement("[cyan]Libertà[close]",     "della [cyan]Libertà[close]")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
