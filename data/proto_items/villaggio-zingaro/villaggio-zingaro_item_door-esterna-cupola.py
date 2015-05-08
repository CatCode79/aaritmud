# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.enums import TO, DOOR
from src.log   import log


#= FUNZIONI ====================================================================

def before_opened(entity, target, reverse_target, container_only, behavioured):
    if not entity.IS_PLAYER:
        return True

    if not target.door_type.key_code:
        log.bug("Nessuna chiave per la door : %r" % target)
        return True

    key = target.door_type.key_code

    for generic_item in entity.iter_contains():
        if generic_item.prototype.code == target.door_type.key_code:
            unguento = generic_item
            return False
    #entity.act("Vorresti aprire ma ti serve %s " % key, TO.ENTITY)
    entity.act("Mentre tenti il gesto, gli aculei spinosi si protendono verso te facendoti desistere!", TO.ENTITY)
    return True
