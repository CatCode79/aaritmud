# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando che serve ad impugnare.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_wield", globals(), locals(), [""]))
from src.commands.command_wield import command_wield


#= COSTANTI ====================================================================

VERBS = {"infinitive_min" : "tenere",
         "infinitive"     : "tenere nella $hand2",
         "you_min"        : "tieni",
         "you"            : "tieni nella $hand2",
         "you2_min"       : "tenerti",
         "you2"           : "tenerti nella $hand2",
         "you3_min"       : "ti tiene",
         "you3"           : "ti tiene nella $hand2",
         "it_min"         : "tiene",
         "it"             : "tiene nella $hand2",
         "self_min"       : "tenersi",
         "self"           : "tenersi nella $hand2",
         "participle"     : "tenut$O"}


#= FUNZIONI ====================================================================

def command_hold(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di prendere un oggetto nella mano secondaria o, se quest'ultima
    è occupata, in quella primaria.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return command_wield(entity, argument, verbs=verbs, behavioured=behavioured, command_name="hold")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "hold <nome oggetto o creatura>\n"
#- Fine Funzione -
