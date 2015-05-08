# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_shout(entity, argument="", behavioured=False):
    """
    Comando per parlare gridando nella stanza.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return rpg_channel(entity, argument, CHANNEL.SHOUT, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "shout <messaggio da gridare>\n"
    syntax += "shout a <nome bersaglio> <messaggio da gridare al bersaglio>\n"
    syntax += "shout al gruppo <messaggio da gridare al gruppo>\n"

    return syntax
#- Fine Funzione -
