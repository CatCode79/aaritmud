# -*- coding: utf-8 -*-

"""
Comando per svegliare qualcuno.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.enums      import POSITION, TO
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[goldenrod]svegliare[close]",
         "noun"       : "[goldenrod]svegli$o[close]",
         "you2"       : "[goldenrod]svegliarti[close]",
         "you"        : "[goldenrod]svegli[close]",
         "it"         : "[goldenrod]sveglia[close]",
         "it2"        : "[goldenrod]svegliandol$O[close]"}


#= FUNZIONI ====================================================================

def command_wake(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        if entity.position == POSITION.SLEEP:
            force_return = check_trigger(entity, "before_wake", entity, None, behavioured)
            if force_return:
                return True

            entity.send_output("Ti %s e ti rimetti in piedi" % verbs["you"])
            entity.act("$n si %s e si rimette in piedi." % verbs["it"], TO.OTHERS)
            entity.position = POSITION.STAND
            return True

            force_return = check_trigger(entity, "after_wake", entity, None, behavioured)
            if force_return:
                return True
        else:
            entity.act("Non è un sogno! Sei già %s." % verbs["noun"], TO.ENTITY)
            entity.act("$n scuote la testa come a voler scacciare i [darkcyan]demoni del sonno[close]", TO.OTHERS)
            return False

    if entity.position == POSITION.SLEEP:
        entity.send_output("%s qualcuno ma solo nei tuoi sogni!" % color_first_upper(verbs["you"]))
        entity.act("$n si muove nel sonno allungando una hand come a scuotere qualcosa", TO.OTHERS)
        return False

    arg1, argument = one_argument(argument)
    target = entity.find_entity(arg1, entity_tables=["players", "mobs"], location=entity.location)
    if not target:
        entity.act("Non c'è nessun [white]%s[close] qui." % arg1, TO.ENTITY)
        entity.act("$n si guarda attorno come a cercare qualcuno ma senza risultati.", TO.OTHERS)
        return False

    if target.position != POSITION.SLEEP:
        entity.act("Provi a %s $N, ma all'ultimo ti accorgi che non sta dormendo." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n prova a %s $N, ma all'ultimo si accorge che non sta dormendo." % verbs["infinitive"], TO.OTHERS, target)
        return False

    force_return = check_trigger(entity, "before_wake", entity, target, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_waked", entity, target, behavioured)
    if force_return:
        return True

    target.position = POSITION.REST
    entity.act("Con la $hand1 scuoti leggermente $N, %s." % VERBS["it2"], TO.ENTITY, target)
    entity.act("$n ti ha svegliat$O.", TO.TARGET, target)
    entity.act("$n con la $hand1 scuote leggermente $N %s." % VERBS["it2"], TO.OTHERS, target)

    force_return = check_trigger(entity, "after_wake", entity, target, behavioured)
    if force_return:
        return True

    force_return = check_trigger(target, "after_waked", entity, target, behavioured)
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
   syntax += "wake\n"
   syntax += "wake <un pg o un mob>\n"

   return syntax
#- Fine Funzione -
