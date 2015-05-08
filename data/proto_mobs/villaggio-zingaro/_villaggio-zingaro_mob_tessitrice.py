# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# - Alle ultime luci della sera la tessitrice cominicia a mutare e si trasforma
#   nel barbagianni.
# - Il sunset è alle 19


#= TO DO =======================================================================

# passare gli oggetti fra i due (all'inizio il medaglione)
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

BAGGIA_PROTO_CODE = "villaggio-zingaro_mob_tessitrice-barbagianni"


#= CODE ========================================================================

def on_sunset(tessitrice):
    barbagianni = Mob(BAGGIA_PROTO_CODE)
    barbagianni.inject(tessitrice.location)

    for content in tessitrice.iter_contains():
        content.from_location()
        content.to_location(barbagianni)

    command_yell(tessitrice, "Aahhh%s Dolore%s" % (random_marks(0, 2), random_marks(0, 3)))

    barbagianni.act("Ti origini da $N e sei $n.", TO.ENTITY, tessitrice)
    barbagianni.act("In un istante $N si trasforma in $n!", TO.OTHERS, tessitrice)
    barbagianni.act("$n si origina da te!", TO.TARGET, tessitrice)

    tessitrice.extract(1)
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
