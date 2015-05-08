# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# 2 7 -2 serpidi
# Questo script non permette ad un player di andare verso una direzione se non
# ha un permesso speciale di Chadyne oppure non uccide il mob di guardia


#= IMPORT ======================================================================

from src.database import database
from src.enums    import TO
from src.mob      import Mob
from src.room     import Room

from src.commands.command_say import command_say


#= COSTANTI ====================================================================

SERPIDE_NERO_PROTO_CODE = "serpidi_mob_serpidenero_36"


#= FUNZIONI ====================================================================

def before_west(entity, from_room, direction, to_room, running, behavioured):
    num_players = 0
    serpide_nero = None
    for contenuto in from_room.iter_contains():
        if contenuto.IS_MOB:
            if contenuto.code.split("#")[0] == SERPIDE_NERO_PROTO_CODE:
                serpide_nero = contenuto.split_entity(1)
        elif contenuto.IS_PLAYER:
            num_players += 1

    if serpide_nero:
        if num_players == 1:
            to_say = "Ehi! Non ti è concesso passare da qui!"
        else:
            to_say = "Per andare verso questa direzione ci vuole un permesso speciale che non avrai mai!!!"
        command_say(serpide_nero, to_say)
        return True
#- Fine Funzione -
