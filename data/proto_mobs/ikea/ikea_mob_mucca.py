# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================


#= IMPORT ======================================================================

from src.enums import TO, POSITION


#= CODE ====================================================================

def before_killed(entity, target, attack, destroy, behavioured):
    entity.act("$N ti guarda con occhio espressivo e ti convince a desistere dall'uccidere.", TO.ENTITY, target)
    entity.act("Fai desistere $n dall'ucciderti!", TO.TARGET, target)
    entity.act("$N redarguisce severamente $n.", TO.OTHERS, target)
    return True 
#- Fine Funzione -

def after_touched(player, mucca, descr, detail, behavioured):
    print "script mukka ikea: ", mucca.position
#- Fine Funzione -
