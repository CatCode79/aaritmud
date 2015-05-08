# -*- coding: utf-8 -*-

#= NOTE ======================================================================

# - Descrizione dinamica del mob a seconda delle ore del giorno
# - Si usano due trigger dei momenti della giornata e si fanno 4 o 5 defer
# - Se si vuole duplicare gli oggetti ricordarsi di inserire forti limitazioni,
#   probabilmente è meglio se lo specchio funzioni sono sugli oggetti dell'area
#   carrozzone così da non avere sorprese di inventario duplicato super potente
#   nei pg


#= IMPORT ======================================================================

import random

from src.log      import log
from src.database import database
from src.enums    import TO, RACE, FLAG, ENTITYPE

from src.commands.command_say import command_say
from src.commands.command_eat import command_eat


#= COSTANTI ===================================================================

CIBO_PROTO_CODE = "carrozzone-zingaro_item_cibo-specchio"
CAT_PROTO_CODE  = "carrozzone-zingaro_mob_gatto-zingaro"


#= FUNZIONI ===================================================================

def before_giving(player, cibo, specchio, direzione, behavioured):
    if not specchio:
        return

    gatto = cerca_il_gatto(player.location, CAT_PROTO_CODE)
    if not gatto:
        # ?
        return

    if not cibo.race == RACE.RODENT:
        player.act("$N storce i baffi schizzinoso.", TO.ENTITY, gatto)
        player.act("$n tenta di propinarti qualcosa che anche un cane rifiuterebbe.", TO.TARGET, gatto)
        player.act("$n tenta inutilmente di dare qualcosa a $N che lo snobba schizzinoso.", TO.OTHERS, gatto)
        return True        
#- Fine Funzione -


def cerca_il_gatto(location, cat_proto_code):
    for en in location.iter_contains():
        if not en.IS_PLAYER and en.prototype.code == cat_proto_code:
            return en.split_entity()
    return None
#- Fine Funzione -
