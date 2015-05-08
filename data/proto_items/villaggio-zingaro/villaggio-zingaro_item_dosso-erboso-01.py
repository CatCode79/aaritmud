# -*- coding: utf-8 -*-


#= DESCRIZIONE =================================================================

# Alle ultime luci della sera la tessitrice cominicia a mutare e si trasforma
# nel barbagianni.
# il sunset è alle 19


#= TODO ========================================================================

# - passare gli oggetti fra i due (all'inizio il medaglione)
# - per gli altri item forse è il caso di fare un chk sul peso...
# - potrebbe anche mollare tutto a terra e poi in versione ragazza raccattare le
#   vesti, forse semplicemente di behaviour?


#= IMPORT ======================================================================

from src.enums   import TO
from src.log     import log
from src.mob     import Mob
from src.utility import random_marks


#= COSTANTI ====================================================================

PROTO_LUPO_CODE = "villaggio-zingaro_mob_lupo-erboso-01"


#= CODE ========================================================================

def on_sunset(dosso):
    if not dosso:
        log.bug("dosso non è un parametro valido: %r" % dosso)
        return

    lupo = Mob(PROTO_LUPO_CODE)
    lupo.inject(dosso.location)

    #for content in tessitrice.iter_contains(use_reversed=True):
    #    content = content.from_location(content.quantity)
    #    content.to_location(barbagianni)

    lupo.act("Ti origini da $N e sei $n.", TO.ENTITY, dosso)
    lupo.act("$N emmette un risonante fruscio e si trasforma improvvisamente in $n!", TO.OTHERS, dosso)
    lupo.act("$n si origina da te!", TO.TARGET, dosso)

    dosso.stop_repop()
    dosso.extract(1)
#- Fine Funzione -
