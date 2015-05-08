# -*- coding: utf-8 -*-

"""
Comando per alzarsi da terra o da altro luogo.
"""

#= IMPORT ======================================================================

from src.gamescript import check_trigger
from src.log        import log
from src.enums      import TO, POSITION


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[aquamarine]alzare[close]",
         "you2"       : "[aquamarine]alzarti[close]",
         "you"        : "[aquamarine]alzi[close]",
         "it"         : "[aquamarine]alza[close]"}


#= FUNZIONI ====================================================================

def command_stand(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.position == POSITION.SLEEP:
        entity.send_output("Ti %s in piedi ma solo nei tuoi sogni!" % verbs["you"])
        entity.act("$n si gira nel sonno ed ora sta supino.")
        return False
    elif entity.position == POSITION.STAND:
        entity.act("Sei già in piedi.", TO.ENTITY)
        entity.act("$n si allunga sulle punte dei $feet come se volesse stare più in piedi di così.", TO.OTHERS)
        return False

    force_return = check_trigger(entity, "before_stand", entity, behavioured)
    if force_return:
        return True

    # (TD) da gestire forse anche il combattimento con ritardi sullo stand
    if entity.position == POSITION.REST:
        entity.act("Smetti di riposare e ti %s in piedi." % verbs["you"], TO.ENTITY)
        entity.act("$n smette di riposare e si %s in piedi." % verbs["it"], TO.OTHERS)
    elif entity.position == POSITION.SIT:
        entity.act("Ti %s in piedi." % verbs["you"], TO.ENTITY)
        entity.act("$n si %s in piedi." % verbs["it"], TO.OTHERS)
    elif entity.position == POSITION.KNEE:
        entity.act("Un ginocchio dopo l'altro e ti %s in piedi." % verbs["you"], TO.ENTITY)
        entity.act("Un ginocchio dopo l'altro e $n si %s in piedi." % verbs["it"], TO.OTHERS)

    entity.position = POSITION.STAND

    force_return = check_trigger(entity, "after_stand", entity, behavioured)
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
   syntax += "stand\n"

   return syntax
#- Fine Funzione -
