# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Oggetto catasta dal quale si estraggono oggetti random mentre si tenta
# di raccoglierlo.


#= IMPORT ======================================================================

import random

from src.database import database
from src.defer    import defer
from src.enums    import PART, TO
from src.log      import log
from src.item     import Item
from src.part     import check_if_part_is_already_weared, get_part_descriptions

from src.commands.command_get import command_get
from src.entitypes.wear       import send_wear_messages


#= COSTANTI ====================================================================

PROTO_PROFUMO_CODE = "villaggio-zingaro_item_alone-premio-cupola"
PROFUMO_PROTO = database["proto_items"][PROTO_PROFUMO_CODE]


#= FUNZIONI ====================================================================

def after_touch(entity, target, descr, detail, behavioured):
    if not entity.IS_PLAYER:
        return False

    if target.weight < 200:
        entity.act("$n pigia al pompetta di $N ma a vuoto.", TO.OTHERS, target)
        entity.act("Pigi la pompetta di $N ma a vuoto.", TO.ENTITY, target)
        return False
    else:
        target.weight = target.weight - PROFUMO_PROTO.weight

    for mode in PROFUMO_PROTO.wear_type.modes:
        for part in mode:
            already_weared_part, already_weared_possession = check_if_part_is_already_weared(entity, part)
            if already_weared_part:
                entity.act("[plum]$N si dissolve immediatamente nell'aria.[close]", TO.ENTITY, PROFUMO_PROTO)
                entity.act("[plum]$N si dissolve immediatamente nell'aria.[close]", TO.OTHERS, PROFUMO_PROTO)
                return

            profumo = Item(PROTO_PROFUMO_CODE)
            profumo.inject(entity)

            profumo.wear_mode += part
            part_descriptions = get_part_descriptions(mode, "wear")

            send_wear_messages(entity, profumo, "Indossi", "indossa", part_descriptions)
            break

    defer(10, profumo_cleaning, profumo, entity)
#- Fine Funzione -


def profumo_cleaning(profumo, entity):
    # Può essere normale poiché vengono inseriti dentro una defer
    if not profumo or not entity:
        return

    if entity:
        entity.act("[plum]$N improvvisamente si dissolve.[close]", TO.OTHERS, profumo)
        entity.act("[plum]$N improvvisamente si dissolve.[close]", TO.ENTITY, profumo)
    profumo.extract(1)
#- Fine Funzione -
