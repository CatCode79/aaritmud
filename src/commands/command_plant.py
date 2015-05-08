# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando per piantare.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.__seed_plant__", globals(), locals(), [""]))
from src.commands.__seed_plant__ import seed_or_plant


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[green]piantare[close]",
         "you2"       : "[green]piantarti[close]",
         "you"        : "[green]pianti[close]",
         "it"         : "[green]pianta[close]",
         "it2"        : "[green]piantarl$O[close]",
         "participle" : "[green]piantato[close]"}


#= FUNZIONI ====================================================================

def command_plant(entity, argument="", verbs=VERBS, behavioured=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return seed_or_plant(entity, argument, verbs, behavioured, "command_plant")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "plant <pianta>\n"
    #syntax += "plant <pianta> <luogo in cui seminare>\n"

    return syntax
#- Fine Funzione -
