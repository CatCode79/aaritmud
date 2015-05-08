# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.channel import talk_channel
from src.enums   import CHANNEL
from src.log     import log


#= FUNZIONI ====================================================================

def command_admtalk(entity, argument=""):
    """
    Permette di parlare con tutti gli amministratori del Mud.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return talk_channel(entity, CHANNEL.ADMTALK, argument)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "admtalk <messaggio da inviare tra admin>\n"
#- Fine Funzione -
