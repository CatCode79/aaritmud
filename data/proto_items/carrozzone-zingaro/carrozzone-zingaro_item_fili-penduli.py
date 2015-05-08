# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Qui l'idea è che l'oggetto sia una numero elevato di matassine colorate
# il player ne prende una e si trova in mano una matassina con un colore più
# o meno casuale.
# l'oggetto vede diminuire il suo peso man mano che si prelvano matassine
# quando il peso scende sotto una certa soglia l'oggetto è rimosso


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import TO
from src.item     import Item
from src.log      import log

from src.commands.command_get import command_get


#= FUNZIONI ====================================================================

def before_try_to_get(entity, target, location, behavioured):
    matasse_db = {1: "carrozzone-zingaro_item_matassa-arruffata-rossa",
                  2: "carrozzone-zingaro_item_matassa-arruffata-indaco",
                  3: "carrozzone-zingaro_item_matassa-arruffata-gialla"}

    num_rand = random.randint(1, 100)
    if num_rand < 21:
        matassa_label = matasse_db[2]
    elif num_rand < 61:
        matassa_label = matasse_db[1]
    else:
        matassa_label = matasse_db[3]

    matassa = Item(matassa_label)
    matassa.inject(location)

    entity.act("Allunghi la $hand verso $N per prelevarne un po'.", TO.ENTITY, target)
    entity.act("Ti senti un po' deprezzato ogni volta $n ti indaga!", TO.TARGET, target)
    entity.act("$n allunga una mano in alto verso $N.", TO.OTHERS, target)

    execution_result = command_get(entity, "matassa")

    # Il peso del filo viene diminuito man mano che se ne preleva quando
    # ne resta troppo poco viene eliminato
    if target.weight < matassa.weight:
        target.act("Una volta pendevi dal soffitto ma ora sei terminato...", TO.ENTITY)
        target.act("Del $n che pendeva dal soffitto ora non ne resta più.", TO.OTHERS)
        target.extract(1)
    else:
        target.weight = target.weight - matassa.weight

    return execution_result
#- Fine Funzione
