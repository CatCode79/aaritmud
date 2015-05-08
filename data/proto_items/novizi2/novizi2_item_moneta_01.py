# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.log   import log
from src.enums import TO


#= FUNZIONI ====================================================================

def after_drop(entity, coin, room, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not coin:
        log.bug("coin non è un parametro valido: %r" % coin)
        return

    if not room:
        log.bug("room non è un parametro valido: %r" % room)
        return

    if coin.quantity != 1:
        return False

    heads_or_tails(coin)
    entity.act("Fai volteggiare $N fino a terra", TO.ENTITY, coin)
    entity.act("$n fa voteggiare te povero $N", TO.TARGET, coin)
    entity.act("$n fa volteggiare $N fino a terra", TO.OTHERS, coin)
    coin = coin.from_location(1)
    coin = coin.to_location(room, use_look=False)
    return True
#- Fine Funzione -


def after_inject(coin, room):
    if not coin:
        log.bug("coin non è un parametro valido: %r" % coin)
        return

    coin.long = "$N è caduta in piedi!"
#- Fine Funzione -


def after_reset(coin):
    if not coin:
        log.bug("coin non è un parametro valido: %r" % coin)
        return

    coin.long = "$N è caduta in piedi!"
#- Fine Funzione -


def heads_or_tails(coin):
    if not coin:
        log.bug("coin non è un parametro valido: %r" % coin)
        return

    number = random.randint(0, 200)
    if number == 0:
        coin.long = "$N è caduta in piedi!"
    elif number % 2 == 0:
        coin.long = "$N cadendo ha segnato testa."
    else:
        coin.long = "$N cadendo ha segnato croce."
#- Fine Funzione -


def before_readed(entity, location, output, extra, behavioured):
    print ">>> entity: ", entity
    print ">>> location: ", location
    print ">>> extra: ", extra
    print ">>> output: ", output
    return
#- Fine Funzione -
