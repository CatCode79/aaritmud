# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.channel import talk_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_chat(entity, argument=""):
    """
    Permette di parlare con tutti nel Mud, in maniera off-gdr.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return talk_channel(entity, CHANNEL.CHAT, argument)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "chat <messaggio da inviare in off-gdr>\n"
#- Fine Funzione -
