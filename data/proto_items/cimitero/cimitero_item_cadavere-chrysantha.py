# -*- coding: utf-8 -*-


#= DESCRIZIONE =================================================================

# Una delle parti della quest
# qui si tratta di provare a prendere o toccare il cadavere di chrysantha
# dentro la teca che di botto si muta in polvere

# I return True servono perché l'item al quale è collegato questo gamescript
# viene rimosso prima di essere raccolto


#= TO DO LIST ==================================================================

# cambiare la tipologia delle room per impedire al bruco d'uscire di sua sponte


#= IMPORT ======================================================================

import random
from src.database import database
from src.enums    import TO
from src.item     import Item
from src.log      import log
from src.mob      import Mob


#= COSTANTI ====================================================================

PROTO_DUST_CODE = "cimitero_item_polvere-chrysantha"

PROTO_ROOMS_CODE = ["cimitero_room_collina-d35",
                    "cimitero_room_collina-d36",
                    "cimitero_room_collina-d37",
                    "cimitero_room_collina-d38",
                    "cimitero_room_collina-d39",
                    "cimitero_room_collina-d40",
                    "cimitero_room_collina-d41",
                    "cimitero_room_collina-d42",
                    "cimitero_room_collina-d43"]

PROTO_CATERPILLAR_BEFORE_CODE = "cimitero_mob_bruco-generico-quest"
PROTO_CATERPILLAR_AFTER_CODE = "cimitero_mob_bruco-saturnia-quest.dat"


#= FUNZIONI ====================================================================

def after_touched(player, cadavere, descr, detail, behavioured):
    print ">>>>>> after touch cadavere Chrysantha <<<<<"
    return turn_to_dust(player, cadavere, cadavere.location)
#- Fine Funzione -


def before_getted(player, cadavere, location, behavioured):
    return turn_to_dust(player, cadavere, location)
#- Fine Funzione -


def turn_to_dust(player, cadavere, location):
    if not player.IS_PLAYER:
        return False

    polvere = Item(PROTO_DUST_CODE)
    polvere.inject(location)
    player.act("$N comincia a sgretolarsi fino a farsi polvere.", TO.ENTITY, cadavere)
    player.act("$N toccato da $n si decompone a vista d'occhio.", TO.OTHERS, cadavere)
    player.act("Ti sgretoli al tocco di $n!", TO.TARGET, cadavere)
    cadavere.extract(1)
    caterpillar_creation()

    return True
#- Fine Funzione -


def caterpillar_creation():
    room_code = random.choice(PROTO_ROOMS_CODE) 
    print  room_code
    injection_room = find_room(room_code)
    if not injection_room:
        log.bug("proto code room non valido: %r" % room_code)
        return

    bruco = Mob(PROTO_CATERPILLAR_BEFORE_CODE)
    bruco.inject(injection_room)
#- Fine Funzione -


def find_room(room_code):
    """
    Ricava la room dal database del mud triamte prototipo.
    """
    for room in database["rooms"].itervalues():
        if room.prototype.code == room_code:
            return room
    return None
#- Fine Funzione -
