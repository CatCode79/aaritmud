# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_say(entity, argument="", behavioured=False):
    """
    Comando per parlare normalmente nella stanza.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return rpg_channel(entity, argument, CHANNEL.SAY, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "say <messaggio da dire>\n"
    syntax += "say a <nome bersaglio> <messaggio da dire al bersaglio>\n"
    syntax += "say al gruppo <messaggio da dire al gruppo>\n"

    return syntax
#- Fine Funzione -
