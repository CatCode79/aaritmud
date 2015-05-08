# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle stanze, uscite, mura e destinazioni.
"""


#= IMPORT ======================================================================

from src.enums    import GRAMMAR
from src.log      import log
from src.note     import Comment, send_note


#= FUNZIONI ====================================================================

def command_comment(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return send_note(entity, argument, "command_comment", "comment", "commento", "commenti", Comment, GRAMMAR.MASCULINE)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "comment <commento che si vuole esprimere>\n"
#- Fine Funzione -
