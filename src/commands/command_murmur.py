# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_murmur(entity, argument="", behavioured=False):
    """
    Comando per parlare mormorando nella stanza.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return rpg_channel(entity, argument, CHANNEL.MURMUR, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "murmur <messaggio da mormorare>\n"
    syntax += "murmur a <nome bersaglio&> <messaggio da mormorare al bersaglio>\n"
    syntax += "murmur al gruppo <messaggio da mormorare al gruppo>\n"

    return syntax
#- Fine Funzione -
