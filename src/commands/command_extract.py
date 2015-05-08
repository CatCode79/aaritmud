# -*- coding: utf-8 -*-

"""
Comando che serve a rimuovere dal gioco un'entità.
"""


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.enums   import TO
from src.log     import log
from src.utility import one_argument, quantity_argument


#= FUNZIONI ====================================================================

def command_extract(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_extract")
        entity.send_output(syntax, break_line=False)
        return False

    arg, argument = one_argument(argument)
    if argument:
        quantity, argument = quantity_argument(argument)
    else:
        quantity = 1

    target = entity.find_entity_extensively(arg, quantity=quantity)
    if not target:
        entity.send_output("Nessuna entità trovata con argomento [white]%s[close]." % arg)
        return False

    if target.IS_PLAYER:
        entity.send_output("Non ti è possibile estrarre dei personaggi, se c'è un problema con un giocatore contattare i capoccia del Mud.")
        return False

    if quantity == 0:
        quantity = target.quantity

    entity.act("Esegui uno extract su $N!", TO.ENTITY, target)
    entity.act("$n esegue un extract su $N!", TO.OTHERS, target)
    target.act("$n esegue un extract su di te!", TO.TARGET, target)
    target.extract(quantity, use_repop=True)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "extract\n"
    syntax += "extract <vittima>\n"
    syntax += "extract <vittima> <quantità>\n"

    return syntax
#- Fine Funzione -
