# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando swallow.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_eat", globals(), locals(), [""]))
from src.commands.command_eat import command_eat


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "ingoiare",
         "you"        : "Ingoi",
         "you2"       : "ingoiarti",
         "self"       : "ingoiarsi",
         "it"         : "ingoia"}


#= FUNZIONI ====================================================================

def command_swallow(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Comando che serve per mangiare un entità.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return command_eat(entity, argument=argument, verbs=verbs, behavioured=behavioured, swallow=True, function_name="command_swallow")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "swallow\n"
    syntax += "swallow <qualcosa o qualcuno>\n"

    return syntax
#- Fine Funzione -
