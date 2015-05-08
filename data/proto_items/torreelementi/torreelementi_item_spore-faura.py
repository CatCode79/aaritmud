# -*- coding: utf-8 -*-


#= DESCRIZIONE =================================================================

# Quando si droppano le spore, se finiscono in un terreno fertile,
# allora danno corpo ad un nuovo mob fungoso


#= IMPORT ======================================================================

import random

from src.database import database
from src.defer    import defer, defer_random_time
from src.enums    import SECTOR, TO
from src.log      import log
from src.mob      import Mob

from src.commands.command_emote import command_emote


#= FUNZIONI ====================================================================

def after_drop(entity, spore, room, behavioured):
    # Se l'oggetto non è stato abbandonato in una stanza esce
    if not room.IS_ROOM:
        entity.act("$N si diradano e spariscono in volo...", TO.ENTITY, spore)
        if spore.code not in database["items"]:
            return
        spore.extract(1)
        return

    # Se il settore della stanza non è tra quelli fertili esce
    if not room.sector.fertile:
        entity.act("$N si diradano e spariscono in volo ancor prima di toccar terra!", TO.ENTITY, spore)
        if spore.code not in  database["items"]:
            return
        spore.extract(1)
        return

    # Tra 10 secondi Aarit avrà terminato di assorbire le spore nel terreno
    # facendone nascere un mob fungoso!
    entity.act("$N acquistano consistenza ovattosa e si depositano in terra formando una muffina bianca.", TO.ENTITY, spore)
    defer(10, born_mushrum, spore, room)
#- Fine Funzione -


def born_mushrum(spore, room):
    # Se le spore non si trovan più tra gli oggetti allora il gamescript è
    # già scattato in precedenza
    if spore.code not in database["items"]:
        return

    # Rimuove le spore dalla stanza e dal database, abbiamo nella funzione
    # spore che possiamo utilizzare fino alla fine della stessa, poi
    # l'oggetto sarà come se non esistesse più
    spore = spore.extract(1)

    # Crea una nuova entità dal nostro conosciutissimo mushroom passandogli il
    # codice identificativo del prototipo
    mushroom = Mob("torreelementi_mob_faura_01")

    # Imposta tutti i riferimenti per il neonato mushroom, sarà da controllare che
    # siano tutti a posto!
    mushroom.inject(room)

    # Avvisiamo tutti quanti del lieto evento
    mushroom.act("Qualcuno ha fatto l'errore di seminarti tramite $N ma lo raggiungerai", TO.ENTITY, spore)
    mushroom.act("L'orrore non avrà dunque mai fine! Ecco enuclearsi $n!", TO.OTHERS, spore)
    mushroom.act("$n 'enuclea ed ora tu te ne devi andare", TO.TARGET, spore)

    # Rendiamo conto della velocità di germinazione con genuina sorpresa
    defer_random_time(15, 30, command_emote, mushroom, "è cresciuto a vista d'occhio!")
#- Fine Funzione -
