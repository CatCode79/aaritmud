# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.enums import DIR
from src.log   import log


#= FUNZIONI ====================================================================

def command_up(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return entity.move(DIR.UP, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "up\n"
#- Fine Funzione -
