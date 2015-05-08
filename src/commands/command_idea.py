# -*- coding: utf-8 -*-

"""
Serve a dar modo ai giocatori di proporre una loro idea agli amministratori.
"""


#= IMPORT ======================================================================

from src.enums    import GRAMMAR
from src.log      import log
from src.note     import Idea, send_note


#= FUNZIONI ====================================================================

def command_idea(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return send_note(entity, argument, "command_idea", "idea", "idea", "idee", Idea, GRAMMAR.FEMININE)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "idea <idea avuta che si vuole segnalare>\n"
#- Fine Funzione -
