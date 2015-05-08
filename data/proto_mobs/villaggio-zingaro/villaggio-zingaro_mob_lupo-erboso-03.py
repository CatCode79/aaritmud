# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# - Alle prime luci dell'alba il barbagianni cominicia a mutare e si trasforma
# nella ragazza tessitrice.
# - Il sunrise è alle 7 ma forse meglio le 6 con il dawn_hour


#= TO DO =======================================================================

# passare gli oggetti della bestiola alla ragazza (all'inizio il medaglione)
# per gli altri item forse è il caso di fare un chk sul peso...
# potrebbe anche mollare tutto a terra e poi in versione ragazza raccattare le
# vesti, forse semplicemente di behaviour?


#= IMPORT ======================================================================

from src.defer   import defer
from src.enums   import TO
from src.log     import log
from src.item    import Item
from src.utility import random_marks

from src.commands.command_follow import command_follow


#= COSTANTI ====================================================================

PROTO_DOSSO_CODE     = "villaggio-zingaro_item_dosso-erboso-03"


#= CODE ========================================================================

def on_sunrise(lupo):
    if not lupo:
        log.bug("lupo non è un parametro valido: %r" % lupo)
        return

    dosso = Item(PROTO_DOSSO_CODE)
    dosso.inject(lupo.location)

    dosso.act("Ti origini da $N e sei $n.", TO.ENTITY, lupo)
    dosso.act("$N emette raccapriccianti guaiti e si trasforma in $n!", TO.OTHERS, lupo)
    dosso.act("$n si origina da te!", TO.TARGET, lupo)

    lupo.stop_repop()
    lupo.extract(1)
#- Fine Funzione -


def on_reset(lupotto):
    defer(1, command_follow, lupotto, "lupa")
#- Fine Funzione -
