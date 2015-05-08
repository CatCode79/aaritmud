# -*- coding: utf-8 -*-

#= NOTE ========================================================================

# (TD) rendere univoco il pezzo di codice di consegna cibi
# (TD) funzione esterna per la consegna in differita del cibo con i relativi TO
# facendo attenzione che il cibo deve essere in game per poterlo usare in TO


#= IMPORT ======================================================================

import random
import re

from src.database import database
from src.defer    import defer_random_time
from src.enums    import TO
from src.log      import log
from src.item     import Item
from src.utility  import is_same, is_infix, multiple_arguments

from src.commands.command_drop import command_drop
from src.commands.command_give import command_give
from src.commands.command_say  import command_say
from src.commands.command_yell import command_yell


#= COSTANTI ====================================================================

PROTO_FOODS_CODES = ["villaggio-zingaro_item_castagna",
                     "villaggio-zingaro_item_castagna-abbrustolita"]


#= FUNZIONI ====================================================================

def before_listen_rpg_channel(caldarrostaio, player, target, phrase, ask, exclaim, behavioured):
    if not player.IS_PLAYER:
        return

    # Mi assicuro che si stia parlando rivolgendosi al caldarrostaio
    if target != caldarrostaio:
        return

    if is_infix("menù", phrase):
        to_say = "a %s Car$o, io vendo solo caldarroste." % player.code
        defer_random_time(1, 2, command_say, caldarrostaio, to_say)
        return

    proto_cibi = []
    for proto_code in PROTO_FOODS_CODES:
        table_name = "proto_" + proto_code.split("_")[1] + "s"  # E con questo hai scoperto come mai i codici prototipo delle entità devono avere l'identificativo della tipologia tra due underscore
        proto_entity = database[table_name][proto_code]
        for keyword in multiple_arguments(proto_entity.get_keywords_attr()):
            #print ">>> Keyword <<<", proto_entity.code, keyword
            if is_infix(keyword, phrase):
                proto_cibi.append(proto_entity)

    if not proto_cibi:
        to_say = "a %s Ma io vendo solo castagne!" % player.code
        command_say(caldarrostaio, to_say)
        return

    to_say = "a %s Castagne in arrivo!" % player.code
    defer_random_time(1, 2, command_say, caldarrostaio, to_say)

    proto_pietanza = random.choice(proto_cibi)
    castagne = proto_pietanza.CONSTRUCTOR(proto_pietanza.code)
    defer_random_time(5, 7, caldarrostaio_act, caldarrostaio, player, castagne)
#- Fine Funzione -


def caldarrostaio_act(caldarrostaio, player, castagne):
    # Normale visto che questa funzione viene deferrata
    if not caldarrostaio or not player or not castagne:
        return

    if player.location != caldarrostaio.location:
        to_yell = "Hei %s, dove cavolo te ne sei andato?" % player.get_name(looker=caldarrostaio)
        command_yell(caldarrostaio, to_yell)
        return

    castagne.inject(caldarrostaio)
    player_code = player.get_numbered_keyword(looker=caldarrostaio)
    pietanza_code = castagne.get_numbered_keyword(looker=caldarrostaio)

    argument = "%s %s" % (pietanza_code, player_code)
    success_result = command_give(caldarrostaio, argument)
    if success_result:
        defer_if_possible(1, 2, caldarrostaio, player, command_say, caldarrostaio, "a %s Buon appetito!" % player_code)
    else:
        # (TD) Lo lascia per terra! è proprio grezzo, bisognerebbe che lo appoggi
        # su di un tavolo, appena vi sarà il sistema della mobilia lo farò
        defer_if_possible(1, 2, caldarrostaio, player, command_say, caldarrostaio, "a %s Scuso ma te l'appoggio qui, eh?" % player_code)
        defer_random_time(3, 4, command_drop, caldarrostaio, pietanza_code)
#- Fine Funzione -
