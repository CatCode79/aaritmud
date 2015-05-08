# -*- coding: utf-8 -*-

"""
Skill per eseguire automaticamente un controattacco iniziale all'attaccante
prendendolo di sorpresa.
"""


#= IMPORT ======================================================================

import random

from src.config import config
from src.enums  import TO
from src.log    import log
from src.skill  import check_skill


#= COSTANTI ====================================================================

VERBS = {}
VERBS["infinitive"] = "[red]contrastare[close]"
VERBS["you2"]     = "[red]contrastarti[close]"
VERBS["noun"]     = "[red]contrastarl$O[close]"

STATS = ("speed", "intelligence")


#= FUNZIONI ====================================================================

# Questa skill non è digitabile quindi non ha skill_counter


def skill_counter(entity, target, verbs=VERBS, silent=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return "failure"

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return "failure"

    # -------------------------------------------------------------------------

    if "counter" not in entity.skills:
        entity.skills["counter"] = 0

    if entity.skills["counter"] <= 0:
        return "failure"

    skill_result = check_skill(entity, target, "counter")
    if skill_result < config.clumsy_value:
        if not silent:
            entity.act("\nTenti maldestramente di %s di $N ma ti ingarbugli e perdi il ritmo dell'attacco." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n tenta maldestramente di %s di $N ma si ingarbuglia e perde il ritmo dell'attacco." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n tenta maldestramente di %s ma si ingarbuglia e perde il ritmo dell'attacco." % verbs["you2"], TO.TARGET, target)
        return "clumsy"
    elif skill_result < config.failure_value:
        # Nessun messaggio se v'è il fallimento
        return "failure"
    elif skill_result < config.success_value:
        if not silent:
            entity.act("\nRiesci ad anticipare il ritmo del colpo di $N e %s." % verbs["noun"], TO.ENTITY, target)
            entity.act("$n riesce ad anticipare il ritmo del colpo di $N e %s." % verbs["noun"], TO.OTHERS, target)
            entity.act("$n riesce ad anticipare il ritmo del tuo colpo e %s."% verbs["you2"], TO.TARGET, target)
        return "success"
    else:
        if not silent:
            entity.act("\nRiesci magistralmente a %s il colpo di $N prendendol$O alla sprovvista." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n riesce magistralmente a %s il colpo di $N prendendol$O alla sprovvista." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n riesce magistralmente a %s il tuo colpo prendendoti alla sprovvista."% verbs["infinitive"], TO.TARGET, target)
        return "masterly"
#- Fine Funzione -
