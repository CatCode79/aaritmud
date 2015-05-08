# -*- coding: utf-8 -*-

"""
Enumerazione delle statistiche.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class StatElement(EnumElement):
    def __init__(self, name, description=""):
        super(StatElement, self).__init__(name, description)
        self.attr_name = ""  # Nome dell'attributo relativo alla statistica



#-------------------------------------------------------------------------------


NONE         = StatElement("Nessuna")
STRENGTH     = StatElement("[red]Forza[close]")
ENDURANCE    = StatElement("[red]Resistenza[close]")
AGILITY      = StatElement("[green]Agilità[close]")
SPEED        = StatElement("[green]Velocità[close]")
INTELLIGENCE = StatElement("[royalblue]Intelligenza[close]")
WILLPOWER    = StatElement("[royalblue]Volontà[close]")
PERSONALITY  = StatElement("[yellow]Personalità[close]")
LUCK         = StatElement("[yellow]Fortuna[close]")

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
