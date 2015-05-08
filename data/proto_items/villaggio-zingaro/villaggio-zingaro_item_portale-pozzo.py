# -*- coding: utf-8 -*-

#= COMMENTI ====================================================================

# Chi entra nel pozzo resta in una room per alcuni secondi poi lo script
# li fa teleportare in un altra room (fondo del pozzo)


#= IMPORT ======================================================================

import random

from src.enums import TO
from src.defer import defer
from src.room  import Destination


#= FUNZIONI ====================================================================

def after_entered(entity, portal, unused_1, unused_2, behavioured):
    defer(random.randint(5, 10), teleport, entity)


def teleport(entity):
    # Ricava la destinazione per il teletrasporto
    destination_room = Destination(-2, -1, -4, "villaggio-zingaro").get_room()
    if destination_room:
        # Invia un messaggio di teleport alle due stanze
        entity.act("\n[dodgerblue]>>>>> SPLASH! <<<<<[close]\nFai un buco nell'acqua con la malagrazia di un pachiderma!", TO.ENTITY)
        entity.act("Tu e $n state per impattare sul fondo del pozzo!", TO.OTHERS)
        entity = entity.from_location(1)
        entity.to_location(destination_room, use_look=True)
        return False

    # Nessuna destinazione o stanza trovata: forse non è stata ancora resettata?
    return False
#- Fine Funzione -
