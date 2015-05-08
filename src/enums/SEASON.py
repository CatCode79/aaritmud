# -*- coding: utf-8 -*-

"""
Enumerazione delle stagioni.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class SeasonElement(EnumElement):
    def __init__(self, name="", description=""):
        super(SeasonElement, self).__init__(name, description)
        adjective = ""
    #- Fine Inizializzazione -
    pass


#-------------------------------------------------------------------------------

NONE   = SeasonElement("Nessuna")
SPRING = SeasonElement("[green]Primavera[close]", "della [green]primavera[close]")
SUMMER = SeasonElement("[yellow]Estate[close]",   "dell'[yellow]estate[close]")
AUTUMN = SeasonElement("[red]Autunno[close]",     "dell'[red]autunno[close]")
WINTER = SeasonElement("[white]Inverno[close]",   "dell'[white]inverno[close]")

SPRING.adjective = "[green]primaverile[close]"
SUMMER.adjective = "[yellow]estiva[close]"
AUTUMN.adjective = "[red]autunnale[close]"
WINTER.adjective = "[white]invernale[close]"

#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
