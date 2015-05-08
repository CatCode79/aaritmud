# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Inserisce un'exit in direzione random. 
# Con direction non prende la direzione, solo inserendola direttamente funziona


#= IMPORT ======================================================================

import random

from src.defer import defer_random_time
from src.room  import Room, Destination, Exit
from src.enums import TO, DIR


#= COSTANTI ====================================================================

LIST_DIR_ONE = [DIR.SOUTH, DIR.NORTHEAST, DIR.EAST, DIR.SOUTHWEST]
LIST_DIR_TWO = [DIR.NORTH, DIR.SOUTHEAST, DIR.WEST, DIR.NORTHWEST]


#= FUNZIONI ====================================================================

def on_dawn(room):
    defer_random_time(10, 500, direction_choice, LIST_DIR_ONE, room)
    defer_random_time(300, 800, direction_choice, LIST_DIR_TWO, room)
#- Fine Funzione -


def direction_choice(list_direction, room):
    # Normale che possa accadere visto che la funzione è una deferred
    if not room:
        return

    direction = random.choice(list_direction)
    print "DIREZIONE = ", direction
    if direction in room.exits:
        return

    exit = Exit(direction)
    room.exits[direction] = exit
    room.act("\n[plum]Un bocciolo si è appena schiuso[close]")    
    defer_random_time(700, 1200, direction_close, direction, room)
#- Fine Funzione -


def direction_close(direction, room):
    # Normale che possa accadere visto che la funzione è una deferred
    if not room:
        return

    if direction not in room.exits:
        return

    del room.exits[direction]
    room.act("\n[indianred]Un fiore dissecca, si stacca e vola verso il basso[close].")
#- Fine Funzione -
