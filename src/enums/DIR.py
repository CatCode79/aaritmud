# -*- coding: utf-8 -*-

"""
Enumerazione delle direzioni.
DIR_SOMEWHERE e DIR_PORTAL non esistono, vengono gestite tramite scripts.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class DirElement(EnumElement):
    def __init__(self, name, description=""):
        super(DirElement, self).__init__(name, description)
        self.english          = ""
        self.name_nocolor     = ""
        self.english_nocolor  = ""
        self.name_for_look    = ""
        self.english_for_look = ""
        self.from_dir         = ""
        self.to_dir           = ""
        self.to_dir2          = ""
        self.reverse_dir      = None
        self.shift            = (0, 0, 0)
        self.trigger_suffix   = ""
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = DirElement("Nessuna")
NORTH     = DirElement("[darkcyan]Nord[close]")
NORTHEAST = DirElement("[lightgreen]Nordest[close]")
EAST      = DirElement("[yellow]Est[close]")
SOUTHEAST = DirElement("[lightblue]Sudest[close]")
SOUTH     = DirElement("[white]Sud[close]")
SOUTHWEST = DirElement("[darkgreen]Sudovest[close]")
WEST      = DirElement("[red]Ovest[close]")
NORTHWEST = DirElement("[blue]Nordovest[close]")
UP        = DirElement("[cyan]Alto[close]")
DOWN      = DirElement("[brown]Basso[close]")

# La traduzione inglese delle direzioni, per coloro che utilizzano i comandi in inglese
NORTH.english     = "[darkcyan]North[close]"
NORTHEAST.english = "[lightgreen]Northeast[close]"
EAST.english      = "[yellow]East[close]"
SOUTHEAST.english = "[lightblue]Southeast[close]"
SOUTH.english     = "[white]South[close]"
SOUTHWEST.english = "[darkgreen]Southwest[close]"
WEST.english      = "[red]West[close]"
NORTHWEST.english = "[blue]Northwest[close]"
UP.english        = "[cyan]Up[close]"
DOWN.english      = "[brown]Down[close]"

# Versione delle direzioni italiane ed inglesi senza colori per velocizzare
# la clean_string in alcuni punti
NORTH.name_nocolor     = "Nord"
NORTHEAST.name_nocolor = "Nordest"
EAST.name_nocolor      = "Est"
SOUTHEAST.name_nocolor = "Sudest"
SOUTH.name_nocolor     = "Sud"
SOUTHWEST.name_nocolor = "Sudovest"
WEST.name_nocolor      = "Ovest"
NORTHWEST.name_nocolor = "Nordovest"
UP.name_nocolor        = "Alto"
DOWN.name_nocolor      = "Basso"

NORTH.english_nocolor     = "North"
NORTHEAST.english_nocolor = "Northeast"
EAST.english_nocolor      = "East"
SOUTHEAST.english_nocolor = "Southeast"
SOUTH.english_nocolor     = "South"
SOUTHWEST.english_nocolor = "Southwest"
WEST.english_nocolor      = "West"
NORTHWEST.english_nocolor = "Northwest"
UP.english_nocolor        = "Up"
DOWN.english_nocolor      = "Down"


# Nome italiano ed inglese della direzione con la maiuscola in mezzo alle
# direzioni diagonali per suggerire il pg ad utilizzare i comandi diagonali
# contratti
NORTH.name_for_look     = "[darkcyan]Nord[close]"
NORTHEAST.name_for_look = "[lightgreen]NordEst[close]"
EAST.name_for_look      = "[yellow]Est[close]"
SOUTHEAST.name_for_look = "[lightblue]SudEst[close]"
SOUTH.name_for_look     = "[white]Sud[close]"
SOUTHWEST.name_for_look = "[darkgreen]SudOvest[close]"
WEST.name_for_look      = "[red]Ovest[close]"
NORTHWEST.name_for_look = "[blue]NordOvest[close]"
UP.name_for_look        = "[cyan]Alto[close]"
DOWN.name_for_look      = "[brown]Basso[close]"

NORTH.english_for_look     = "[darkcyan]North[close]"
NORTHEAST.english_for_look = "[lightgreen]NorthEast[close]"
EAST.english_for_look      = "[yellow]East[close]"
SOUTHEAST.english_for_look = "[lightblue]SouthEast[close]"
SOUTH.english_for_look     = "[white]South[close]"
SOUTHWEST.english_for_look = "[darkgreen]SouthWest[close]"
WEST.english_for_look      = "[red]West[close]"
NORTHWEST.english_for_look = "[blue]NorthWest[close]"
UP.english_for_look        = "[cyan]Up[close]"
DOWN.english_for_look      = "[brown]Down[close]"


# Quello che si legge quando un'entità arriva da una direzione
NORTH.from_dir     = "da [darkcyan]nord[close]"
NORTHEAST.from_dir = "da [lightgreen]nordest[close]"
EAST.from_dir      = "da [yellow]est[close]"
SOUTHEAST.from_dir = "da [lightblue]sudest[close]"
SOUTH.from_dir     = "da [white]sud[close]"
SOUTHWEST.from_dir = "da [darkgreen]sudovest[close]"
WEST.from_dir      = "da [red]ovest[close]"
NORTHWEST.from_dir = "da [blue]nordovest[close]"
UP.from_dir        = "dall'[cyan]alto[close]"
DOWN.from_dir      = "dal [brown]basso[close]"

# Quello che si legge quando un'entità va' verso una direzione
NORTH.to_dir     = "verso [darkcyan]nord[close]"
NORTHEAST.to_dir = "verso [lightgreen]nordest[close]"
EAST.to_dir      = "verso [yellow]est[close]"
SOUTHEAST.to_dir = "verso [lightblue]sudest[close]"
SOUTH.to_dir     = "verso [white]sud[close]"
SOUTHWEST.to_dir = "verso [darkgreen]sudovest[close]"
WEST.to_dir      = "verso [red]ovest[close]"
NORTHWEST.to_dir = "verso [blue]nordovest[close]"
UP.to_dir        = "verso l'[cyan]alto[close]"
DOWN.to_dir      = "verso il [brown]basso[close]"

# Alternativa descrittiva verso una direzione
NORTH.to_dir2     = "a [darkcyan]nord[close]"
NORTHEAST.to_dir2 = "a [lightgreen]nordest[close]"
EAST.to_dir2      = "a [yellow]est[close]"
SOUTHEAST.to_dir2 = "a [lightblue]sudest[close]"
SOUTH.to_dir2     = "a [white]sud[close]"
SOUTHWEST.to_dir2 = "a [darkgreen]sudovest[close]"
WEST.to_dir2      = "a [red]ovest[close]"
NORTHWEST.to_dir2 = "a [blue]nordovest[close]"
UP.to_dir2        = "in [cyan]alto[close]"
DOWN.to_dir2      = "in [brown]basso[close]"

# Le rispettive direzioni inverse
NORTH.reverse_dir     = SOUTH
NORTHEAST.reverse_dir = SOUTHWEST
EAST.reverse_dir      = WEST
SOUTHEAST.reverse_dir = NORTHWEST
SOUTH.reverse_dir     = NORTH
SOUTHWEST.reverse_dir = NORTHEAST
WEST.reverse_dir      = EAST
NORTHWEST.reverse_dir = SOUTHEAST
UP.reverse_dir        = DOWN
DOWN.reverse_dir      = UP

# Spostamento nella griglia delle coordinate (x, y, z) in quella direzione
NORTH.shift      = ( 0,  1,  0)
NORTHEAST.shift  = ( 1,  1,  0)
EAST.shift       = ( 1,  0,  0)
SOUTHEAST.shift  = ( 1, -1,  0)
SOUTH.shift      = ( 0, -1,  0)
SOUTHWEST.shift  = (-1, -1,  0)
WEST.shift       = (-1,  0,  0)
NORTHWEST.shift  = (-1,  1,  0)
UP.shift         = ( 0,  0,  1)
DOWN.shift       = ( 0,  0, -1)

NORTH.trigger_suffix     = "north"
NORTHEAST.trigger_suffix = "northeast"
EAST.trigger_suffix      = "east"
SOUTHEAST.trigger_suffix = "southeast"
SOUTH.trigger_suffix     = "south"
SOUTHWEST.trigger_suffix = "southwest"
WEST.trigger_suffix      = "west"
NORTHWEST.trigger_suffix = "northwest"
UP.trigger_suffix        = "up"
DOWN.trigger_suffix      = "down"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
