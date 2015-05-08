# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando give.
"""

#= IMPORT ======================================================================

from src.config import config
from src.enums  import FLAG, ROOM
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.__give_put__", globals(), locals(), [""]))
from src.commands.__give_put__ import give_or_put


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[orange]dare[close]",
         "noun"       : "[orange]darlo[close]",
         "you"        : "[orange]dai[close]",
         "you2"       : "[orange]darti[close]",
         "it"         : "[orange]dà[close]"}


#= FUNZIONI ====================================================================

def command_give(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di dare entità, di solito oggetti, ad altre entità, di solito
    player.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return give_or_put(entity, argument, verbs, behavioured, ("mobs", "players", "items"), FLAG.NO_GIVE, ROOM.NO_GIVE, "give", "gave", "giving", "a")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "give <oggetto o creatura da dare> <oggetto o creatura a cui darla>\n"
#- Fine Funzione -
