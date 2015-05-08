# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# il consueto script di generazione oggetti quando si getta l'entità
# il get sui semi-frutta produce entità seminabili e non
# l'oggetto semi frutta diminuisce di peso man mano che se ne preleva


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums import TO, FLAG
from src.item  import Item

from src.commands.command_get import command_get


#= TROUBLE =====================================================================

def before_try_to_get(entity, target, location, behavioured):
    frutta_semi_db = ["flora_item_mirtillo-rosso-01-frutto",
                      "flora_item_leccio-01-ghianda-viva",
                      "flora_item_leccio-02-ghianda-morta",
                      "flora_item_mirtillo-nero-01-frutto",
                      "flora_item_mirtillo-rosso-00-frutto-marcio",
                      "flora_item_mirtillo-rosso-00-frutto-sterile",
                      "flora_item_farnia-01-ghianda-viva",
                      "flora_item_farnia-02-ghianda-morta"]

    num_rand = random.randint(1, 100)
    if num_rand < 8:
        frutto_seme_code = frutta_semi_db[0]
    elif num_rand < 18:
        frutto_seme_code = frutta_semi_db[1]
    elif num_rand < 22:
        frutto_seme_code = frutta_semi_db[2]
    elif num_rand < 32:
        frutto_seme_code = frutta_semi_db[3]
    elif num_rand < 35:
        frutto_seme_code = frutta_semi_db[4]
    elif num_rand < 40:
        frutto_seme_code = frutta_semi_db[5]
    elif num_rand < 76:
        frutto_seme_code = frutta_semi_db[6]
    else:
        frutto_seme_code = frutta_semi_db[7]

    # Crea e inserisce il seme scelto nella locazione da cui prenderlo poi
    seed_founded = Item(frutto_seme_code)
    seed_founded.inject(location)

    # Attenzione che il get invierà i propri messaggi oltre a questi qui
    entity.act("Infili la $hand verso $N.", TO.ENTITY, target)
    entity.act("$n allunga una mano verso $N.", TO.OTHERS, target)
    entity.act("Ti senti un po' deprezzato ogni volta che $n ti indaga!", TO.TARGET, target)

    # Bisogna utilizzare la get_numbered_keyword perché non si sa se entity
    # in quel momento possa visualizzare la short diurna, notturna o il nome
    argument = seed_founded.get_numbered_keyword(looker=entity)
    if not location.IS_ROOM:
        argument += " %s " % location.get_numbered_keyword(looker=entity)
    execution_result = command_get(entity, argument)

    # La diminuzione del peso deve essere eseguita quando effettivamente sia
    # stato eseguito il comando di get, ovvero execution_result ha valore
    # di verità positiva
    if execution_result:
        if target.weight < seed_founded.weight:
            target.act("Dei $n che c'erano ora non resta nulla.", TO.ENTITY)
            target.act("Di te ormai ora non resta nulla.", TO.OTHERS)
            target.extract(1)
        else:
            target.weight = target.weight - seed_founded.weight

    return True
#- Fine Funzione
