# -*- coding: utf-8 -*-

#= COMMENTI ======================================================================
# quando qualcuno dice "tutto qui sta per nutrirsi di me" viene trasferito nella
# room preposta alle coordinate 2 0 -1 dell'area conflitti


#= IMPORT ======================================================================

import re
import random

from src.defer   import defer_random_time
from src.enums   import TO
from src.room    import Destination, Room
from src.utility import is_same

#from src.scripts.essential      import defer_if_possible, get_target_implicetely


#= COSTANTI ====================================================================

ALFA_ONLY_PATTERN = re.compile("[^a-zA-Z ]+")


#= FUNZIONI ====================================================================

def after_rpg_channel(listener, speaker, target, phrase, ask, exclaim, behavioured):
    destination_room = Destination(2, 0, -1, "conflitti").get_room()
    if not destination_room:
        # Forse non è stata ancora resettato nulla alla destinazione
        return False

    phrase = ALFA_ONLY_PATTERN.sub("", phrase)
    if is_same(phrase, "tutto qui sta per nutrirsi di me"):
        speaker = speaker.from_location(1)
        speaker.to_location(destination_room, use_look=True)

    return False
#- Fine Funzione -


def after_look(entity, target, descr, detail, use_examine, behavioured):
    defer_random_time(800, 900, go_to_dt, entity, entity.location)
    return False
#- Fine Funzione -


def go_to_dt(entity, location):
    if not entity:
        return False
    if entity.location != location:
        return False

    entity.act("[red]La tua mente si perde e vieni consumat$o lentamente fino a morte![close]", TO.ENTITY)
    entity.act("Il corpo di $n si disfa!", TO.OTHERS)
    if entity.IS_PLAYER:
        entity.dies(teleport_corpse=True)
    else:
        entity.dies()
#- Fine Funzione -
