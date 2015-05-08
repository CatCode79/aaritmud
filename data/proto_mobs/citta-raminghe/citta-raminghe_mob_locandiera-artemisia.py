# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

import random

from src.color    import color_first_upper
from src.database import database
from src.defer    import defer, defer_random_time, defer_if_possible
from src.enums    import TO
from src.item     import Item
from src.log      import log
from src.utility  import is_same, is_infix, multiple_arguments

from src.commands.command_say  import command_say
from src.commands.command_give import command_give
from src.commands.command_drop import command_drop


#= COSTANTI ====================================================================

PROTO_FOODS_CODES = ["citta-raminghe_item_food-bistecca-pepe",
                     "citta-raminghe_item_food-dolce-vaniglia",
                     "citta-raminghe_item_food-pollo-stufato",
                     "citta-raminghe_item_food-spezzatino-prugne-mandorle",
                     "citta-raminghe_item_food-zuppa-fagioli-peperoncino"]

#= FUNZIONI ====================================================================

def before_listen_rpg_channel(locandiera, player, target, phrase, ask, exclaim, behavioured):
    # Mi assicuro che si stia parlando rivolgendosi alla locandiera
    if target != locandiera:
        return

    player_code = player.get_numbered_keyword(looker=locandiera)

    if is_infix("menù", phrase):
        to_say = "a %s Il nostro menù di oggi lo potete vedere qui." % player_code
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, to_say)
        return

    proto_cibi = []
    for proto_code in PROTO_FOODS_CODES:
        table_name = "proto_" + proto_code.split("_")[1] + "s"
        proto_entity = database[table_name][proto_code]

        for keyword in multiple_arguments(proto_entity.get_keywords_attr(looker=locandiera)):
            if is_infix(keyword, phrase):
                proto_cibi.append(proto_entity)

    if not proto_cibi:
        to_say = "a %s Non credo di poterla accontentare..." % player_code
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, to_say)
        return

    proto_pietanza = random.choice(proto_cibi)
    pietanza = proto_pietanza.CONSTRUCTOR(proto_pietanza.code)

    to_say = "a %s Ottimo! %s in arrivo." % (player_code, color_first_upper(pietanza.get_name(looker=player)))
    defer_if_possible(1, 2, locandiera, player, command_say, locandiera, to_say)
    defer_random_time(6, 8, locandiera_act, locandiera, pietanza, player)
#- Fine Funzione -


def locandiera_act(locandiera, pietanza, player):
    # Normale che possa capitare visto che la funzione è deferrata
    if not locandiera or not pietanza or not player:
        return

    pietanza.inject(locandiera)
    player_code = player.get_numbered_keyword(looker=locandiera)
    pietanza_code = pietanza.get_numbered_keyword(looker=locandiera)

    argument = "%s %s" % (pietanza_code, player_code)
    success_result = command_give(locandiera, argument)
    if success_result:
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, "a %s Buon appetito!" % player_code)
    else:
        # (TD) Lo lascia per terra! è proprio grezzo, bisognerebbe che lo appoggi
        # su di un tavolo, appena vi sarà il sistema della mobilia lo farò
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, "a %s Mi scuso ma la appoggio qui..." % player_code)
        defer_random_time(3, 4, command_drop, locandiera, pietanza_code)
#- Fine Funzione -
