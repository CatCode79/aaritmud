# -*- coding: utf-8 -*-

#= COMMENTI ======================================================================
# - La room ha una sola uscita, a sud
# - La destination della room manda nella room stessa (mi serviva un
#   uscita finta insomma)

# Ora devo cercare le coordinate di dove sta ikea_item_carrozzone-01
# devo fare in modo che il valore di DESTINATION dell'uscita coincida
# con quello di ikea_item_carrozzone-01


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import DIR, TO
from src.log      import log


#= COSTANTI ====================================================================

CODICE_CARROZZONE = "carrozzone-zingaro_item_negozio-carrozzone"


#= FUNZIONI ====================================================================

# (TD) Questo sistema è un placebo, in realtà servirà il trigger
# before_command_south tuttavia tramite il trigger after_south più sotto si
# riesce a lenire (ma non a risolvere) il problema del movimento referenziato
# alla stanza stessa e non al carrozzone mobile
def before_south(entity, from_room, direction, to_room, running, behavioured):
    carrozzone = find_carrozzone()

    # Esce se non è stato trovato nessun carrozzone
    if not carrozzone:
        entity.act("Senti l'impellente esigenza di posticipare il commiato.", TO.ENTITY)
        entity.act("$n vorrebbe uscire a $s ma ci ripensa.", TO.OTHERS)
        return True
    
    # Il carrozzone deve trovarsi per forza in una stanza, altrimenti
    # non ricava le coordinate
    if not carrozzone.location.IS_ROOM:
        entity.act("Vedi che il carrozzone è finito in zone troppo poco raccomandabli e decidi di restare.", TO.ENTITY)
        entity.act("$n sbircia all'esterno e si rabbuia.", TO.OTHERS)
        return True

    exit = change_south_exit_destination(from_room, carrozzone)
    # Non ha ritornato l'uscita, qualcosa è andato storto
    if not exit:
        entity.act("Vedi che il carrozzone è finito in zone troppo poco raccomandabli e decidi di restare.", TO.ENTITY)
        entity.act("$n sbircia all'esterno e si rabbuia.", TO.OTHERS)
        return True

    if random.randint(1, 5) == 1:
       entity.act("Mentre esci senti un occhio che ti punta." % direction, TO.ENTITY)
       entity.act("$n s'irrigidisce mentre esce." % direction, TO.OTHERS)

    return False
#- Fine Funzione -


# (TD) ma... praticamente questa funzione non fa nulla!
# (TDS)
# serve per tenere aggiornata la destinazione per via di quel che si vede descritto
# come nome dell'uscita, forse è meglio aggiornarla su ogni move del carrozzone
def after_look(entity, room, descr, detail, use_examine, behavioured):
    if not room.IS_ROOM:
        return False

    carrozzone = find_carrozzone()
    if not carrozzone:
        return False

    exit = change_south_exit_destination(room, carrozzone)
    if not exit:
        return False

    return False
#- Fine Funzione -


def find_carrozzone():
    """
    Ricava il carrozzone in movimento dal database degli oggetti del mud.
    """
    for item in database["items"].itervalues():
        if item.prototype.code == CODICE_CARROZZONE:
            return item.split_entity(1)

    return None
#- Fine Funzione -


def change_south_exit_destination(room, carrozzone):
    """
    Ritorna l'uscita se tutto va a buon fine.
    """
    if not room.IS_ROOM:
        log.bug("Se sei arrivato qui avresti dovuto già controllare che room %s sia effettivamente una stanza, invece è un %r" % (
            room.code, room))
        return None

    if DIR.SOUTH not in room.exits:
        log.bug("Inattesa inesistenza dell'uscita a sud per la stanza %s" % room.code)
        return None

    exit = room.exits[DIR.SOUTH]
    exit.destination.x    = carrozzone.location.x
    exit.destination.y    = carrozzone.location.y
    exit.destination.z    = carrozzone.location.z
    exit.destination.area = carrozzone.location.area

    return exit
#- Fine Funzione -
