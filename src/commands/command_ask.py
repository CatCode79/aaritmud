# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.channel    import rpg_channel
from src.enums      import CHANNEL
from src.log        import log
from src.utility    import put_final_mark


#= FUNZIONI ====================================================================

def command_ask(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    if argument:
        argument = put_final_mark(argument, "?")

    return rpg_channel(entity, argument, CHANNEL.SAY, ask=True, exclaim=False, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "ask <messaggio da dire>\n"
    syntax += "ask a <nome bersaglio> <messaggio da dire al bersaglio>\n"
    syntax += "ask al gruppo <messaggio da dire al gruppo>\n"

    return syntax
#- Fine Funzione -
