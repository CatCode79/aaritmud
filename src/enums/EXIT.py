# -*- coding: utf-8 -*-

"""
Enumerazione delle flag di uscita.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class ExitElement(EnumElement):
    def __init__(self, name, description=""):
        super(ExitElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE         = ExitElement("Nessuna")
NO_LOOK_LIST = ExitElement("NoLookList", "L'uscita non viene vista tra le altre")
NO_MOB       = ExitElement("NoMob",      "L'uscita non è praticabile dai mob")
NO_ITEM      = ExitElement("NoItem",     "L'uscita non è praticabile dagli oggetti")
NO_ROOM      = ExitElement("NoRoom",     "L'uscita non è praticabile dalle stanze")
NO_PLAYER    = ExitElement("NoPlayer",   "L'uscita non è praticabile dai giocatori, neppure da quelli che seguono un'altro tipo di entità.")
NO_FLEE      = ExitElement("NoFlee",     "Per questa uscita non si può fuggire")
DIGGABLE     = ExitElement("Diggable",   "L'uscità si rende agibile scavandovi")
PIT          = ExitElement("Pit",        "L'uscita non è agibile ed è un buco, solo con le corde si può scendervi (da non confondersi con la flag ROOM_NOFLOOR, qui il buco è solo parte del pavimento)")
# (TD) magari utilizzare invece un'etichetta con il comando da utilizzare per oltrepassarla
xCLIMB       = ExitElement("xClimb",     "Uscita scavalcabile solo tramite il comando climb")
xENTER       = ExitElement("xEnter",     "Uscita in cui si può entrare solo con il comando enter")
xLEAVE       = ExitElement("xLeave",     "Uscita che si può lasciare solo con il comando leave")
xAUTO        = ExitElement("xAuto",      "Uscita utilizzabile solo se digitata come se fosse un comando")
xSEARCH      = ExitElement("xSearch",    "Uscita che si può trovare solo se cercata esplicitamente con il comando search")
xLOOK        = ExitElement("xLook",      "Uscita che permette di guardare nell'altra stanza con il comando look")
xJUMP        = ExitElement("xJump",      "Uscita raggiungibile solo saltandovi")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
