# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

import random

from src.defer    import defer, defer_random_time
from src.database import database
from src.enums    import SECTOR, TO
from src.log      import log
from src.mob      import Mob

from src.commands.command_say import command_say


#= FUNZIONI ====================================================================

def before_drop(entity, brain, room, behavioured):
    # Se il giocatore cerca di abbandonare il cervello ne riceve un simpatico
    # tentacoloso messaggio (chi ha giocato a day of tentacle?)
    entity.act("$N pulsa come se... come se... come se volesse conquistare il mondo!", TO.ENTITY, brain)
#- Fine Funzione -


def after_dropped(entity, brain, room, behavioured):
    # Se l'oggetto non è stato abbandonato in una stanza esce
    if not room.IS_ROOM:
        return

    # Se il settore della stanza non è tra quelli fertili esce
    if room.sector not in (SECTOR.PLAIN, SECTOR.WOOD):
        entity.act("$N pulsa come se... come se... come se volesse conquistare il mondo, ma oggi il mondo non è disponibile!", TO.ENTITY, brain)
        return

    entity.act("$N pulsa come se... come se... come se volesse conquistare il mondo!", TO.ENTITY, brain)

    # Tra 10 secondi il reattore di aarit avrà terminato di assorbire il
    # cervello nel terreno facendone nascere un mindflayer
    defer(10, born_to_be_wild_or_something, brain, room)
#- Fine Funzione -


def  born_to_be_wild_or_something(brain, room):
    # Se il  cervello non si trova più tra gli oggetti allora il gamescript è
    # già scattato in precedenza
    if brain.code not in  database["items"]:
        return

    # Rimuove il cervello dalla stanza e dal database,  abbiamo nella funzione
    # brain che possiamo utilizzare fino  alla fine della stessa, poi
    # l'oggetto sarà come se non  esistesse più
    brain.extract(1)

    # Crea una nuova entità dal nostro conosciutissimo mindf passandogli il
    # codice identificativo del prototipo
    mindf = Mob("mfdonald_mob_mindflayer_01")

    # Imposta tutti i riferimenti per il neonato mindf, sarà da controllare che
    # siano tutti a posto!
    mindf.inject(room)

    # Avvisiamo tutti quanti del lieto evento
    mindf.act("$n nasce da $N e inizia subito a muovere i tentacolini, che carino!", TO.OTHERS, brain)
    mindf.act("Nasci da $N e inizi subito ad avere un certo languorino; ma la tua non è proprio fame... e solo voglia di qualcosa di buono!", TO.ENTITY, brain)
    mindf.act("$n nasce da te, e ti senti subito molto orGoglione di quello che hai fatto!", TO.TARGET, brain)

    # Ora che è nato facciamogli dire qualcosa di intelligente in un tempo
    # variabili di secondi (qui in realtà sarebbe meglio utilizzare la funzione
    # interpret per inviare i comandi, cosicché mob che, per esempio, dormono
    # si mettono nella posizione alzata per inviare il comando, ma vabbe')
    defer_random_time(15, 30, command_say, mindf, "Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl, fhtagn!")
    # Urgh, ma questo è un attacco! 10 milioni di neuroni bruciati con una
    # sola chiamata a funzione! Gattarola!
#- Fine Funzione -
