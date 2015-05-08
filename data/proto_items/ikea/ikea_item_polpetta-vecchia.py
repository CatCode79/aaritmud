# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random
from src.defer    import defer
from src.enums    import TO, FLAG, POSITION


#= COSTANTI ====================================================================

TIME_DELAY = 10
polpetta_long = "disgustosamente ricoperta di [darkkhaki]muco colante[close]"

#= FUNZIONI ====================================================================

def before_eated(entity, polpetta, devour, swallow, behavioured):
    if random.randint(0, 1) == 1:
        entity.act("Il tuo spirito di sopravvivenza prende il sopravvento e blocca il gesto sconsiderato.", TO.ENTITY)
        entity.act("$n tenta un gesto ma poi cambia idea.", TO.OTHERS, polpetta)
        entity.act("$N pensa di mangiarti ma poi cambia idea $n.", TO.TARGET, polpetta)
        return True


def after_eated(entity, polpetta, devour, swallow, behavioured):
    defer(TIME_DELAY, nausea, entity, polpetta)


def nausea(entity, polpetta):
    # Può capitare visto che questa funzione viene usata in una defer
    if not polpetta or not entity:
        return

    entity.act("Dal profondo giunge un fetido lezzo che ti induce un certo tremito.", TO.ENTITY)
    entity.act("$n è scosso da un tremito improvviso.", TO.OTHERS, polpetta)
    entity.act("Ti vendichi inducendo le prime avvisaglie in $n.", TO.TARGET, polpetta)
    defer(TIME_DELAY, puke_polpetta, entity, polpetta)
#- Fine Funzione


def puke_polpetta(entity, polpetta):
    # Può capitare visto che questa funzione viene usata in una defer
    if not polpetta or not entity:
        return

    if FLAG.INGESTED not in polpetta.flags:
        return

    entity.act("Sei percorso da tremendi conati, cadi in ginocchio e vomiti $N.", TO.ENTITY, polpetta)
    entity.act("$n è preda di strani tremori, cade in ginocchio e vomita $N.", TO.OTHERS, polpetta)
    entity.act("Ti fai liberare dallo stomaco di $n.", TO.TARGET, polpetta)
    entity.position = POSITION.KNEE
    polpetta.flags -= FLAG.INGESTED
    polpetta.extract(1)
    polpetta.inject(entity.location)
    polpetta.long  = "$N " +  polpetta_long
#- Fine Funzione
