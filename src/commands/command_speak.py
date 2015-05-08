# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando che serve a risparmiare un'entità sconfitta.
"""

#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import FLAG
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[lightwood]parlare[close]"}


#= FUNZIONI ====================================================================

def command_speak(entity, argument="", verbs=VERBS):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        syntax = get_command_syntax(entity, "command_speak")
        entity.send_output(syntax, break_line=False)
        return False

    target = entity.find_entity_extensively(argument)
    if not target:
        entity.act("Non c'è nessuno [white]%s[close] qui attorno con cui puoi %s." % (argument, verbs["infinitive"]))
        entity.act("$n sembra stia cercando qualcuno qui attorno senza trovarlo.", TO.OTHERS)
        return False

    for dialog in target.dialogs:
        if dialog.code == "speak":
            break
    else:
        entity.send_output("%s non sembra avere molto da dirti." % target.get_name())
        return

    # (TD) aggiungere il check trigger

    # (TD) splittare target

    entity.flags += FLAG.CONVERSING
    entity.send_output(dialog.introduction)
    dialog.send_statement(target, entity)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "speak\n"
    return "speak <colui con cui vuoi dialogare>\n"
#- Fine Funzione -
