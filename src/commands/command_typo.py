# -*- coding: utf-8 -*-

"""
Serve a dar modo ai giocatori di segnalare una tipica svista nella
digitazione, oppure un errore sintattico o grammaticale.
"""


#= IMPORT ======================================================================

from src.enums import GRAMMAR
from src.log   import log
from src.note  import Typo, send_note


#= FUNZIONI ====================================================================

def command_typo(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return send_note(entity, argument, "command_typo", "typo", "typo", "typo", Typo, GRAMMAR.MASCULINE)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "typo <errore testuale trovato>\n"
#- Fine Funzione -
