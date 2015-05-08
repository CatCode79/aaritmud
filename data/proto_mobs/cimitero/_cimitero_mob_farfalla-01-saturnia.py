# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Sistema di riproduzione e conservazione della
# farfalla / bruco saturnia karpuridae

#= TO DO LIST ==================================================================


#= IMPORT ======================================================================

import random

from src.defer import defer, defer_random_time
from src.database import database
from src.log import log

from src.enums import SECTOR, TO
from src.item  import Item
from src.mob   import Mob

from src.commands.command_say import command_say


#= COSTANTI ====================================================================

PROTO_EGG_CODE     = "cimitero_item_uovo-saturnia"
PROTO_CATERPILLAR_CODES = ["cimitero_mob_bruco-01-saturnia",
                       "cimitero_mob_bruco-02-saturnia", 
                       "cimitero_mob_bruco-03-saturnia", 
                       "cimitero_mob_bruco-04-saturnia"] 

PROTO_CHRYSALIS_CODE   = "cimitero_item_crisalide-viva"
PROTO_BUTTERFLY_CODE = "cimitero_mob_farfalla-01-saturnia"

#= TROUBLE =====================================================================

def on_reset(butterfly):
    if not butterfly:
        log.bug("butterfly non è un parametro valido: %r" % butterfly)
        return

    start_deposing(butterfly)
#- Fine Funzione -


def on_booting(butterfly):
    if not butterfly:
        log.bug("butterfly non è un parametro valido: %r" % butterfly)
        return

    start_deposing(butterfly)
#- Fine Funzione -


def generic_creation(parent, proto_code, show_act=False):
    if not parent:
        log.bug("parent non è un parametro valido: %r" % parent)
        return None

    if not proto_code:
        log.bug("proto_code non è un parametro valido: %r" % proto_code)
        return None

    # Dà una controllatina a chi contiene il parente
    if not parent.location:
        log.bug("parent.location per qualche strano motivo è %r con codice %s e parent %s" % (
            parent.location, proto_code, parent.prototype.code))
        return None

    # Si assicura che il codice passato esista
    if proto_code in database["proto_items"]:
        proto_son = database["proto_items"][proto_code]
    elif proto_code in database["proto_mobs"]:
        proto_son = database["proto_mobs"][proto_code]
    else:
        log.bug("Il codice %s non è stato trovato nel database" % proto_code, log_stack=False)
        return None

    if show_act:
        parent.act("My name is $n: preparazione all'evoluzione!", TO.OTHERS)
        parent.act("My name is $n: preparazione all'evoluzione!", TO.ENTITY)

    # Se eccede il numero di entità definito in MaxGlobalQuantity allora esce
    if proto.has_reached_max_global_quantity():
    #if proto_son.max_global_quantity != 0 and proto_son.current_global_quantity >= proto_son.max_global_quantity:
        if show_act:
            parent.act("My name is $n: troppi %s!" % proto_code, TO.OTHERS)
            parent.act("My name is $n: troppi %s!" % proto_code, TO.ENTITY)
        if random.randint(1, 5) == 1:
            # Faccio il death istantaneo per verificare che non sia qui il
            # problema da un certo punto in poi pare che le uova non si
            # schiudano più anche senza che vi sian pulcini
            #defer_random_time(150, 300), death, parent)
            if show_act:
                parent.act("My name is $n: muoio!", TO.OTHERS)
                parent.act("My name is $n: muoio!", TO.ENTITY)
            death(parent)
        else:
            defer_random_time(150, 300, start_deposing , parent)
            if show_act:
                parent.act("My name is $n I'll try later!", TO.OTHERS)
                parent.act("My name is $n I'll try later!", TO.ENTITY)
        # Esce da qui in tutti e due i casi
        return None

    # Crea un nuovo figlio
    type = proto_code.split("_")[1]
    if type == "mob":
        son = Mob(proto_code)
    elif type == "item":
        son = Item(proto_code)
    else:
        log.bug("type non è valido con codice %s: %s" % (proto_code, type))
        return None

    if not son:
        log.bug("Non è stato possibile creare un figlio con codice %s: %r" % (proto_code, son), log_stack=False)
        return None

    if show_act:
        parent.act("My name is $n: son $N created!", TO.OTHERS, son)
        parent.act("My name is $n: son $N created!", TO.ENTITY, son)

    return son
#- Fine Funzione -


def start_deposing(butterfly):
    if not butterfly:
        log.bug("butterfly non è un parametro valido: %r" % butterfly)
        return None

    egg = generic_creation(butterfly, PROTO_EGG_CODE)
    if not egg:
        # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
        return

    # Inserisce l'uovo in gioco
    egg.inject(butterfly.location)

    # Tra un po' farà nascere il bruco dall'uovo
    defer(10, caterpillar_born, egg, butterfly)

    # la farfalla farà un altro uovo
    defer_random_time(10, 100, start_deposing, butterfly)
#- Fine Funzione


def caterpillar_born(egg, butterfly):
    if not egg:
        log.bug("egg non è un parametro valido: %r" % egg)
        return None

    if not butterfly:
        log.bug("butterfly non è un parametro valido: %r" % butterfly)
        return None

    caterpillar = generic_creation(egg, random.choice(PROTO_CATERPILLAR_CODES))
    if not caterpillar:
        # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
        return

    # @GATTO: Veramente si vuole questa cosa?
    # @GATTO: Altrimenti il check sottostante dei settori lo puoi fare aggiungendo:
    # @GATTO: if location.IS_ROOM and room.sector not in [...]
    # @GATTO: così fai funzionare il tutto anche il zone non room, e se room
    # @GATTO: solo per quei settori
    # @GATTO c'è un caso simile nella funzione più sotto
    location = egg.location
    if not location.IS_ROOM:
        return

    # Se il settore della stanza non è corretto esce
    #if location.sector not in (SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND, SECTOR.HOUSE):
    #    return

    # Se l'uovo nel frattempo già non si trova più tra gli oggetti allora esce
    if egg.code not in database["items"]:
        return

    # Rimuove l'uovo dalla stanza e dal database
    egg.extract(1)

    # Inserisce il bruco nel gioco
    caterpillar.inject(location)

    # Avvisiamo tutti quanti del lieto evento
    caterpillar.act("$N si schiude e se ne esce $n!", TO.OTHERS, egg)
    caterpillar.act("Nasci da $N e sei un $n.", TO.ENTITY, egg)
    caterpillar.act("$n nasce da te!", TO.TARGET, egg)

    # Ora che è nato, è certo contento e lo dirà al mondo!
    #defer_random_time(15, 30), command_say, caterpillar, "Nemmeno la morte ti può salvare da me!")
    defer_random_time(60, 80, caterpillar_chrysalis, caterpillar, butterfly)
#- Fine Funzione -


def caterpillar_chrysalis(caterpillar, mother):
    if not caterpillar:
        log.bug("caterpillar non è un parametro valido: %r" % caterpillar)
        return

    if not mother:
        log.bug("mother non è un parametro valido: %r" % mother)
        return

    butterfly_chrysalis = generic_creation(caterpillar, PROTO_CHRYSALIS_CODE)

    if not butterfly_chrysalis:
        # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
        return

    # Se il bruco nel frattempo non si trova più tra i mob allora esce
    if caterpillar.code not in database["mobs"]:
        return

    location = caterpillar.location
    if not location:
        log.bug("location non valida: %r" % location)
        return
 
    # Rimuove il bruco
    caterpillar.extract(1)

    # Inserisce la crisalide
    butterfly_chrysalis.inject(location)

    butterfly_chrysalis.act("$N s'è inbozzolato in $n", TO.OTHERS, caterpillar)
    butterfly_chrysalis.act("$N s'è inbozzolato in $n", TO.ENTITY, caterpillar)

    defer_random_time(60, 80, chrysalis_open, butterfly_chrysalis, mother)

def chrysalis_open(chrysalis, mother):
    if not chrysalis:
        log.bug("chrysalis non è un parametro valido: %r" % chrysalis)
        return

    if not mother:
        log.bug("mother non è un parametro valido: %r" % mother)
        return

    baby_butterfly = generic_creation(chrysalis, PROTO_BUTTERFLY_CODE)
    if not baby_butterfly:
        # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
        return

    location = chrysalis.location
    if not location.IS_ROOM:
        return

    # Se il settore della stanza non è corretto esce
    #if location.sector not in (SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND, SECTOR.HOUSE):
    #    return

    # Se la crisalide  nel frattempo non si trova più tra i mob allora esce
    if chrysalis.code not in database["items"]:
        return

    # Rimuove la crisalide dalla stanza e dal database,
    chrysalis.extract(1)

    # Imposta tutti i riferimenti per la farfalla
    baby_butterfly.inject(location)

    # shortizza la farfalla..
    #baby_butterfly.short = "una [red]farfalla[close]"

    # Avvisiamo tutti quanti del lieto evento
    baby_butterfly.act("$N non è più un piccolino ma $n!", TO.OTHERS, chrysalis)
    baby_butterfly.act("Ti origini da $N e sei un $n.", TO.ENTITY, chrysalis)
    baby_butterfly.act("$n nasce da te!", TO.TARGET, chrysalis)

    # Ora che è nato, è certo contento e lo dirà al mondo!
    #defer_random_time(15, 30), command_say, baby_butterfly, "Ero piccolo ma adesso non più!")

    # Ora che è cresciuta comincerà a depositare
    defer_random_time(35, 40, start_deposing, baby_butterfly)
#- Fine Funzione -


def death(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # Se l'entità nel frattempo non si trova più nel database allora esce
    if entity.code not in database[entity.ACCESS_ATTR]:
        return

    # Avvisa tutti del tristo evento
    entity.act("$N non è più fra noi...", TO.OTHERS, entity)
    entity.act("$N non è più fra noi...", TO.ENTITY, entity)
    entity.act("È ora di morire!", TO.TARGET, entity)

    # Rimuove l'entità dalla locazione e dal database
    entity.extract(1)
#- Fine Funzione -
