# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_yell(entity, argument, behavioured=False):
    """
    Comando per parlare urlando nella stanza.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return rpg_channel(entity, argument, CHANNEL.YELL, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "yell <messaggio da urlare>\n"
    syntax += "yell a <nome bersaglio> <messaggio da urlare al bersaglio>\n"
    syntax += "yell al gruppo <messaggio che si vuole urlare al gruppo>\n"

    return syntax
#- Fine Funzione -
