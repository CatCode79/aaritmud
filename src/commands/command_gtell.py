# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.log import log


#= FUNZIONI ====================================================================

def command_gtell(entity, argument=""):
    """
    Permette di parlare al gruppo in maniera off-gdr.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    # (TD)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "gtell <messaggio off-gdr da dire al gruppo>\n"
#- Fine Funzione -
