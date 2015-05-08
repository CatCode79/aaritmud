# -*- coding: utf-8 -*-

"""
Comando per sedersi.
"""

#= IMPORT ======================================================================

from src.enums      import TO, POSITION
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[mediumwood]sedere[close]",
         "you2"       : "[mediumwood]sederti[close]",
         "you"        : "[mediumwood]siedi[close]",
         "it"         : "[mediumwood]siede[close]",
         "noun"       : "[mediumwood]sedut$o[close]"}


#= FUNZIONI ====================================================================

def command_sit(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.position == POSITION.SLEEP:
        entity.send_output("Ti %s, ma solo nei tuoi sogni!" % verbs["you"])
        entity.act("$n si rannicchia nel sonno.", TO.OTHERS)
        return False
    elif entity.position == POSITION.SIT:
        entity.act("Sposti a destra e a sinistra il bacino cercando una posizione da %s più comoda." % verbs["noun"], TO.ENTITY)
        entity.act("$n sposta a destra e a sinistra il bacino cercando una posizione da %s più comoda." % verbs["noun"], TO.OTHERS)
        return False

    force_return = check_trigger(entity, "before_sit", entity, behavioured)
    if force_return:
        return True

    if entity.position == POSITION.REST:
        entity.act("Smetti di riposare e ti %s." % verbs["you"], TO.ENTITY)
        entity.act("$n smette di riposare e si %s." % verbs["it"], TO.OTHERS)
    elif entity.position == POSITION.STAND:
        entity.act("Ti %s." % verbs["you"], TO.ENTITY)
        entity.act("$n si %s." % verbs["it"], TO.OTHERS)
    elif entity.position == POSITION.KNEE:
        entity.act("Alzi un ginocchio dopo l'altro e ti %s." % verbs["you"], TO.ENTITY)
        entity.act("$n alza un ginocchio dopo l'altro e si %s." % verbs["it"], TO.OTHERS)

    entity.position = POSITION.SIT

    force_return = check_trigger(entity, "after_sit", entity, behavioured)
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
    syntax += "sit\n"
    syntax += "sit <un mobile>\n"

    return syntax
#- Fine Funzione -
