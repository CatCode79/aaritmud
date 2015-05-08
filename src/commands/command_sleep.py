# -*- coding: utf-8 -*-

"""
Comando per addormentarsi.
"""


#= IMPORT ======================================================================

import random

from src.enums      import TO, POSITION
from src.gamescript import check_trigger
from src.log        import log


#= COSTANTI ====================================================================

# (TD) in realtà questo sistema di adrenalina era originariamente il sistema di
# stato mentale eventualmente da reimplementare
#ADRENALINE_LIMIT = 10

VERBS = {"infinitive" : "[neonblue]dormire[close]",
         "you2"       : "[neonblue]dormirci[close]",
         "you"        : "[neonblue]dormi[close]",
         "it"         : "[neonblue]dorme[close]",
         "gerund"     : "[neonblue]dormendo[close]"}


#= FUNZIONI ====================================================================

def command_sleep(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.position == POSITION.SLEEP:
        entity.send_output("Stai già %s, più di così non puoi!" % verbs["gerund"])
        entity.act("$n russa profondamente.", TO.OTHERS)
        return False

    force_return = check_trigger(entity, "before_sleep", entity, behavioured)
    if force_return:
        return True

    elif entity.position == POSITION.REST:
        #if entity.adrenaline > (ADRENALINE_LIMIT + random.randint(0, 0.2 * ADRENALINE_LIMIT)):
        #    entity.act("Difficile %s con tutta questa eccitazione in corpo." % verbs["infinitive"], TO.ENTITY)
        #    entity.act("$n socchiude gli occhi cercando di %s, ma è troppo irrequieto." % verbs["infinitive"], TO.OTHERS)
        #    return False
        entity.act("È tempo di riposare le stanche membra.", TO.ENTITY)
        entity.act("$n chiude gli occhi e s'assopisce lentamente.", TO.OTHERS)
    elif entity.position == POSITION.SIT:
        #if entity.adrenaline > (ADRENALINE_LIMIT + random.randint(0, 0.3/2 * ADRENALINE_LIMIT)):
        #    entity.act("Difficile %s con tutta questa eccitazione in corpo." % verbs["infinitive"], TO.ENTITY)
        #    entity.act("$n socchiude gli occhi cercando di %s, ma è troppo irrequieto." % verbs["infinitive"], TO.OTHERS)
        #    return False
        entity.act("È tempo di distendersi e riposare le stanche membra.", TO.ENTITY)
        entity.act("$n si distende, chiude gli occhi e s'assopisce lentamente.", TO.OTHERS)
    elif entity.position == POSITION.KNEE:
        #if entity.adrenaline > (ADRENALINE_LIMIT + random.randint(0, 0.2 * ADRENALINE_LIMIT)):
        #    entity.act("Difficile %s con tutta questa eccitazione in corpo." % verbs["infinitive"], TO.ENTITY)
        #    entity.act("$n socchiude gli occhi cercando di %s, ma è troppo irrequieto." % verbs["infinitive"], TO.OTHERS)
        #    return False
        entity.act("Appoggi i palmi per terra, ti metti più comodo, chiudi gli occhi e scivoli nel sonno.", TO.ENTITY)
        entity.act("$n appoggia i palmi per terra, si distende, chiude gli occhi e s'assopisce lentamente.", TO.OTHERS)
    elif entity.position == POSITION.STAND:
        #if entity.adrenaline > (ADRENALINE_LIMIT + random.randint(0, 0.5 * ADRENALINE_LIMIT)):
        #    entity.act("Difficile %s con tutta questa eccitazione in corpo." % verbs["infinitive"], TO.ENTITY)
        #    entity.act("$n socchiude gli occhi cercando di %s, ma è troppo irrequieto" % verbs["infinitive"], TO.OTHERS)
        #    return False
        entity.act("Ti metti più comodo, chiudi gli occhi e ti lasci scivolare nel sonno.", TO.ENTITY)
        entity.act("$n si distende, chiude gli occhi e s'assopisce lentamente.", TO.OTHERS)

    entity.position = POSITION.SLEEP

    force_return = check_trigger(entity, "after_sleep", entity, behavioured)
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
    syntax += "sleep\n"

    return syntax
#- Fine Funzione -

