# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# SCRIPT CESTINATO (prototipo delle plants)

# mirtilli rossi
# semplice progetto d'ecosistema su mirtillo rosso
# il DROP in locazioni opportune del seme di mirtillo rosso
# origina una sequenza di callLater che sostituiscono il mirtillo
# con un germoglio, una pianta, pianta in fiore, pianta in frutto.
# dopo aver fruttificato torna pianta e va in loop pianta, in fiore, in frutto.
# nella versione in frutto vi sono mirtilli buoni e cattivi.
# ad ogni stadio di mutamento della pianta un random vede se la pianta
# deve morire oppure no.

# il numero di frutti prodotti è dato da un valore random + un valore fissato
# MAX_FRUIT_QUANTITY e dall'età della pianta

# la fortuna è un parametro che viene decrementato di stadio in stadio
# imponendo un limite all'età massima della pianta

#= NOTE DI CODIFICA=============================================================


# allo stato attuale le varie funzioni si passano fra loro il codice della room
# anche se solo la funzione germinate() ne fa uso

 

#= IMPORT ======================================================================

import random

from twisted.internet import reactor

from src.database import database
from src.log    import log

from src.enums import SECTOR, TO
from src.item  import Item


#= COSTANTI ===================================================================

# numero di frutti buoni caricati dalla pianta in fiore
MAX_FRUIT_QUANTITY = 5
# intero > 1 ; più è alto e più longeve saranno mediamente le piante
FORTUNA = 100

# durata min e max dello stadio di semente
SEED_WAIT_MIN = 100
SEED_WAIT_MAX = 200
# durata min e max dello stadio di germoglio
GERM_WAIT_MIN = 100
GERM_WAIT_MAX = 200
# durata min e max dello stadio di pianta
PLANT_WAIT_MIN = 100
PLANT_WAIT_MAX = 200
# durata min e max della fioritura
FLOWER_WAIT_MIN = 100
FLOWER_WAIT_MAX = 200
# durata min e max della pianta con i frutti maturi
GROWED_WAIT_MIN = 500
GROWED_WAIT_MAX = 1000

#= TROUBLE  ======================================================================

def after_drop(entity, seed, room, behavioured):

    if not room.IS_ROOM:
        return

    if room.sector not in (SECTOR.PLAIN, SECTOR.WOOD, SECTOR.SAVANNA, SECTOR.HILL):
        return

    fortuna = FORTUNA
    if random.randint(1, fortuna) == 1:
        reactor.callLater(random.randint( SEED_WAIT_MIN, SEED_WAIT_MAX ), marciume, seed, room)
        return
    #coefficiente che segna l'età della pianta
    AGE = 0
    reactor.callLater(random.randint( SEED_WAIT_MIN, SEED_WAIT_MAX ), germinate, seed, room, AGE, fortuna)
#- Fine Funzione

def germinate(seed, room, age, fortuna):

    if seed.code not in database["items"]:
        return

    germoglio = Item("karpuram_item_mirtillo-rosso-02-germoglio")
    if not germoglio:
        log.bug("impossibile creare germoglio: %r" % germoglio)
        return

    #rudimentale contollo per vedere che il seme non sia stato spostato nel frattempo
    # 2 i problemi a cui si va incontro
    # aa) qualcuno lo droppa e poi lo raccatta e lo ridroppa 1ora dopo e comunque lui cresce (da evitare)
    # bb) la room stessa si resetta e anche se il seme non è stato spostato la room è cambiate e lui non cresce (da evitare)
    # forse il controllo con le coordinate xyz potrebbe risolvere b 
    # (gatto dice che non si presenta il problema bb anche se la room resetta)
    # c'è da vedere perché al solito credo ci siam fraintesi ed io pensavo al reset di room diverse nelle stesse coordinate

    # per risolvere aa forse basta in qualche modo che un get interrompa lo script (come fare?)
    if room != seed.location:
        # log da rimuovere 
        log.bug("room di drop diversa da room attuale")
        return

    location=seed.location

    seed.act("Di recente $N s'è schiuso...", TO.OTHERS, seed)
    seed.act("Di recente $N s'è schiuso...", TO.ENTITY, seed)

    seed.extract(1)

    germoglio.inject(location)

    germoglio.act("... in $N.", TO.OTHERS, germoglio)
    germoglio.act("... in $N.", TO.ENTITY, germoglio)
    fortuna = fortuna -1
    if random.randint(1, fortuna) == 1:
        reactor.callLater(random.randint( GERM_WAIT_MIN , GERM_WAIT_MAX ), desiccation, germoglio, room, age)
        return
    reactor.callLater(random.randint( GERM_WAIT_MIN , GERM_WAIT_MAX ), growing, germoglio, room, age, fortuna)

#- Fine Funzione

def growing(germoglio, room, age, fortuna):

    if germoglio.code not in database["items"]:
        return

    pianta = Item("karpuram_item_mirtillo-rosso-03-pianta")
    if not pianta:
        log.bug("impossibile creare pianta: %r" % pianta)
        return

    location=germoglio.location

    germoglio.act("Quel che poco tempo fa era solo $N, ora ...", TO.OTHERS, germoglio)
    germoglio.act("Quel che poco tempo fa era solo $N, ora ...", TO.ENTITY, germoglio)
    germoglio.extract(1)

    pianta.inject(location)

    pianta.act("... è $N.", TO.OTHERS, pianta)
    fortuna = fortuna -1
    if random.randint(1, fortuna) == 1:
        reactor.callLater(random.randint( PLANT_WAIT_MIN , PLANT_WAIT_MAX ), desiccation, pianta, room, age)
        return
    reactor.callLater(random.randint( PLANT_WAIT_MIN , PLANT_WAIT_MAX ), blooming, pianta, room, age, fortuna)

#- Fine Funzione

def blooming(pianta, room, age, fortuna):

    if pianta.code not in database["items"]:
        return

    fiore = Item("karpuram_item_mirtillo-rosso-04-fiore")
    if not fiore:
        log.bug("impossibile creare fiore: %r" % fiore)
        return

    location=pianta.location

    pianta.act("Nelle scorse ore $N ha aperto i fiori", TO.OTHERS, pianta)
    pianta.act("Nelle scorse ore $N ha aperto i fiori", TO.ENTITY, pianta)
    pianta.extract(1)

    fiore.inject(location)

    fiore.act("$N rifulge di tutto il suo splendore.", TO.OTHERS, fiore)
    fiore.act("$N rifulge di tutto il suo splendore.", TO.ENTITY, fiore)
    fortuna = fortuna -1
    if random.randint(1, fortuna) == 1:
        reactor.callLater(random.randint( FLOWER_WAIT_MIN , FLOWER_WAIT_MAX ), desiccation, fiore, room, age )
        return
    reactor.callLater(random.randint( FLOWER_WAIT_MIN , FLOWER_WAIT_MAX ),fructification , fiore, room, age, fortuna)

#- Fine Funzione

def fructification(fiore, room, age, fortuna):

    if fiore.code not in database["items"]:
        return

    fruttificato = Item("karpuram_item_mirtillo-rosso-05-fruttificato")
    if not fruttificato:
        log.bug("impossibile creare fruttificato: %r" % fruttificato)
        return
    #l'istruzione Item è eseguita qui per il chk
    #poi però è ripetuta più volte nel loop
    #qui in qualche modo è codice sporco...
    bacca_buona = Item("karpuram_item_mirtillo-rosso-01-frutto")
    if not fruttificato:
        log.bug("impossibile creare fruttificato: %r" % bacca_buona)
        return
    bacca_cattiva = Item("karpuram_item_mirtillo-rosso-00-frutto-sterile")
    if not fruttificato:
        log.bug("impossibile creare fruttificato: %r" % bacca_cattiva)
        return

    location=fiore.location

    fiore.act("Dei fiori d'un tempo $N non ne ha più...", TO.OTHERS, fiore)
    fiore.act("Dei fiori d'un tempo $N non ne ha più...", TO.ENTITY, fiore)
    fiore.extract(1)

    fruttificato.inject(location)
    
    for q in xrange(MAX_FRUIT_QUANTITY + 2 * age + random.randint(1,4) - 2 ):
        bacca_buona = Item("karpuram_item_mirtillo-rosso-01-frutto")
        bacca_buona.inject(fruttificato) 

    for q in xrange(MAX_FRUIT_QUANTITY + 2 * age + random.randint(1,4) - 2 ):
        bacca_cattiva = Item("karpuram_item_mirtillo-rosso-00-frutto-sterile")
        bacca_cattiva.inject(fruttificato) 

    fruttificato.act("in compenso ora è $N.", TO.OTHERS, fruttificato)
    fortuna = fortuna -1
    if random.randint(1, fortuna) == 1:
        reactor.callLater(random.randint(GROWED_WAIT_MIN,GROWED_WAIT_MAX), desiccation, fruttificato, room, age )
        return
     
    reactor.callLater(random.randint(GROWED_WAIT_MIN,GROWED_WAIT_MAX), renew, fruttificato, room, age, fortuna )

#- Fine Funzione

def renew(fruttificato, room, age, fortuna):

    if fruttificato.code not in database["items"]:
        return

    pianta = Item("karpuram_item_mirtillo-rosso-03-pianta")
    if not pianta:
        log.bug("impossibile creare pianta: %r" % pianta)
        return

    age = age +1
    location=fruttificato.location

    fruttificato.act("quel che un tempo doveva esser $N, ora ...", TO.OTHERS, fruttificato)
    fruttificato.act("quel che un tempo doveva esser $N, ora ...", TO.ENTITY, fruttificato)
    fruttificato.extract(1)

    pianta.inject(location)

    pianta.act("... è $N che fruttificherà più avanti", TO.OTHERS, pianta)
    pianta.act("... è $N che fruttificherà più avanti", TO.ENTITY, pianta)
    
    fortuna = fortuna -1
    if random.randint(1, fortuna) == 1:
        reactor.callLater(random.randint(10,20), desiccation, pianta, room, age )
        return
    reactor.callLater(random.randint(10,20), blooming, pianta, room, age, fortuna)

#- Fine Funzione

# il seme è marcito
def marciume(seed, room):

    if seed.code not in database["items"]:
        return
    frutto_marcio = Item("karpuram_item_mirtillo-rosso-00-frutto-marcio")
    if not frutto_marcio:
        log.bug("impossibile creare frutto_marcio: %r" % frutto_marcio)
        return

    if room != seed.location:
        # log da rimuovere 
        log.bug("room di drop diversa da room attuale")
        return

    location=seed.location

    seed.act("$N appare tutto molliccio...", TO.OTHERS, seed)
    seed.act("$N appare tutto molliccio...", TO.ENTITY, seed)

    seed.extract()

    frutto_marcio.inject(location)

    frutto_marcio.act("... è $N buono solo come concime.", TO.OTHERS, frutto_marcio)
    frutto_marcio.act("... è $N buono solo come concime.", TO.ENTITY, frutto_marcio)
    # c'è da valutare se i semi marci son da far sparire dopo un po'
    # evitandone l'accumulo sconsiderato

#- Fine Funzione
# lo stadio attuale della pianta va in marcescenza
def desiccation(generic_plant, room, age):

    if generic_plant.code not in database["items"]:
        return

    pianta_morta = Item("karpuram_item_mirtillo-rosso-06-pianta_morta")
    if not pianta_morta:
        # qui non dovrà uscire dallo script che sennò si frizza la pianta a questo stadio
        log.bug("impossibile creare pianta_morta: %r" % pianta_morta)
        return

    location=generic_plant.location

    generic_plant.act("Il rigoglio di $N ...", TO.OTHERS, generic_plant)
    generic_plant.act("Il rigoglio di $N ...", TO.ENTITY, generic_plant)
    generic_plant.extract()

    pianta_morta.inject(location)
    pianta_morta.descr_sixth = "una pianta che ha passato %r stagioni" % age
    pianta_morta.act("... è tramontato in $N.", TO.OTHERS, pianta_morta)
    pianta_morta.act("... è tramontato in $N.", TO.ENTITY, pianta_morta)
    #anche qui è da vedere come rimuovere i cadaveri delle piante morte
    #ha la stessa urgenza di rimozione dei mirtilli marci

#- Fine Funzione



#
#    # Ora che è nato, è certo contento e lo dirà al mondo!
#    reactor.callLater(random.randint(15, 30), command_say, gallina_adulta, "Ero piccolo ma adesso non più!")
#
#    reactor.callLater(random.randint(20, 35), start_deposing, gallina_adulta)
##- Fine Funzione -
#
#def death(entity):
#
#    location = entity.location
#    if not location:
#        log.bug("gatto, l'on_init è lento sul grow")
#        return
#    if not location.IS_ROOM:
#        return
#
#    # Se il settore della stanza non è corretto esce
#    if location.sector not in (SECTOR.INSIDE, SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND):
#        return
#
#    # Se il gallinotto nel frattempo non si trova più tra i mob allora esce
#    if entity.code not in  database["mobs"]:
#        return
#
#    # Rimuove il gallinozzo dalla stanza e dal database,
#    # Avvisiamo tutti quanti del lieto evento
#    entity.act("$N non è più fra noi...", TO.OTHERS, entity)
#    entity.act("È ora di morire!", TO.TARGET, entity)
#    
#    entity.from_location()
#    del(database["mobs"][entity.code])
##- Fine Funzione -
#
## funzione di rimozione entità di tipo item
#def death_items(entity):
#
#    location = entity.location
#    if not location:
#        log.bug("not location")
#        return
#    if not location.IS_ROOM:
#       # (TD) 
#       # qui probabile che debba andare a morire anche se non è in room
#        # quindi vada tolto il controllo
#        log.bug("location is not room")
#        return
#
#    # la morte non si ferma davanti a simili quisquilie
#    ## Se il settore della stanza non è corretto esce
#    #if location.sector not in (SECTOR.INSIDE, SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND):
#        return
#
#    # Se nel frattempo non si trova più tra gli items  allora esce
#    if entity.code not in  database["items"]:
#        return
#
#    # Rimuove finalmente dalla stanza e dal database,
#    # Avvisiamo tutti quanti del triste epilogo
#    entity.act("$N non è più fra noi...", TO.OTHERS, entity)
#    entity.act("Appassisco", TO.TARGET, entity)
#    
#    entity.from_location()
#    del(database["items"][entity.code])
##- Fine Funzione -
#
## perfezionato e rimuove sia mob che intem
#def death(entity):
#
#    location = entity.location
#    if not location:
#        log.bug("gatto, l'on_init è lento sul grow")
#        return
#    # tolto che la morte non bada a simili quisquilie
#    #if not location.IS_ROOM:
#    #    return
#
#    # tolto che la morte non bada a simili quisquilie
#    ## Se il settore della stanza non è corretto esce
#    #if location.sector not in (SECTOR.INSIDE, SECTOR.PLAIN, SECTOR.WOOD, SECTOR.FARMLAND):
#        return
#
#    # Se l'entità nel frattempo non si trova più tra i mob o tra gli items allora esce
#    if entity.code not in  database[entity.ACCESS_ATTR]:
#        return
#
#    # Rimuove l'entità dalla locazione e dal database,
#    # ma prima avvisiamo tutti quanti del lieto evento
#    entity.act("$N non è più fra noi...", TO.OTHERS, entity)
#    entity.act("È ora di morire!", TO.TARGET, entity)
#    
#    entity.from_location()
#    del(database[entity.ACCESS_ATTR][entity.code])
##- Fine Funzione -
