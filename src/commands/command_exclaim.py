# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.log import log

from src.enums   import CHANNEL
from src.channel import rpg_channel
from src.utility import put_final_mark


#= FUNZIONI ====================================================================

def command_exclaim(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    if argument:
        argument = put_final_mark(argument, "!")

    return rpg_channel(entity, argument, CHANNEL.SAY, ask=False, exclaim=True, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "exclaim <messaggio da dire>\n"
    syntax += "exclaim a <nome bersaglio> <messaggio da dire al bersaglio>\n"
    syntax += "exclaim al gruppo <messaggio da dire al gruppo>\n"

    return syntax
#- Fine Funzione -
