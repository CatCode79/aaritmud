# -*- coding: utf-8 -*-

"""
Comando per inginocchiarsi.
"""


#= IMPORT ======================================================================

from src.enums      import TO, POSITION
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[darkred]inginocchiare[close]",
         "you2"       : "[darkred]inginocchiarti[close]",
         "you"        : "[darkred]inginocchi[close]",
         "it"         : "[darkred]inginocchia[close]"}


#= FUNZIONI ====================================================================

def command_knee(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.position == POSITION.SLEEP:
        entity.send_output("Ti %s, ma solo nei tuoi sogni!" % verbs["you"])
        entity.act("$n si agita spostandosi su di un lato.", TO.OTHERS)
        return False
    elif entity.position == POSITION.KNEE:
        entity.act("Sposti di un poco le ginocchia cercando una posizione più comoda.", TO.ENTITY)
        entity.act("$n sposta di un poco le ginocchia cercando una posizione più comoda.", TO.OTHERS)
        return False

    force_return = check_trigger(entity, "before_knee", entity, behavioured)
    if force_return:
        return True

    if entity.position == POSITION.REST:
        entity.act("Smetti di riposare e ti %s." % verbs["you"], TO.ENTITY)
        entity.act("$n smette di riposare e si %s." % verbs["it"], TO.OTHERS)
    elif entity.position == POSITION.STAND:
        entity.act("Ti %s." % verbs["you"], TO.ENTITY)
        entity.act("$n si %s." % verbs["it"], TO.OTHERS)
    elif entity.position == POSITION.SIT:
        entity.act("Scivoli lentamente in avanti e ti %s." % verbs["you"], TO.ENTITY)
        entity.act("$n scivola lentamente in avanti e si %s." % verbs["it"], TO.OTHERS)

    entity.position = POSITION.KNEE

    force_return = check_trigger(entity, "before_knee", entity, behavioured)
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
    syntax += "knee\n"

    return syntax
#- Fine Funzione -
