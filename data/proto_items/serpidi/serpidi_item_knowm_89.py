# -*- coding: utf-8 -*-

# 3 10 -2 serpidi


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import TO
from src.item     import Item
from src.mob      import Mob
from src.room     import Room


#= FUNZIONI ====================================================================

def before_readed(entity, target, output, extra, behavioured):
    if not target.location or not target.location.IS_PLAYER:
        entity.act("Non hai la pergamena a tua disposizione!", TO.ENTITY)
        return True

    entity.act("$n distende la pergamena e prova a leggerla a voce alta!", TO.OTHERS)
#- Fine Funzione -


def dstat(val, perc):
    return str(int(val * perc / 100))
#- Fine Funzione -


def after_readed(entity, target, output, extra, behavioured):
    toplife = 0
    mostro = None
    for contenuto in entity.location.iter_contains():
        if contenuto.IS_MOB:
            if contenuto.max_life > toplife:
                toplife = contenuto.max_life
                mostro = contenuto
    if not mostro:
        entity.send_output("Nella stanza non ci sono entità vive!")
        return

    level_difference = mostro.level - entity.level
    if level_difference < 5:
        inaccuracy_perc = random.randint(95, 105)
    elif level_difference < 10:
        inaccuracy_perc = random.randint(85, 115)
    elif level_difference < 20:
        inaccuracy_perc = random.randint(70, 130)
    else: 
        entity.send_output("%s è troppo potente per te! Meglio sparire al più presto..." % mostro.get_name(looker=entity))
        return

    entity.act("[red]C[close][yellow]hadyne[close][white] ti informa, per sua grazia e bontà, di quanto segue:[close]", TO.ENTITY)
    entity.act("[white]mob name: [close]"     + mostro.name, TO.ENTITY)
    entity.act("[white]race: [close]"         + str(mostro.race), TO.ENTITY)
    entity.act("[white]level: [close]"        + str(mostro.level), TO.ENTITY)
    entity.act("[white]strength: [close]"     + dstat(mostro.strength, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]endurance: [close]"    + dstat(mostro.endurance, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]agility: [close]"      + dstat(mostro.agility, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]speed: [close]"        + dstat(mostro.speed, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]intelligence: [close]" + dstat(mostro.intelligence, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]willpower: [close]"    + dstat(mostro.willpower, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]personality: [close]"  + dstat(mostro.personality, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]luck: [close]"         + dstat(mostro.luck, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]life: [close]"         + dstat(mostro.max_life, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]mana: [close]"         + dstat(mostro.max_mana, inaccuracy_perc), TO.ENTITY)
    entity.act("[white]vigor: [close]"        + dstat(mostro.max_vigour, inaccuracy_perc), TO.ENTITY)
    entity.act("[yellow]* * * * * * * * * * * * * * * * * * * * * * * *[close]", TO.ENTITY)
    target.extract(1)
#- Fine Funzione -
