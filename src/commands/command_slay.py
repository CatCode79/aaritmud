# -*- coding: utf-8 -*-

"""
Comando che serve a far sparire mob o oggetto fastidiosi.
"""


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.enums   import TO, TRUST
from src.log     import log


#= FUNZIONI ====================================================================

def command_slay(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_slay")
        entity.send_output(syntax, break_line=False)
        return False

    target = entity.find_entity_extensively(argument)
    if not target:
        entity.send_output("Nessuna entità trovata con argomento [green]%s[close]." % argument)
        return False

    if target.IS_PLAYER and entity.trust < TRUST.IMPLEMENTOR:
        entity.send_output("Non ti è possibile slayare dei personaggi, se c'è un problema con un giocatore contattare i capoccia del Mud.")
        return False

    entity.act("Esegui uno slay su $N!", TO.ENTITY, target)
    entity.act("$n esegue uno slay su $N!", TO.OTHERS, target)
    target.act("$n esegue uno slay su di te!", TO.TARGET, target)
    target.dies(opponent=None)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "slay\n"
    syntax += "slay <vittima>\n"

    return syntax
#- Fine Funzione -
