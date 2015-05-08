# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random
from src.enums import TO


#= FUNZIONI ====================================================================

def before_touched(entity, pallotta, descr, detail, behavioured):
    # Se quello che si tocca non è una extra
    if not detail or not detail.IS_EXTRA:
        return False

    # Se la extra non è quella dei peli allora esce
    if "peli" not in detail.keywords:
        return False

    if entity.max_life >= entity.life + 10:
        # (TD) nessun messaggio di act in questo caso? io li inserirei
        entity.life += 10
        entity.act("$n invoca il tuo potere", TO.TARGET, pallotta)
        entity.act("Il sacro potere di $N ti pervade donandoti nuova forza vitale!", TO.ENTITY, pallotta)
        entity.act("$n invoca con successo il sacro potere di $N che ne incornicia i tratti di nuovo vigore!", TO.OTHERS, pallotta)
        if not random.randint(1, 10):
            entity.act("$n t'invoca ma tu te ne vai.", TO.TARGET, pallotta)
            entity.act("Senti che non era ancora tempo e $N svanisce in una nuvoletta [close]verde[close]!", TO.ENTITY, pallotta)
            entity.act("$n magicamente fa sparire $N!", TO.OTHERS, pallotta)
            extract(pallotta)
            return True
        return True
    else: 
        #entity.act("$n si affanna inutilmente invocando il tuo potere", TO.TARGET, pallotta)
        #entity.act("Non senti nulla di particolare accarezzando $N!", TO.ENTITY, pallotta)
        #entity.act("$n si affanna inutilmente toccando $N!", TO.OTHERS, pallotta)
        return False
#- Fine Funzione -
