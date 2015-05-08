# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Qui l'idea è che l'oggetto sia una numero di canovacci a costituire l'item
# l'oggetto vede diminuire il suo peso man mano che si prelvano canovacci
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
     matasse_db = {1: "carrozzone-zingaro_item_canovaccio-01-macchiato",
                   2: "carrozzone-zingaro_item_canovaccio-01-pulito",
                   3: "carrozzone-zingaro_item_canovaccio-01-usurato",
                   4: "carrozzone-zingaro_item_canovaccio-02-macchiato",
                   5: "carrozzone-zingaro_item_canovaccio-02-pulito",
                   6: "carrozzone-zingaro_item_canovaccio-02-usurato"}

     num_rand = random.randint(1,100)
     if num_rand < 17:
         matassa_label = matasse_db[1]
     elif num_rand < 34:
         matassa_label = matasse_db[2]
     elif num_rand < 50:
         matassa_label = matasse_db[3]
     elif num_rand < 67:
         matassa_label = matasse_db[4]
     elif num_rand < 84:
         matassa_label = matasse_db[5]
     else:
         matassa_label = matasse_db[6]

     matassa = Item(matassa_label)
     matassa.inject(location)

     entity.act("Affondi la $hand verso $N incurante.", TO.ENTITY, target)
     entity.act("Ti senti un po' deprezzato ogni volta $n ti indaga!", TO.TARGET, target)
     entity.act("Incurante $n allunga una $hand verso $N.", TO.OTHERS, target)

     execution_result = command_get(entity, "canovaccio")

     # Il peso del filo viene diminuito man mano che se ne preleva quando
     # ne resta troppo poco viene eliminato
     if target.weight < matassa.weight:
        target.act("E questo era il tuo ultimo pezzo di stoffa...", TO.ENTITY)
        target.act("E questo era l'ultimo pezzo di stoffa...", TO.OTHERS)
        target.extract(1)
     else:
        target.weight = target.weight - matassa.weight

     return execution_result
#- Fine Funzione
