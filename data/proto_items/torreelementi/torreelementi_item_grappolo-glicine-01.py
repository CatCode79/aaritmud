# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# C'è un grappolo di glicine in terra NO_LOOK_LIST suggerito dalle descrizoni
# della room.
# Se si cerca di raccoglierlo ogni tanto non va a buon fine (troppe api)
# Se il get va a buon fine viene rimossa la flag NO_LOOK_LIST e 
# dopo poco viene generato un altro grappolo


#= IMPORT ======================================================================

import random

from src.engine import engine

from src.defer import defer_random_time
from src.enums import TO, FLAG
from src.item  import Item
from src.log   import log


#= FUNZIONI ====================================================================

def on_reset(grappolo):
    #non lo faccio scattare al boot
    if engine.booting:
        return
    if not grappolo:
        log.bug("grappolo non è un parametro valido: %r" % grappolo)
        return
    change_item(grappolo)
#- Fine Funzione -


def before_get(player, grappolo, room, behavioured):
    if not room:
        log.bug("room non è valida: %r" % room)
        return

    if random.randint(0, 3) == 0:
        grappolo.act("$N Cerchi di prenderti ma ci son troppe api per ora e rinuncia.", TO.ENTITY, player)
        grappolo.act("$N cerca di prendere gualcosa nel glicine ma rinuncia ben prima di allungare la $HAND.", TO.OTHERS, player)
        grappolo.act("Cerchi di prendere $n, ma ci son troppe api per ora e rinunci.", TO.TARGET, player)
        return True

    if FLAG.NO_LOOK_LIST in grappolo.flags:
        grappolo.flags -= FLAG.NO_LOOK_LIST
        change_item(grappolo)
        defer_random_time(10, 60, popping_new_grappolo, room)
#- Fine Funzione -


def popping_new_grappolo(room):
    new_grappolo = Item("torreelementi_item_grappolo-glicine-01")
    new_grappolo.inject(room)
#- Fine Funzione -


def change_item(grappolo):
    grappolo_long_db = {1 : "adagiato in terra",
                        2 : "adagiato in terra",
                        3 : "adagiato in terra"}

    grappolo_short_db = {1 : "un grappolo in fiore di [purple]glicine porpora[close]",
                         2 : "un grappolo fiorito di [violet]glicine viola[close]",
                         3 : "un grappolo fiorito di [blue]glicine blu[close]"}

    grappolo_name_db = {1 : "Un Grappolo Fiorito di [purple]Glicine Porpora[close]",
                        2 : "Un Grappolo Fiorito di [violet]Glicine Viola[close]",
                        3 : "Un Grappolo Fiorito di [blue]Glicine Blu[close]"}

    grappolo_descr_db = {1 : "Un grappolo di fiori di glicine di un bellissimo [purple]porpora[close]",
                         2 : "Un grappolo di fiori di glicine di un bellissimo [violet]viola[close]",
                         3 : "Un grappolo di fiori di glicine di un bellissimo [blue]blu[close]"}

    grappolo_num = random.randint(1, 3)
    #print grappolo_num
    grappolo.long  = "$N " + grappolo_long_db[grappolo_num]
    grappolo.short = grappolo_short_db[grappolo_num]
    grappolo.name  = grappolo_name_db[grappolo_num]
    grappolo.descr = grappolo_descr_db[grappolo_num]
#- Fine Funzione -
