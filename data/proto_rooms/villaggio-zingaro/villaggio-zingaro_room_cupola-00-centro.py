# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.defer import defer
from src.enums import TO, FLAG
from src.item  import Item


#= COSTANTI ====================================================================

oggetti = {"chiave" : "villaggio-zingaro_item_chiave-premio-cupola"}


#= FUNZIONI ====================================================================

def after_move(entity, from_room, direction, to_room, running, behavioured):
    if not entity.IS_PLAYER:
        return 

    for content in to_room.iter_contains():
        if content.IS_PLAYER:
             continue
        if content.prototype.code == oggetti["chiave"]:
             return

    chiave = Item(oggetti["chiave"])
    chiave.inject(to_room)

    defer(3, ambience_act_1, to_room)
    defer(5, ambience_act_2, to_room, chiave)


def ambience_act_1(to_room):
    # Può essere normale visto che la funzione viene deferrata
    if not to_room:
        return
    to_room.act("\n[mediumturquoise]Improvvisamente la gemma centrale si illumia e comincia a pulsare[close]...")
    to_room.act("\n[mediumturquoise]Alcune gocce perlacee scivolano sulla sua superficie cadendo a terra[close].")


def ambience_act_2(to_room, chiave):
    # Può essere normale visto che la funzione viene deferrata
    if not to_room or not chiave:
        return
    to_room.act("\n[darkorange]Pochi istanti dopo, lì dove erano cadute le gocce, una piccola chiave emerge dal terreno[close]...")
    chiave.flags -= FLAG.NO_LOOK_LIST
