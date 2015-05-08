# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando disclose, che non è altro che un close
forzato sui soli oggetti di tipologia contenitore.
"""


#= IMPORT ======================================================================

from src.config     import config
from src.gamescript import check_trigger
from src.log        import log

if config.reload_commands:
    reload(__import__("src.commands.command_close", globals(), locals(), [""]))
from src.commands.command_close import command_close


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[darkcyan]richiudere[close]",
         "you2"       : "[darkcyan]richiuderti[close]",
         "you"        : "[darkcyan]Richiudi[close]",
         "it"         : "[darkcyan]richiude[close]"}


#= FUNZIONI ====================================================================

def command_shut(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return command_close(entity, argument, verbs=verbs, behavioured=behavioured, container_only=True)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "shut <contenitore da richiudere>\n"
#- Fine Funzione -
