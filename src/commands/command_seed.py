# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando per seminare.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.__seed_plant__", globals(), locals(), [""]))
from src.commands.__seed_plant__ import seed_or_plant


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[greenyellow]seminare[close]",
         "you2"       : "[greenyellow]seminarti[close]",
         "you"        : "[greenyellow]semini[close]",
         "it"         : "[greenyellow]semina[close]",
         "participle" : "[greenyellow]seminato[close]"}


#= FUNZIONI ====================================================================

def command_seed(entity, argument="", verbs=VERBS, behavioured=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return seed_or_plant(entity, argument, verbs, behavioured, "command_seed")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "seed <seme>\n"
    #syntax += "seed <seme> <luogo in cui seminare>\n"

    return syntax
#- Fine Funzione -
