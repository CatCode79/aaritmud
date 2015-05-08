# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di danno.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class DamageElement(EnumElement):
    def __init__(self, name, description=""):
        super(DamageElement, self).__init__(name, description)
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE      = DamageElement("Nessuno")
#UNDEFINED = DamageElement("Undefined", "Danno non ben specificato")  # (TT) non so se tenerlo o se definire sempre una tipologia valida per tutti i danni
HUNGER    = DamageElement("Hunger",    "Danno ricevuto per fame")


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)




#define WDT_HIT		0
#define WDT_SLICE		1
#define WDT_STAB		2
#define WDT_SLASH		3
#define WDT_WHIP		4
#define WDT_CLAW		5
#define WDT_BLAST		6
#define WDT_POUND		7
#define WDT_CRUSH		8
#define WDT_GREP		9
#define WDT_BITE		10
#define WDT_PIERCE		11
#define WDT_SUCTION		12
#define WDT_BEATING		13
#define WDT_DIGESTION	14
#define WDT_CHARGE		15
#define WDT_SLAP		16
#define WDT_PUNCH		17
#define WDT_WRATH		18
#define WDT_MAGIC		19
#define WDT_DIVINE_POWER	20
#define WDT_CLEAVE		21
#define WDT_SCRATCH		22
#define WDT_PECK_PIERCE	23
#define WDT_PECK_BASH	24
#define WDT_CHOP		25
#define WDT_STING		26
#define WDT_SMASH		27
#define WDT_SHOCKING_BITE	28
#define WDT_FLAMING_BITE	29
#define WDT_FREEZING_BITE	30
#define WDT_ACIDIC_BITE	31
#define WDT_CHOMP		32
#define WDT_SHOT		33
#define WDT_LIFE_DRAIN	34
#define WDT_THIRST		35
#define WDT_SLIME		36
#define WDT_THWACK		37
#define WDT_FLAME		38
#define WDT_CHILL		39
#define WDT_ELDER		40
#define WDT_SCREECH		41
