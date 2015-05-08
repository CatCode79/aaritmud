# -*- coding: utf-8 -*-

"""
Comando che inizia un combattimento con un'altra entità.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[red]distruggere[close]",
         "you2"       : "[red]distruggerti[close]",
         "you"        : "[red]distruggi[close]",
         "gerund"     : "[red]distruggendo[close]",
         "noun"       : "[red]distruggerl%s[close]"}


#= FUNZIONI ====================================================================

def command_destroy(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    if config.reload_commands:
        reload(__import__("src.commands.command_kill", globals(), locals(), [""]))
    from src.commands.command_kill import kill_handler

    entity_tables = ["items"]
    return kill_handler(entity, argument, "command_destroy", entity_tables, destroy=True, verbs=verbs, behavioured=behavioured)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "destroy <nome dell'oggetto>\n"

    return syntax
#- Fine Funzione -
