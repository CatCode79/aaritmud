##(BB) di difficile creazione visto che esistono sia i mucchi fisici che quelli visivi

# -*- coding: utf-8 -*-

"""
Comando per dividere un mucchio fisico.
"""


#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import TO
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[khaki]dividere[close]",
         "you2"       : "[khaki]dividerci[close]",
         "you"        : "[khaki]dividi[close]",
         "it"         : "[khaki]divide[close]",
         "gerund"     : "[khaki]dividendo[close]"}


#= FUNZIONI ====================================================================

def command_split(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che [white]cosa[close] vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_split")
            entity.send_output(syntax)
        return False

    force_return = check_trigger(entity, "before_split", entity, target1, target2)
    if force_return:
        return True


    force_return = check_trigger(entity, "after_split", entity, target1, target2)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "split <mucchio da divedere>\n"
    syntax += "split <mucchio da divedere> <quantità voluta>\n"

    return syntax
#- Fine Funzione -
