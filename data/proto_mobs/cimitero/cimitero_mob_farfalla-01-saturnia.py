# -*- coding: utf-8 -*-

"""
Sistema di riproduzione e conservazione della
farfalla / bruco saturnia karpuridae
"""

#= IMPORT ======================================================================

import random

from src.database import database
from src.defer    import defer, defer_random_time
from src.enums    import FLAG, SECTOR, TO
from src.item     import Item
from src.log      import log
from src.mob      import Mob


#= COSTANTI ====================================================================

PROTO_EGG_CODE          = "cimitero_item_uovo-saturnia"
PROTO_CATERPILLAR_CODES = ["cimitero_mob_bruco-01-saturnia",
                           "cimitero_mob_bruco-02-saturnia",
                           "cimitero_mob_bruco-03-saturnia",
                           "cimitero_mob_bruco-04-saturnia"]
PROTO_CHRYSALIS_CODE    = "cimitero_item_crisalide-viva"
PROTO_BUTTERFLY_CODE    = "cimitero_mob_farfalla-01-saturnia"


#= FUNZIONI ====================================================================

def on_reset(butterfly):
    start_deposing(butterfly)
#- Fine Funzione -


#la disattivo per scrupolo che non sia conflitto fra i due trigger
def off_on_booting(butterfly):
    start_deposing(butterfly)
#- Fine Funzione -


def start_deposing(butterfly):
    # E' normale visto che la funzione viene anche deferrata
    if not butterfly:
        return None

    egg = generic_creation(butterfly, PROTO_EGG_CODE)
    # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
    # oppure se la farfalla muore
    if not egg:
        return

    # Inserisce l'uovo in gioco
    egg.inject(butterfly.location)

    # Tra un po' farà nascere il bruco dall'uovo
    defer(10, from_egg_to_caterpillar, egg)

    # La farfalla farà un altro uovo
    defer_random_time(15, 20, start_deposing, butterfly)
#- Fine Funzione


def generic_creation(parent, proto_code, show_act=True):
    # E' normale visto che la funzione viene anche deferrata
    if not parent:
        return None

    # Si assicura che il codice passato esista
    if proto_code in database["proto_items"]:
        proto_son = database["proto_items"][proto_code]
    elif proto_code in database["proto_mobs"]:
        proto_son = database["proto_mobs"][proto_code]
    else:
        log.bug("Il codice %s non è stato trovato nel database" % proto_code, log_stack=False)
        return None

#    if show_act:
#        parent.act("My name is $n: preparazione all'evoluzione!", TO.OTHERS)

    # Se eccede il numero di entità definito in MaxGlobalQuantity allora esce
    if proto_son.has_reached_max_global_quantity():
    #if proto_son.max_global_quantity != 0 and proto_son.current_global_quantity >= proto_son.max_global_quantity:
        if show_act:
            parent.act("My name is $n: troppi %s!" % proto_code, TO.OTHERS)
            parent.act("My name is $n: troppi %s!" % proto_code, TO.ENTITY)
        if random.randint(1, 5) == 1:
            if show_act:
                parent.act("My name is $n: muoio!", TO.OTHERS)
                parent.act("My name is $n: muoio!", TO.ENTITY)
            death(parent)
        else:
            defer_random_time(60, 61, generic_creation, parent, proto_code)
            if show_act:
                parent.act("My name is $n I'll try later!", TO.OTHERS)
                parent.act("My name is $n I'll try later!", TO.ENTITY)
        # Esce da qui in tutti e due i casi
        return None

    # Crea un nuovo figlio
    son = proto_son.CONSTRUCTOR(proto_son.code)
    if show_act:
        parent.act("My name is $n: son $N created!", TO.OTHERS, son)
        parent.act("My name is $n: son $N created!", TO.ENTITY, son)

    return son
#- Fine Funzione -


def from_egg_to_caterpillar(egg):
    # E' normale visto che la funzione viene deferrata
    if not egg:
        return

    caterpillar = generic_creation(egg, random.choice(PROTO_CATERPILLAR_CODES))
    # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
    if not caterpillar:
        return

    # @GATTO: if location.IS_ROOM and room.sector not in [...]
    # @GATTO: così fai funzionare il tutto anche il zone non room, e se room
    # @GATTO: solo per quei settori
    if not egg.location.IS_ROOM:
        return

    caterpillar.inject(egg.location)
    # Avvisiamo tutti quanti del lieto evento
    caterpillar.act("$N si schiude e se ne esce $n!", TO.OTHERS, egg)
    caterpillar.act("Nasci da $N e sei un $n.", TO.ENTITY, egg)
    caterpillar.act("$n nasce da te!", TO.TARGET, egg)
    egg.extract(1)

    defer_random_time(20, 22, from_caterpillar_to_chrysalis, caterpillar)
#- Fine Funzione -


def from_caterpillar_to_chrysalis(caterpillar):
    # Se non è valido significa che è stato estratto prima che la deferred scattasse
    if not caterpillar:
        return

    chrysalis = generic_creation(caterpillar, PROTO_CHRYSALIS_CODE)
    # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
    if not chrysalis:
        return

    chrysalis.inject(caterpillar.location)
    chrysalis.act("$N s'è inbozzolato in $n", TO.OTHERS, caterpillar)
    chrysalis.act("$N s'è inbozzolato in $n", TO.ENTITY, caterpillar)
    caterpillar.extract(1)

    defer_random_time(20, 30, from_chrysalis_to_butterfly, chrysalis)
#- Fine Funzione -


def from_chrysalis_to_butterfly(chrysalis):
    # Se non è valido significa che è stato estratto prima che la deferred scattasse
    if not chrysalis:
        return

    baby_butterfly = generic_creation(chrysalis, PROTO_BUTTERFLY_CODE)
    # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
    if not baby_butterfly:
        return

    if not chrysalis.location.IS_ROOM:
        return

    baby_butterfly.inject(chrysalis.location)
    # Avvisiamo tutti quanti del lieto evento
    baby_butterfly.act("$N non è più un piccolino ma $n!", TO.OTHERS, chrysalis)
    baby_butterfly.act("$N non è più un piccolino ma $n!", TO.ENTITY, chrysalis)
    chrysalis.extract(1)

    # Ora che è cresciuta comincerà a depositare
    defer_random_time(35, 40, start_deposing, baby_butterfly)
#- Fine Funzione -


def death(entity):
    # Avvisa tutti del mesto evento
    entity.act("$N non è più fra noi...", TO.OTHERS, entity)
    entity.act("$N non è più fra noi...", TO.ENTITY, entity)
    entity.act("È ora di morire!", TO.TARGET, entity)

    # Rimuove l'entità dalla locazione e dal database
    entity.extract(1)
#- Fine Funzione -
