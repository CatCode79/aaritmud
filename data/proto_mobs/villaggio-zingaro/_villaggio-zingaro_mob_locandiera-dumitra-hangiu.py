# -*- coding: utf-8 -*-

#= NOTE ======================================================================

# (TD) rendere univoco il pezzo di codice di consegna cibi
# (TD) funzione esterna per la consegna in differita del cibo con i relativi TO
#      facendo attenzione che il cibo deve essere in game per poterlo usare in TO


#= IMPORT ======================================================================

import random
import re

from src.color    import first_color_upper
from src.database import database
from src.defer    import defer_random_time, defer_if_possible
from src.enums    import TO
from src.log      import log
from src.item     import Item
from src.utility  import is_same, is_infix, multiple_arguments

from src.commands.command_drop import command_drop
from src.commands.command_give import command_give
from src.commands.command_say  import command_say


#= COSTANTI ====================================================================

PROTO_FOODS_CODES = ["villaggio-zingaro_item_polpette",
                     "villaggio-zingaro_item_zuppa",
                     "villaggio-zingaro_item_sformato",
                     "villaggio-zingaro_item_budino",
                     "ikea_item_filetto-alla-griglia"]


#= FUNZIONI ====================================================================

def before_listen_rpg_channel(locandiera, player, target, phrase, ask, exclaim, behavioured):
    # Mi assicuro che si stia parlando rivolgendosi alla locandiera
    if target != locandiera:
        return

    if is_infix("menù", phrase):
        to_say = "a %s Il nostro menù di oggi lo potete leggere anche da qui, è lì sul bancone." % player.code
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, to_say)
        return

    proto_cibi = []
    for proto_code in PROTO_FOODS_CODES:
        table_name = "proto_" + proto_code.split("_")[1] + "s"
        proto_entity = database[table_name][proto_code]
        for keyword in multiple_arguments(proto_entity.get_keywords_attr(looker=locandiera)):
            if is_infix(keyword, phrase):
                proto_cibi.append(proto_entity)

    player_code = player.get_numbered_keyword(looker=locandiera)

    if not proto_cibi:
        to_say = "a %s Non abbiam nessun cibo di quel tipo..." % player_code
        command_say(locandiera, to_say)
        return

    proto_pietanza = random.choice(proto_cibi)
    pietanza = proto_pietanza.CONSTRUCTOR(proto_pietanza.code)

    to_say = "a %s Ottimo! %s in arrivo." % (player_code, first_color_upper(pietanza.get_name(looker=locandiera)))
    defer_random_time(1, 2, command_say, locandiera, to_say)
    defer_random_time(5, 7, locandiera_act, locandiera, player, pietanza)
#- Fine Funzione -


# (TD) Funzione forse un po' troppo uguale a quella della locandiera della città
# delle raminghe, una delle due cambiarla un po' come comportamento o come messaggi
def locandiera_act(locandiera, player, cibo):
    # Normale che possa capitare visto che la funzione è deferrata
    if not locandiera or not cibo or not player:
        return

    cibo.inject(locandiera)
    player_code = player.get_numbered_keyword(looker=locandiera)
    cibo_code = cibo.get_numbered_keyword(looker=locandiera)

    argument = "%s %s" % (cibo_code, player_code)
    success_result = command_give(locandiera, argument)
    if success_result:
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, "a %s Buon appetito!" % player_code)
    else:
        # (TD) Lo lascia per terra! è proprio grezzo, bisognerebbe che lo appoggi
        # su di un tavolo, appena vi sarà il sistema della mobilia lo farò
        defer_if_possible(1, 2, locandiera, player, command_say, locandiera, "a %s Mi scuso ma la appoggio qui..." % player_code)
        defer_random_time(3, 4, command_drop, locandiera, cibo_code)
#- Fine Funzione -
