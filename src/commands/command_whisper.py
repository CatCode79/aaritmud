# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.channel import rpg_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_whisper(entity, argument="", behavioured=False):
    """
    Comando per parlare sussurrando nella stanza.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return rpg_channel(entity, argument, CHANNEL.WHISPER, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "whisper <messaggio da sussurrare>\n"
    syntax += "whisper a <nome bersaglio> <messaggio da sussurrare al bersaglio>\n"
    syntax += "whisper al gruppo <messaggio da sussurrare al gruppo>\n"

    return syntax
#- Fine Funzione -
