# -*- coding: utf-8 -*-

"""
Comando per riposare.
"""

#= IMPORT ======================================================================

from src.enums      import TO, POSITION
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[cornflowerblue]riposare[close]",
         "you2"       : "[cornflowerblue]riposarti[close]"}


#= FUNZIONI ====================================================================

def command_rest(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.position == POSITION.SLEEP:
        entity.send_output("Ti accomodi a %s, ma solo nei tuoi sogni!" % verbs["infinitive"])
        entity.act("$ si stiracchia nel sonno.", TO.OTHERS)
        return False
    elif entity.position == POSITION.REST:
        entity.act("Ti allunghi cercando una posizione più comoda per te", TO.ENTITY)
        entity.act("$n allunga alla grandissima cercando una posizione più comoda." % verbs["infinitive"], TO.ENTITY)
        return False

    force_return = check_trigger(entity, "before_rest", entity, behavioured)
    if force_return:
        return True

    if entity.position == POSITION.SIT:
        entity.act("Stuf$o di stare sedut$o ti metti a %s." % verbs["infinitive"], TO.ENTITY)
        entity.act("$n si mette a %s." % verbs["infinitive"], TO.OTHERS)
    elif entity.position == POSITION.STAND:
        entity.act("Ti metti a %s." % verbs["infinitive"], TO.ENTITY)
        entity.act("$n mette a %s." % verbs["infinitive"], TO.OTHERS)
    elif entity.position == POSITION.KNEE:
        entity.act("Alzi un ginocchio dopo l'altro e ti metti a %s." % verbs["infinitive"], TO.ENTITY)
        entity.act("$n alza un ginocchio dopo l'altro e si mette a %s." % verbs["infinitive"], TO.OTHERS)

    entity.position = POSITION.REST

    force_return = check_trigger(entity, "after_rest", entity, behavioured)
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
    syntax += "rest\n"

    return syntax
#- Fine Funzione -
