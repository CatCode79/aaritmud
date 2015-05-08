# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Inserendo un oggetto di peso opportuno nell'oggetto compare una exit
# nella room nicchia
# (TC) Perché non svuota tutto il contenitore? eh? eh?


#= IMPORT ======================================================================

from src.defer    import defer
from src.database import database
from src.room     import Room, Destination, Exit
from src.enums    import TO, DIR


#= COSTANTI ====================================================================

PROTO_ROOM_CODE = "villaggio-zingaro_room_grotta-nicchia"
EXIT_TO_OPEN = DIR.NORTHEAST
#PESO_MASSIMO = 100000
PESO_MINIMO = 2000
TIME_DELAY = 3000


#= FUNZIONI ====================================================================

def after_putting(player, item, container, direction, behavioured):
    if not player.IS_PLAYER:
        return

    location = find_room(PROTO_ROOM_CODE)
    if not location:
        return 

    if container.get_carried_weight() < PESO_MINIMO:
        player.act("Avverti una soffusa vibrazione generata da $N.", TO.ENTITY, container)
        player.act("Una leggera vibrazione accompagna il gesto di $n.", TO.OTHERS, container)
        player.act("Ti senti in grado di reggere almeno fino ai due chili!", TO.TARGET, container)
        return

    player.act("Una bassa vibrazione ti avvolge, mentre da lontano si sente il rumore di massi che cedono.", TO.ENTITY, container)
    player.act("Una bassa vibrazione avvolge tutto intorno, mentre da lontano si sente il rumore di massi che cedono.", TO.OTHERS, container)
    player.act("Senti d'aver superato la soglia dei due chili!", TO.TARGET, container)

    # Crea la nuova uscita nella room remota
    exit = Exit(EXIT_TO_OPEN)
    location.exits[EXIT_TO_OPEN] = exit
    location.act("La terra comincia a tremare....")

    # Dopo un certo tempo si richiude tutto
    defer(TIME_DELAY, close_exit_again, container, location)


def close_exit_again(container, location):
    """    
    Svuota il container ed elimina l'uscita della room
    """
    # Può capitare visto che questa funzione viene usata in una defer
    if not container or not location:
        return

    del location.exits[EXIT_TO_OPEN]

    location.act("La terra smette di tremare....")

    # IMPERATIVO l'uso di percorrere la lista a rovescio perché il
    # ciclo la modifica facendole sparire gli oggetti di sotto gli occhi
    for content in container.iter_contains(use_reversed=True):
        content = content.from_location(content.quantity)
        content.to_location(container.location)

    container.act("Vomiti tutto il tuo contenuto.", TO.ENTITY)
    container.act("Una forte scossa attraversa $n facendo cadere tutto a terra.", TO.OTHERS)


def find_room(proto_code):
    """
    Ricava la room dal database del mud tramite prototipo.
    """
    for room in database["rooms"].itervalues():
        if room.prototype.code == proto_code:
            return room

    return None
