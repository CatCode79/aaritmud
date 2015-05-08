# -*- coding: utf-8 -*-

"""
Enumerazione delle virtù.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

# http://en.wikipedia.org/wiki/Virtues_of_Ultima
class VirtueElement(EnumElement):
    def __init__(self, name, description=""):
        super(VirtueElement, self).__init__(name, description)
        self.mantra     = ""
        self.sigil      = None
#        from enums import PRINCIPLE
#        self.principles = Flags(PRINCIPLE.NONE)
#        self.dungeon    = ""
#        self.word_of_power = ""


#-------------------------------------------------------------------------------

NONE         = VirtueElement("Nessuna"                     )
HONESTY      = VirtueElement("[royalblue]Onestà[close]"    )
COMPASSION   = VirtueElement("[yellow]Compassione[close]"  )
VALOR        = VirtueElement("[red]Valore[close]"          )
JUSTICE      = VirtueElement("[green]Giustizia[close]"     )
SACRIFICE    = VirtueElement("[orange]Sacrificio[close]"   )
HONOR        = VirtueElement("[purple]Onore[close]"        )
SPIRITUALITY = VirtueElement("[white]Spiritualità[close]"  )
HUMILITY     = VirtueElement("[darkslategray]Umiltà[close]")

HONESTY.mantra      = "ahm"
COMPASSION.mantra   = "mu"
VALOR.mantra        = "ra"
JUSTICE.mantra      = "beh"
SACRIFICE.mantra    = "cah"
HONOR.mantra        = "summ"
SPIRITUALITY.mantra = "om"
HUMILITY.mantra     = "lum"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
