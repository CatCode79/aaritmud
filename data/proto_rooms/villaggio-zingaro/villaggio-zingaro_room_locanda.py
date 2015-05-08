# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

"""
Inietta una bimba in locanda.
"""


#= IMPORT ======================================================================

import random

from src.database import database
from src.defer    import defer_random_time
from src.enums    import TO
from src.log      import log
from src.mob      import Mob


#= COSTANTI ====================================================================

PROTO_MOB_CODE = "villaggio-zingaro_mob_bimba-tereza"


#= FUNZIONI ====================================================================

def on_dawn(locanda):
    print "<<<<< iniezione bimba in 1,60 >>>>>>>>>"
    defer_random_time(1, 60, coming , locanda)


def coming(locanda):
    """
    Controlla non ci siano bimbe in giro e poi la inietta.
    """
    # È possibile visto che questa funzione viene deferrata
    if not locanda:
        return

    for mob in database["mobs"].itervalues():
        if mob.prototype.code == PROTO_MOB_CODE:
            return
    
    bimba = Mob(PROTO_MOB_CODE)
    bimba.inject(locanda)

    bimba.act("Entri trotterellante in $N", TO.ENTITY, locanda)
    bimba.act("$n entra trotterellando in $N.", TO.OTHERS, locanda)
    bimba.act("Ti senti calpestare dal trotterellare di $n", TO.TARGET, locanda)
#- Fine Funzione -
