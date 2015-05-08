# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.log      import log
from src.database import database
from src.enums    import TO, RACE, FLAG, ENTITYPE

from src.commands.command_say import command_say
from src.commands.command_eat import command_eat


#= COSTANTI ===================================================================

TROLL_PROTO_CODE  = "accademia-drago_mob_immagine-grark"


#= FUNZIONI ===================================================================

def before_incoming(entity, from_room, direction, to_room, ragazza, running, behavioured):
    change_descr(ragazza)
#- Fine Funzione -

def before_intuited(entity, ragazza, descr, detail, behavioured):
    change_descr(ragazza)
#- Fine Funzione -

def before_looked(entity, ragazza, descr, detail, use_examine, behavioured):
    change_descr(ragazza)
#- Fine Funzione -

def change_descr(ragazza):
    if not ragazza:
        return

    troll = cerca_il_troll(ragazza.location, TROLL_PROTO_CODE)
    if not troll:
        ragazza.long = "$N appare preoccupata."
        ragazza.descr_sixth = "Ne deve aver passate di brutte esperienze..."
    else:
        ragazza.long = "$N piange disperata per le sevizie del troll"
        ragazza.descr_sixth = "#looker is SEX.MALE#Mhhhh... un'umana di un certa sua bellezza... almeno una volta tolti i vari strati  di  sudiciume....  potresti guardare senza intervenire, oppure potresti salvarla, oppure ancora potresti salvarla per vedere quanto vale la sua riconoscenza...#Mhhhh... Porre fine a questa situazione? Approfittarne? Tirar dritto?#"

def before_die(ragazza, opponent):
    troll = cerca_il_troll(ragazza.location, TROLL_PROTO_CODE)
    if troll:
        troll.long = "$N grugnisce soddisfatto"
#- Fine Funzione -

def cerca_il_troll(location, troll_proto_code):
    for en in location.iter_contains():
        if not en.IS_PLAYER and en.prototype.code == troll_proto_code:
            return en
    return None
#- Fine Funzione -
