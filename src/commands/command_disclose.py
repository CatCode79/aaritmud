# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando disclose, che non è altro che un open
forzato sui soli oggetti di tipologia contenitore.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_open", globals(), locals(), [""]))
from src.commands.command_open import command_open


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[cyan]schiudere[close]",
         "you2"       : "[cyan]schiuderti[close]",
         "you"        : "[cyan]schiudi[close]",
         "it"         : "[cyan]schiude[close]"}


#= FUNZIONI ====================================================================

def command_disclose(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return command_open(entity, argument, verbs=VERBS, container_only=True)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "disclose <contenitore da aprire>\n"
#- Fine Funzione -
