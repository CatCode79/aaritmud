# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Secret che si apre solo di touch di una sua extra o
# con il nome impossibile non riportato in nessun modo.


#= IMPORT ======================================================================

from src.enums      import DOOR, TO


#= COSTANTI ====================================================================

PORTA_PROTO_CODE = "opekus_item_door-decorazione-secret"


#= FUNZIONI ====================================================================

def after_touched(entity, room, descr, detail, behavioured):
    return False

def before_touched(entity, room, descr, detail, behavioured):
    if not detail:
        return False

    if not detail.IS_EXTRA:
        return False

    if "decorazione" in detail.keywords:
        porta = cerca_porta_segreta(room, PORTA_PROTO_CODE)
        if not porta:
            return False

    if not porta.is_hinged():
        return False

    if DOOR.CLOSED not in porta.door_type.flags:
        return False

    entity_message = porta.door_type.entity_open_message
    entity.act(entity_message, TO.ENTITY, porta)

    target_message = porta.door_type.target_open_message
    entity.act(target_message, TO.TARGET, porta)

    others_message = porta.door_type.others_open_message
    entity.act(others_message, TO.OTHERS, porta)

    porta.door_type.flags -= DOOR.CLOSED
    return True
#- Fine Funzione -


def cerca_porta_segreta(location, porta_proto_code):
    for en in location.iter_contains():
        if not en.IS_PLAYER and en.prototype.code == porta_proto_code:
            return en
    return None
#- Fine Funzione -
