# -*- coding: utf-8 -*-

#= DESCRIPTION =================================================================

# Anello che conferisce il NO_LOOK_LIST a chi lo indossa
# (TD) in futuro sarà un affect a dover fare la cosa
# Qui il problema è se l'anello viene rimosso in modo non canonico,
# ad esempio rimuovendo persistenze; la flag rimarrebbe addosso al pg
# temporaneamente c'è il trigger remove_persistence per lenire parzialmente  


#= IMPORT ======================================================================

from src.enums import FLAG, TO


#= FUNZIONI ====================================================================


def before_remove(entity, target, detail, chosen_part, behavioured):
    entity.flags -= FLAG.NO_LOOK_LIST
    entity.act("Magico potere del rivelamento.", TO.ENTITY, target)
    entity.act("$N appare lentamente dal nulla.", TO.OTHERS, target)
    entity.act("Riappari lentamente.", TO.TARGET, target)
#- Fine Funzione -


def after_wear(entity, target, chosen_part, chosen_mode, behavioured):
    entity.flags += FLAG.NO_LOOK_LIST
    entity.act("Magico potere dell'occultamento.", TO.ENTITY, target)
    entity.act("$N svanisce lentamente alla vista.", TO.OTHERS, target)
    entity.act("Svanisci quasi completamente.", TO.TARGET, target)
#- Fine Funzione -


def remove_persistence(anello):
    if anello.location.IS_PLAYER:
        anello.location -= FLAG.NO_LOOK_LIST
#- Fine Funzione -
