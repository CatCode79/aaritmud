# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.enums import FLAG, TO


#= FUNZIONI ====================================================================

def before_touched(entity, target, descr, detail, behavioure):
    if FLAG.NO_LOOK_LIST in target.flags:
        target.flags -= FLAG.NO_LOOK_LIST
        target.act("Collochi in modo più visibile $N.", TO.ENTITY, entity)
        target.act("$n colloca $N in modo più visibile.", TO.OTHERS, entity)
#- Fine Funzione -


def before_getted(entity, target, location, behavioured):
    if FLAG.NO_LOOK_LIST in target.flags:
        target.act("$N era misteriosamente nascosto qui.", TO.OTHERS)
        target.act("$N era misteriosamente nascosto qui.", TO.ENTITY)
#- Fine Funzione -
