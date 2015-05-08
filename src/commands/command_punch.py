# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando per dar pugni.
"""


#= IMPORT ======================================================================

from src.gamescript import check_trigger
from src.log        import log


#= FUNZIONI ====================================================================

def command_punch(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    # (TD) inserire il check_trigger
    # (TD) finirlo

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "punch\n"

    return syntax
#- Fine Funzione -
