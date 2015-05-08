# -*- coding: utf-8 -*-

# 3 10 -2 serpidi

#= IMPORT ======================================================================

import random

from src.defer    import defer
from src.database import database
from src.enums    import TO
from src.item     import Item
from src.mob      import Mob


#= COSTANTI ====================================================================

PROTO_ITEM_CODE = "serpidi_item_ritorno_88"


#= FUNZIONI ====================================================================

def before_readed(entity, target, output, extra, behavioured):
    if not target.location or not target.location.IS_PLAYER:
        entity.act("Non hai la pergamena a tua disposizione!", TO.ENTITY)
        return True

    entity.act("$n distende la pergamena e prova a leggerla a voce alta!", TO.OTHERS, target)
#- Fine Funzione -


def find_room(PROTO_ROOM_CODE):
    # Ricava la room dal database del mud triamte prototipo.
    for room in database["rooms"].itervalues():
        if room.prototype.code == PROTO_ROOM_CODE:
            return room

    return None
#- Fine Funzione -


def after_readed(entity, target, output, extra, behavioured):
    defer(2, character_teleports, entity, target)
#- Fine Funzione -


def send_sentence():
    xxx = 1
#- Fine Funzione -


def character_teleports(player, target):
    #pergamena = Item(PROTO_ITEM_CODE)

    # Ora rimuovo il lettore della pergamena
    player.act("Ti senti trasportare da un'altra parte!", TO.ENTITY)
    player.act("$n sparisce risucchiato da qualche altra parte!", TO.OTHERS)
    player = player.from_location(player.quantity)

    # Lo sbatto nella room che più mi piace
    ROOM_CODE = "opekus_room_periferia_03"
    location = find_room(ROOM_CODE)
    if not location:
        # Se non trova la room stampa a schermo il messaggio e poi esce dallo script
        print "******* sticazzi, no location found: ", ROOM_CODE
        return

    player.to_location(location, use_look=True)
    #defer(4, send_sentence)
    #rimuovo la pergamena
    target.extract(1)
    #target.from_location(target.quantity)
#- Fine Funzione -
