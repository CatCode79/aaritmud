# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import OPTION, TO
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {}
VERBS["infinitive"] = "[lightcyan]uscire[close]"


#= FUNZIONI ====================================================================

def command_exit(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Dove vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_exit")
            entity.send_output(syntax)
        return False

    # (TD) aggiungervi il check_trigger
    # (TD) finirlo
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "exit <entità da cui vuoi uscire>\n"
#- Fine Funzione -
