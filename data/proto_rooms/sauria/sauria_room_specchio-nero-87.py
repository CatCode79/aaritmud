# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.enums import TO
from src.room  import Destination


#= FUNZIONI ====================================================================

def after_look(entity, target, descr, detail, use_examine, behavioured):
    # Se quello che si guarda è una extra
    if not detail:
        return False
    if not detail.IS_EXTRA:
        return False

    teleport(entity, target, descr, detail)
#- Fine Funzione -


def after_touch(entity, target, descr, detail, behavioured):
    # Se quello che si guarda è una extra
    if not detail:
        return False
    if not detail.IS_EXTRA:
        return False

    teleport(entity, target, descr, detail)
#- Fine Funzione -


def teleport(entity, target, descr, detail):
    # Ricava la destinazione per il teletrasporto
    destination_room = Destination(0, 0, 10, "sauria").get_room()
    if not destination_room:
        # Nessuna destinazione o stanza trovata: forse non è stata ancora resettata?
        return False

    # Invia un messaggio di teleport alle due stanze
    entity.act("[yellow]Varchi il nero specchio che ti si para dinnanzi[close].", TO.ENTITY)
    entity.act("[yellow]$n attraversa lo specchio nero[close]!", TO.OTHERS)
    entity = entity.from_location(1)
    entity.to_location(destination_room)
    entity.act("[yellow]Sei ora in una nuova realtà[close].", TO.ENTITY)
    entity.act("[yellow]$n giunge da lidi lontani[close]!", TO.OTHERS)
#- Fine Funzione -
