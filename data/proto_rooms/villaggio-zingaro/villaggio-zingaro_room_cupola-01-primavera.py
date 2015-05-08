# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.defer import defer
from src.enums import DIR, TO
from src.item  import Item


#= COSTANTI ====================================================================

oggetti = {"chiave"         : "villaggio-zingaro_item_chiave-premio-cupola",
           "funghi"         : "villaggio-zingaro_item_cerchio-funghi",
           "contenitore_01" : "villaggio-zingaro_item_contenitore-premio-cupola-01",
           "contenitore_02" : "villaggio-zingaro_item_contenitore-premio-cupola-02",
           "contenitore_03" : "villaggio-zingaro_item_contenitore-premio-cupola-03",
           "premio_01"      : "villaggio-zingaro_item_premio-cupola-01",
           "premio_02"      : "villaggio-zingaro_item_premio-cupola-02",
           "premio_03"      : "villaggio-zingaro_item_premio-cupola-03"}


#= FUNZIONI ====================================================================

def before_move(entity, from_room, direction, to_room, running, behavioured):
    if not entity.IS_PLAYER:
        return

    if direction != DIR.NORTHEAST:
        return

    for content in to_room.iter_contains():
        if content.IS_PLAYER:        
            continue           
        if content.prototype.code == oggetti["contenitore_01"]:
            return

    funghi = Item(oggetti["funghi"])
    contenitore_01 = Item(oggetti["contenitore_01"])
    contenitore_02 = Item(oggetti["contenitore_02"])
    contenitore_03 = Item(oggetti["contenitore_03"])
    premio_01 = Item(oggetti["premio_01"])
    premio_02 = Item(oggetti["premio_02"])
    premio_03 = Item(oggetti["premio_03"])

    funghi.inject(to_room)
    contenitore_01.inject(to_room)
    contenitore_02.inject(to_room)
    contenitore_03.inject(to_room)
    premio_01.inject(contenitore_01)
    premio_02.inject(contenitore_02)
    premio_03.inject(contenitore_03)
    
    to_room.act("\n[mediumturquoise]Una luce provieniente dal centro della cupola ti acceca per pochi attimi... qualcosa è cambiato attorno a te[close].")
    defer(3600, cleaning, to_room)


def cleaning(to_room):
    # Può essere normale visto che la funzione viene deferrata
    if not to_room:
        return

    print ">>> CLEANING <<<"
    for content in to_room.iter_contains(use_reversed=True):
        if content.IS_ACTOR:
            continue
        if content.prototype.code in oggetti.values():
           print ">>> ITEM <<<", content.code
           content.extract(1)
    print ">>> CLINATO <<<"
    to_room.act("\n[mediumturquoise]Un lieve baglio della pietra centrale e tutto sparisce... così com'era venuto[close].")
