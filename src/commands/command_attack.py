# -*- coding: utf-8 -*-

"""
Comando che inizia un combattimento con un'altra entità.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[red]attaccare[close]",
         "you2"       : "[red]attaccarti[close]",
         "you"        : "[red]attacchi[close]",
         "gerund"     : "[red]attaccando[close]",
         "noun"       : "[red]attaccarl%s[close]",
         "it"         : "[red]attacchi[close]"}


#= FUNZIONI ====================================================================

def command_attack(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    if config.reload_commands:
        reload(__import__("src.commands.command_kill", globals(), locals(), [""]))
    from src.commands.command_kill import kill_handler

    entity_tables = ("mobs", "players")
    return kill_handler(entity, argument, "command_attack", entity_tables, attack=True, verbs=verbs, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "attack <creatura o giocatore>\n"

    return syntax
#- Fine Funzione -
