# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# oggetto catasta dal quale si estraggono oggetti random mentre si
# tenta di raccoglierlo.


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import TO
from src.log      import log
from src.item     import Item

from src.commands.command_get import command_get


#= COSTANTI ====================================================================

PROTO_CIANFUSAGLIE_CODES = [
    "ikea_item_calzino",
    "ikea_item_calzino",
    "ikea_item_calzino",
    "ikea_item_guanti",
    "ikea_item_guanti",
    "ikea_item_guanti",
    "ikea_item_cucchiaio-dolce",
    "ikea_item_cucchiaio-dolce",
    "ikea_item_cucchiaio-dolce",
    "ikea_item_cucchiaio-dolce",
    "carrozzone-zingaro_item_canovaccio-01-macchiato",
    "carrozzone-zingaro_item_canovaccio-01-macchiato",
    "carrozzone-zingaro_item_canovaccio-01-macchiato",
    "carrozzone-zingaro_item_canovaccio-01-macchiato",
    "carrozzone-zingaro_item_canovaccio-01-macchiato",
    "carrozzone-zingaro_item_saponetta-01",
    "carrozzone-zingaro_item_saponetta-01",
    "carrozzone-zingaro_item_saponetta-01",
    "carrozzone-zingaro_item_saponetta-01",
    "carrozzone-zingaro_item_vasetto-01",
    "carrozzone-zingaro_item_vasetto-01",
    "carrozzone-zingaro_item_vasetto-01",
    "villaggio-zingaro_item_filo-di-ferro",
    "villaggio-zingaro_item_filo-di-ferro",
    "villaggio-zingaro_item_filo-di-ferro",
    "villaggio-zingaro_item_filo-di-ferro",
    "villaggio-zingaro_item_filo-di-ferro",
    "ikea_item_cintura",
    "ikea_item_cintura",
    "ikea_item_cintura",
    "ikea_item_cintura",
    "mfdonald_item_anello_ematite_01",
    "miniere-kezaf_item_gemma-zircone"]


def before_try_to_get(entity, target, location, behavioured):
    if (random.randint(0, 1) == 0):
        entity.act("Infili una $hand tra i fili ma qualcosa ti punge e la ritiri subito di scatto.", TO.ENTITY, target)
        entity.act("Non appena $n infila una $hand tra i fili la ritira di scatto.", TO.OTHERS, target)
        return True

    oggetto = Item(random.choice(PROTO_CIANFUSAGLIE_CODES))
    oggetto.inject(location)

    entity.act("Infili la $hand tra $N per prendere qualcosa.", TO.ENTITY, target)
    entity.act("Ti senti un po' deprezzat$O ogni volta $n t'indaga!", TO.TARGET, target)
    entity.act("$n infila la $hand tra $N per prendere qualcosa.", TO.OTHERS, target)

    numbered_keyword = oggetto.get_numbered_keyword(looker=entity)
    execution_result = command_get(entity, numbered_keyword)

    # Il peso dei fili viene diminuito man mano che se ne preleva.
    # Prima di farlo verifica che sia uscita una keyword quando ne resta
    # troppo poco viene eliminato
    if execution_result:
        if target.weight < oggetto.weight:
           target.act("Ed ora non ne trovi neanche uno, o così sembra.", TO.OTHERS, target)
           target.act("Ed ora non ne è rimasto neanche uno, o così sembra.", TO.ENTITY, target)
           target.extract(1)
        else:
           target.weight = target.weight - oggetto.weight

    return execution_result
#- Fine Funzione
