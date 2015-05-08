# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.defer    import defer
from src.enums    import TO, FLAG, RACE


#= COSTANTI ====================================================================

TIME_DELAY = 5
TIME_LONG_RESET = 100

pescetto_long = "provato da esperienze indicibili"
likes_fish_races = [RACE.FELAR, RACE.CAT, RACE.PYTHON, RACE.FOX]


#= FUNZIONI ====================================================================

def before_used(entity, pescetto, argument, behavioured):
        entity.act("Cerchi d'usare ed usi.", TO.ENTITY, pescetto)
        entity.act("$n tenta d'usarti ora.", TO.TARGET, pescetto)
        entity.act("$n tenta d'usare $N che dibattendosi lo voleva far desistere.", TO.OTHERS, pescetto)
        return False


def before_eated(entity, pescetto, devour, swallow, behavioured):
    if random.randint(0, 1) == 1:
        entity.act("Cerchi d'ingollare $N che però si dibatte impedendotelo.", TO.ENTITY, pescetto)
        entity.act("$n tenta d'ingoiarti ma vinci tu per ora.", TO.TARGET, pescetto)
        entity.act("$n tenta d'ingoiare $N che dibattendosi disperato l$o fa desistere.", TO.OTHERS, pescetto)
        return True


def after_eated(entity, pescetto, devour, swallow, behavioured):
    defer(TIME_DELAY, nausea, entity, pescetto)


def nausea(entity, pescetto):
    # Può capitare visto che questa funzione viene usata in una defer
    if not pescetto or not entity:
        return

    if FLAG.INGESTED not in pescetto.flags:
        return

    if entity.race in likes_fish_races:
        return

    entity.act("Un forte senso di nausea ti si aggrappa alla bocca dello stomaco facendoti vomitare.", TO.ENTITY)
    entity.act("L'espressione di $n cambia in un tangibile disgusto poco prima di vomitare.", TO.OTHERS, pescetto)
    entity.act("$n ti vomita all'esterno verso la libertà.", TO.TARGET, pescetto)

    pescetto.flags -= FLAG.INGESTED
    pescetto.extract(1)
    pescetto.inject(entity.location)
    pescetto.long  = "$N " +  pescetto_long
    defer(TIME_LONG_RESET, reset_long, pescetto)
#- Fine Funzione

def reset_long(pescetto):
    # Può capitare visto che questa funzione viene usata in una defer
    if not pescetto:
        return

    pescetto.long  = "$N " +  "si muove senza pace"
#- Fine Funzione
