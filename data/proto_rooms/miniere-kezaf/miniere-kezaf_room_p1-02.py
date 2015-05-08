# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Scavando crea una nuova room e la collega


#= IMPORT ======================================================================

import random

from src.color    import remove_colors
from src.database import database
from src.defer    import defer_random_time
from src.enums    import TO, DIR
from src.log      import log
from src.room     import Room, Destination, Exit


#= COSTANTI ====================================================================

PROTO_ROOMS_TEMPORARY_CODES = ["miniere-kezaf_room_generic-diggable-01",
                               "miniere-kezaf_room_generic-diggable-02",
                               "miniere-kezaf_room_generic-diggable-03",
                               "miniere-kezaf_room_generic-diggable-04",
                               "miniere-kezaf_room_generic-diggable-05",
                               "miniere-kezaf_room_generic-diggable-06",
                               "miniere-kezaf_room_generic-diggable-07",
                               "miniere-kezaf_room_generic-diggable-08",
                               "miniere-kezaf_room_generic-diggable-09",
                               "miniere-kezaf_room_generic-diggable-10"]

PROTO_ROOMS_STABLE_CODES = ["miniere-kezaf_room_generic-diggable-01-after",
                            "miniere-kezaf_room_generic-diggable-02-after",
                            "miniere-kezaf_room_generic-diggable-03-after",
                            "miniere-kezaf_room_generic-diggable-04-after",
                            "miniere-kezaf_room_generic-diggable-05-after",
                            "miniere-kezaf_room_generic-diggable-06-after",
                            "miniere-kezaf_room_generic-diggable-07-after",
                            "miniere-kezaf_room_generic-diggable-08-after",
                            "miniere-kezaf_room_generic-diggable-09-after",
                            "miniere-kezaf_room_generic-diggable-10-after"]


#= FUNZIONI ====================================================================

def before_dig(entity, location, target, dir, behavioured):
    if not dir or dir == DIR.NONE:
       log.bug("none dir dig: %s" % dir)
       return

    # Impedisco di andare up come scavo
    if dir == DIR.UP:
        return

    # get_destination_room ritorna None se non vi è nessuna coordinata
    # valida in quella direzione
    dig_dest = location.get_destination_room(dir)
    if dig_dest:
       #log.bug("il get_destination nella dir specificata è: %s" % dig_dest)
       return

    new_room = Room(random.choice(PROTO_ROOMS_TEMPORARY_CODES))
    coords = "%d %d %d" % (location.x + dir.shift[0], location.y + dir.shift[1], location.z + dir.shift[2])
    new_room.to_area(database["areas"]["miniere-kezaf"], coords)
    defer_random_time(30, 60, descr_modify, new_room)

    # Crea la nuova uscita da zero
    exit = Exit(dir)
    location.exits[dir] = exit
    destination = Destination(location.x + dir.shift[0], location.y + dir.shift[1], location.z + dir.shift[2], "miniere-kezaf")
    if destination:
        exit.destination = destination

    reverse_exit = Exit(dir.reverse_dir)
    new_room.exits[dir.reverse_dir] = reverse_exit
    current_location = Destination(location.x, location.y, location.z, "miniere-kezaf")
    if current_location:
        reverse_exit.destination = current_location

    entity.act("\nSei riuscit$o a procedere per un certo tratto.\n", TO.ENTITY)
    entity.act("\n$n ha scavato per un certo tratto.\n", TO.OTHERS)
    return True
#- Fine Funzione -


def descr_modify(room):
    # Normale visto che la funzione è deferrata
    if not room:
        return

    proto_room_code = random.choice(PROTO_ROOMS_STABLE_CODES)
    if not proto_room_code in database["proto_rooms"]:
        log.bug("nessuna proto room: %s" % proto_room)
        return

    proto_room = database["proto_rooms"][proto_room_code]
    room.descr = proto_room.descr
#- Fine Funzione -
