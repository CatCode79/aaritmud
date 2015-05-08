# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

"""
Impedisce di raccattare oggetti non propri nel negozio.
"""


#= IMPORT ======================================================================

from src.enums import TO
from src.log   import log


#= COSTANTI ====================================================================

PROTO_MOB_CODE =  "villaggio-zingaro_mob_emporista-urf-aliyeva"


#= FUNZIONI ====================================================================

def before_get_from_location(entity, target, location, behavioured):
    if target.owner and target.owner() == entity:
        return False

    room = entity.get_in_room()
    if not room:
        log.bug("room non è stata trovata valida per %r" % entity)
        return False

    emporista = find_emporista(room)
    if not emporista:
        return False

    if emporista == entity:
        return False

    emporista.act("Ti sfoghi con i maleducati", TO.ENTITY, entity)
    emporista.act("$N non fa in tempo a raccoglier qualcosa che un occhiata dell'emporista l$O gela.", TO.OTHERS, entity)
    emporista.act("$n ti redarguisce!", TO.TARGET, entity)
    return True


def find_emporista(room):
    if not room:
        log.bug("room non è un parametro valido: %r" % room)
        return None

    for emporista in room.iter_contains():
        #print emporista.code
        if not emporista.IS_MOB:
            continue
        if emporista.prototype and emporista.prototype.code == PROTO_MOB_CODE:
            return emporista.split_entity(1)

    return None
