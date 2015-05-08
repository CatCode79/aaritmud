# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_sing(entity, argument="", behavioured=False):
    """
    Comando per cantare nella locazione.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return rpg_channel(entity, argument, CHANNEL.SING, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "sing <messaggio da cantare>\n"
    syntax += "sing a <nome bersaglio> <messaggio da cantare al bersaglio>\n"
    syntax += "sing al gruppo <messaggio da cantare al gruppo>\n"

    return syntax
#- Fine Funzione -
