# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.log      import log
from src.database import database
from src.enums    import TO, RACE, FLAG, ENTITYPE

from src.commands.command_say import command_say
from src.commands.command_eat import command_eat


#= COSTANTI ===================================================================

RAGAZZA_PROTO_CODE  = "accademia-drago_mob_ragazza"


#= FUNZIONI ===================================================================

def before_incoming(entity, from_room, direction, to_room, troll, running, behavioured):
    change_descr(troll)
#- Fine Funzione -

def before_looked(entity, troll, descr, detail, use_examine, behavioured):
    # Questo non serve a molto visto che il cambio della long si vede
    #  cmnq solo al look successivo
    change_descr(troll)
#- Fine Funzione -

def change_descr(troll):
    if not troll:
        return

    ragazza = cerca_la_ragazza(troll.location, RAGAZZA_PROTO_CODE)
    if not ragazza:
        troll.long = "$N grugnisce soddisfatto"
    else:
        troll.long = "$N grugnisce soddisfatto mentre sevizia una povera donna."
#- Fine Funzione -


def before_die(troll, opponent):
    ragazza = cerca_la_ragazza(troll.location, RAGAZZA_PROTO_CODE)
    if ragazza:
        ragazza.long = "$N piange disperata per le sevizie del troll"
        ragazza.descr_sixth = "#looker is SEX.MALE#Mhhhh... un'umana di un certa sua bellezza... almeno una volta tolti i vari strati  di  sudiciume....  potresti guardare senza intervenire, oppure potresti salvarla, oppure ancora potresti salvarla per vedere quanto vale la sua riconoscenza...#Mhhhh... Porre fine a questa situazione? Approfittarne? Tirar dritto?#"
#- Fine Funzione -

def cerca_la_ragazza(location, ragazza_proto_code):
    for en in location.iter_contains():
        if not en.IS_PLAYER and en.prototype.code == ragazza_proto_code:
            return en
    return None
#- Fine Funzione -
