# -*- coding: utf-8 -*-

"""
Enumerazione dele posizioni.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class PositionElement(EnumElement):
    def __init__(self, name, description=""):
        super(PositionElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = PositionElement("Nessuna")
DEAD      = PositionElement("[darkslategray]Mort$o[close]", "[darkslategray]è mort$O[close]")
MORTAL    = PositionElement("[darkred]Quasi mort$o[close]", "[darkred]sta morendo[close]")
INCAP     = PositionElement("[blue]Incapacitat$o[close]",   "[blue]è incapacitat$O[close]")
STUN      = PositionElement("[darkcyan]Stordit$o[close]",   "[darkcyan]è stordit$O[close]")
SLEEP     = PositionElement("[cyan]Dormi[close]",           "[cyan]sta dormendo[close]")
REST      = PositionElement("[green]Riposi[close]",         "[green]sta riposando[close]")
SIT       = PositionElement("Sedut$o",                      "è sedut$O")
KNEE      = PositionElement("[gray]Inginocchiat$o[close]",  "[gray]è inginocchiat$O[close]")
#RECUMBENT = PositionElement("[pink]Appoggiat$o[close]",     "[gray]è appoggiat$O[close]")
STAND     = PositionElement("Alzat$o",                      "è alzat$O")
SHOVE     = PositionElement("[yellow]Spingi[close]",        "[yellow]sta spingendo[close]")
DRAG      = PositionElement("[orange]Trascini[close]",      "[orange]sta trascinando[close]")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
