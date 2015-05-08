# -*- coding: utf-8 -*-


#= DESCRIZIONE =================================================================

# - Alle prime luci dell'alba il barbagianni cominicia a mutare e si trasforma
#   nella ragazza tessitrice.
# - Il sunrise è alle 7 ma forse meglio le 6 con il dawn_hour


#= TO DO =======================================================================

# passare gli oggetti della bestiola alla ragazza (all'inizio il medaglione)
# per gli altri item forse è il caso di fare un chk sul peso...
# potrebbe anche mollare tutto a terra e poi in versione ragazza raccattare le
# vesti, forse semplicemente di behaviour?


#= IMPORT ======================================================================

from src.enums   import TO
from src.log     import log
from src.mob     import Mob
from src.utility import random_marks

from src.commands.command_yell import command_yell


#= COSTANTI ====================================================================

TESSY_PROTO_CODE = "villaggio-zingaro_mob_tessitrice"


#= CODE ========================================================================

def on_sunrise(barbagianni):
    tessy = Mob(TESSY_PROTO_CODE)
    tessy.inject(barbagianni.location)

    for content in barbagianni.iter_contains():
        content.from_location()
        content.to_location(tessy)
        #Nel caso volessi resettare lo slot dell'item:
        #content.wear_mode.clear()

    command_yell(barbagianni, "Screeeh%s Scretch%s" % (random_marks(0, 2), random_marks(0, 3)))

    tessy.act("Ti origini da $N e sei $n.", TO.ENTITY, barbagianni)
    tessy.act("In un istante $N si trasforma in  $n!", TO.OTHERS, barbagianni)
    tessy.act("$n si origina da te!", TO.TARGET, barbagianni)

    #print "barbagianni proto glob qty prima dell'estract", barbagianni.current_global_quantity
    barbagianni.extract(1)
#- Fine Funzione -


def before_killed(entity, target, attack, destroy, behavioured):
    target.act("$n ti guarda con occhio espressivo e ti convince a desistere dall'uccidere.", TO.ENTITY, entity)
    target.act("Fai desistere $n dall'ucciderti!", TO.TARGET, entity)
    target.act("$n redarguisce severamente $N.", TO.OTHERS, entity)
    return True
#- Fine Funzione -

def before_kicked(entity, target, foo, behavioured):
    target.act("$n ti guarda con occhio espressivo e ti convince a desistere ed abbassi il $FOOT.", TO.ENTITY, entity)
    target.act("Fai desistere $n dal calciarti!", TO.TARGET, entity)
    target.act("$n redarguisce severamente $N.", TO.OTHERS, entity)
    return True
#- Fine Funzione -
