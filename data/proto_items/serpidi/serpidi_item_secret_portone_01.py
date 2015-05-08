# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Script che random richiude la porta al pg subito dopo che l'ha aperta


#===============================================================================

import random

from src.enums import TO, FLAG, DOOR
from src.log   import log

from src.commands.command_close import command_close


#===============================================================================

def after_opened(player, portone, reverse_target, container_only, behavioured):
    random_number = random.randint(1, 100)
    if random_number < 25: 
        player.act("[white]Stai per entrare nel quartiere generale dei Serpidi, ricordati che alcuni di loro sono molto pericolosi[close]", TO.ENTITY, portone)
        player.act("[white]State per entrare nel quartiere generale dei Serpidi[close]", TO.OTHERS, portone)
        player.act("[white]Te la ridi sotto i baffi[close]", TO.TARGET, portone)
    elif random_number > 75:
        if DOOR.CLOSED not in portone.door_type.flags:
            player.act("[white]un improvvisa quanto potente ventata richiude il portone con un fragore assordante[close]", TO.ENTITY, portone)
            player.act("[white]un improvvisa quanto potente ventata richiude il portone con un fragore assordante[close]", TO.OTHERS, portone)
            player.act("[white]Un improvvisa folata ti chiude con eccessiva violenza[close]", TO.TARGET, portone)
            portone.door_type.flags += DOOR.CLOSED

    return True
#- Fine Funzione
