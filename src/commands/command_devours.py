# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_eat", globals(), locals(), [""]))
from src.commands.command_eat import command_eat


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[red]divorare[close]",
         "you"        : "[red]Divori[close]",
         "you2"       : "[red]divorarti[close]",
         "self"       : "[red]divorarsi[close]",
         "it"         : "[red]divora[close]"}


#= FUNZIONI ====================================================================

def command_devours(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return command_eat(entity, argument=argument, verbs=verbs, behavioured=behavioured, devours=True, swallow=False, function_name="command_devours")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "devours\n"
    syntax += "devours <qualcosa o qualcuno>\n"

    return syntax
#- Fine Funzione -
