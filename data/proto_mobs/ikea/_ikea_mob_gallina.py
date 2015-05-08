# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Su Aarit le galline fanno anche le uova!
# Chiedimi come.

# - La gallina ogni tot tempo dovrebbe poter deporre un uovo ikea_item_uovo
# - Se non è in una room (inventario di qualcuno o altre buggerie) non depone
# - Se c'è già un altro uovo non depone


#= IMPORT ======================================================================

import random

from src.database import database
from src.defer    import defer, defer_random_time
from src.enums    import SECTOR, TO
from src.log      import log
from src.item     import Item
from src.mob      import Mob

from src.commands.command_say import command_say


#= COSTANTI ====================================================================

PROTO_EGG_CODE     = "ikea_item_uovo-gallina"
PROTO_CHICK_CODE   = "ikea_mob_pulcino"
PROTO_CHICKEN_CODE = "ikea_mob_gallina"

CHICK_SHORTS = {1 : "un [orange]galletto[close]",
                2 : "un [green]gallinaccio[close]",
                3 : "un [purple]galletto[close]",
                4 : "un piccolo [blue]gallo[close]"}


#= FUNZIONI ====================================================================

def on_reset(chicken):
    start_deposing(chicken)
#- Fine Funzione -


def on_booting(chicken):
    start_deposing(chicken)
#- Fine Funzione -


def generic_creation(parent, proto_code, show_act=True):
    # Si assicura che il codice passato esista
    if proto_code in database["proto_items"]:
        proto_son = database["proto_items"][proto_code]
    elif proto_code in database["proto_mobs"]:
        proto_son = database["proto_mobs"][proto_code]
    else:
        log.bug("Il codice %s non è stato trovato nel database" % proto_code, log_stack=False)
        return None

    if show_act:
        parent.act("My name is $n: deposing reloaded!", TO.OTHERS)
        parent.act("My name is $n: deposing reloaded!", TO.ENTITY)

    # Se eccede il numero di entità definito in MaxGlobalQuantity allora esce
    if proto_son.has_reached_max_global_quantity():
    #if proto_son.max_global_quantity != 0 and proto_son.current_global_quantity >= proto_son.max_global_quantity:
        if show_act:
            parent.act("My name is $n: ther'are too many %s!" % proto_code, TO.OTHERS)
            parent.act("My name is $n: ther'are too many %s!" % proto_code, TO.ENTITY)
        if random.randint(1, 5) == 1:
            # Faccio il death istantaneo per verificare che non sia qui il
            # problema da un certo punto in poi pare che le uova non si
            # schiudano più anche senza che vi sian pulcini
            #defer_random_time(150, 300), death, parent)
            if show_act:
                parent.act("My name is $n and I'll die now!", TO.OTHERS)
                parent.act("My name is $n and I'll die now!", TO.ENTITY)
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


def start_deposing(chicken):
    if not chicken:
        log.bug("chicken non è un parametro valido: %r" % chicken)
        return None

    egg = generic_creation(chicken, PROTO_EGG_CODE)
    if not egg:
        # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
        return

    # Inserisce l'uovo in gioco
    location = chicken.location
    egg.inject(location)

    # Tra un po' farà nascere il pulcino dall'uovo
    defer(10, chick_born, egg, chicken)

    # La gallina che canta è quella che ha fatto l'uovo e ne farà un altro
    defer_random_time(10, 100, start_deposing, chicken)
#- Fine Funzione


def chick_born(egg, chicken):
    if not egg:
        log.bug("egg non è un parametro valido: %r" % egg)
        return None

    if not chicken:
        log.bug("chicken non è un parametro valido: %r" % chicken)
        return None

    chick = generic_creation(egg, PROTO_CHICK_CODE)
    if not chick:
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
    if location.sector not in (SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND, SECTOR.HOUSE):
        return

    # Se l'uovo nel frattempo già non si trova più tra gli oggetti allora esce
    if egg.code not in database["items"]:
        return

    # Rimuove l'uovo dalla stanza e dal database
    egg.extract(1)

    # Inserisce il pulcino nel gioco
    chick.inject(location)

    # Diversifichiamo un po' a a caso la short
    if random.randint(1, 2) == 1:
        chick.short = "un [yellow]pulcino[close]"

    # Avvisiamo tutti quanti del lieto evento
    chick.act("$N si schiude e se ne esce $n!", TO.OTHERS, egg)
    chick.act("Nasci da $N e sei un $n.", TO.ENTITY, egg)
    chick.act("$n nasce da te!", TO.TARGET, egg)

    # Ora che è nato, è certo contento e lo dirà al mondo!
    defer_random_time(15, 30, command_say, chick, "Nemmeno la morte ti può salvare da me!")
    defer_random_time(30, 60, chick_color, chick)
    defer_random_time(60, 80, chick_grow, chick, chicken)
#- Fine Funzione -


def chick_color(chick):
    if not chick:
        log.bug("chick non è un parametro valido: %r" % chick)
        return

    # @GATTO: ma qui forse in realtà ti conviene fare una lista di codici
    # @GATTO: di prototipo.. così da avere separate le definizioni dei dati dal
    # @GATTO: codice e poterle modificare come vuoi, qualcosa tipo:
    #import random   # <- da mettere in alto, il primo tra tutti gli import
    #PROTO_CODES = ["ikea_mob_galletto", "ikea_mob_gallina"]  # <- Da mettere in alto nella zona delle costanti
    #mob = Mob(random.choice(PROTO_CODES))

    chick.short = CHICK_SHORTS[random.randint(1,4)]
#- Fine Funzione


def chick_grow(chick, mother):
    if not chick:
        log.bug("chick non è un parametro valido: %r" % chick)
        return

    if not mother:
        log.bug("mother non è un parametro valido: %r" % mother)
        return

    gallina_adulta = generic_creation(chick, PROTO_CHICKEN_CODE)
    if not gallina_adulta:
        # Può capitare se l'entità ha raggiunto il suo massimo globale creabile
        return

    location = chick.location
    if not location.IS_ROOM:
        return

    # Se il settore della stanza non è corretto esce
    if location.sector not in (SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND, SECTOR.HOUSE):
        return

    # Se il gallinotto nel frattempo non si trova più tra i mob allora esce
    if chick.code not in database["mobs"]:
        return

    # Rimuove il gallinozzo dalla stanza e dal database,
    chick.extract(1)

    # Imposta tutti i riferimenti per la gallina
    gallina_adulta.inject(location)

    # shortizza la gallina..
    gallina_adulta.short = "una [red]gallina[close]"

    # Avvisiamo tutti quanti del lieto evento
    gallina_adulta.act("$N non è più un piccolino ma $n!", TO.OTHERS, chick)
    gallina_adulta.act("Ti origini da $N e sei un $n.", TO.ENTITY, chick)
    gallina_adulta.act("$n nasce da te!", TO.TARGET, chick)

    # Ora che è nato, è certo contento e lo dirà al mondo!
    defer_random_time(15, 30, command_say, gallina_adulta, "Ero piccolo ma adesso non più!")

    # Ora che è cresciuta comincerà a depositare
    defer_random_time(35, 40, start_deposing, gallina_adulta)
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
