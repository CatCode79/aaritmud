# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.config     import config
from src.enums      import OPTION, TO
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import put_final_dot


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[mandarianorange]esprimere[close]",
         "you2"       : "[mandarianorange]esprimerti[close]",
         "it2"        : "[mandarianorange]esprimersi[close]"}


#= FUNZIONI ====================================================================

def command_emote(entity, argument="", behavioured=False):
    """
    Permette di inviare liberamente dei messaggi per poter esprimere sentimenti
    o gesti.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    force_return = check_trigger(entity, "before_emote", entity, argument, behavioured)
    if force_return:
        return True

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_emote")
            entity.send_output(syntax, break_line=False)
        return False

    if len(argument) > config.max_google_translate:
        entity.act("Non puoi %s in maniera così prolissa." % verbs["you2"])
        entity.act("Non riesce ad %s adeguatamente e si impappina." % verbs["it2"])
        return False

    argument = put_final_dot(argument)

    # Mostra a tutti ciò che il giocatore vuole esprimere
    if "$n" in argument:
        argument = color_first_upper(argument)
        entity.act(argument.replace("$n", entity.name), TO.ENTITY)
        entity.act(argument, TO.OTHERS)
    else:
        entity.act("%s %s" % (entity.name, argument), TO.ENTITY)
        entity.act("$n %s" % argument, TO.OTHERS)

    force_return = check_trigger(entity, "after_emote", entity, argument, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "emote <gesto o espressione da esprimere>\n"
#- Fine Funzione -
