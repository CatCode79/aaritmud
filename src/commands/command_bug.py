# -*- coding: utf-8 -*-

"""
Serve a dar modo ai giocatori di segnalare un baco agli amministratori.
"""


#= IMPORT ======================================================================

from src.enums import GRAMMAR
from src.log   import log
from src.note  import Bug, send_note


#= FUNZIONI ====================================================================

def command_bug(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return send_note(entity, argument, "command_bug", "bug", "bug", "bug", Bug, GRAMMAR.MASCULINE)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "bug <frase descrivente il baco trovato>\n"
#- Fine Funzione -
