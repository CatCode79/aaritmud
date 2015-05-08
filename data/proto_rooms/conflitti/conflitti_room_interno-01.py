# -*- coding: utf-8 -*-

## questo gamescript va inserito nella stanza da guardare

#= IMPORT ======================================================================

from src.enums import TO
from src.room  import Destination


#= FUNZIONI ====================================================================

def after_look(entity, target, descr, detail, use_examine, behavioured):
    # Funziona solo se quello che si guarda è un'extra
    if not detail:
        return False
    if not detail.IS_EXTRA:
        return False

    # Se l'extra non è quella della parete allora esce
    if "parete" not in detail.keywords:
        return False

    # Ricava la destinazione per il teletrasporto
    destination_room = Destination(1, 0, -1, "conflitti").get_room()
    if not destination_room:
        # Nessuna destinazione o stanza trovata: forse non è stata ancora resettata?
        return False

    # Invia un messaggio di teleport alle due stanze
    entity.act("Una presenza offusca e dirada la tua attenzione.", TO.ENTITY)
    entity.act("$n se ne va da qui!", TO.OTHERS)
    entity = entity.from_location(1)
    entity.to_location(destination_room)
    entity.act("Qualcuno o qualcosa ti osserva...", TO.ENTITY)
    entity.act("$n arriva qua!", TO.OTHERS)
    return False
#- Fine Funzione -
