# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# death trap prototipo disabilitata e sostituita ora dalla flag ROOM.DEATH_TRAP


#= IMPORT ======================================================================

from src.enums import TO, DIR


#= FUNZIONI ====================================================================

def dummy_after_move(entity, from_room, direction, to_room, running, behavioured): 
    entity.act("Sei mort$o nelle paludi", TO.ENTITY)
    entity.act("$n è morto nelle paludi", TO.OTHERS)
    entity.life = 0
#- Fine Funzione -
