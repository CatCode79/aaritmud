# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Il frutto è un SECRET.CONTAINER una volta aperto non si deve poter richiudere
# e si deve rovinare (life diminuita)
# (TD) dovrebbe caricare dei semi al suo interno


#= IMPORT ======================================================================

import random

from src.database import database
from src.defer    import defer
from src.enums    import CONTAINER, FLAG
from src.item     import Item
from src.log      import log

from src.commands.command_follow import command_follow


#= COSTANTI ====================================================================

PROTO_SEED_CODE = {"fertile" : "flora_item_peperoncino-01-seme",
                   "sterile" : "flora_item_peperoncino-02-seme-sterile"}

OPENING_DAMAGE = 5
TIME_DELAY = 1


#= FUNZIONI ====================================================================

def after_open(player, peperoncino, reverse_target, container_only, behavioured):
    peperoncino.container_type.flags -= CONTAINER.CLOSABLE 
    residual_life = max(0, peperoncino.life - OPENING_DAMAGE)
#- Fine Funzione -


def after_inject(peperoncino, location):
    print "peperone on inject"
    defer(TIME_DELAY, seed_refill, peperoncino, location, 'fertile')
    defer(TIME_DELAY, seed_refill, peperoncino, location, 'sterile')
#- Fine Funzione -


def seed_refill(peperoncino, location, seme_id):
    if not peperoncino:
        return

    # (TC) pare che sull'on_inject non vi sia ancora il contained by ma si
    # debba attendere qualche secondo

    # Si assicura che il codice passato esista
    if PROTO_SEED_CODE[seme_id] not in database["proto_items"]:
        log.bug("Il codice %s non è stato trovato nel database" % proto_code, log_stack=False)
        return

    proto_seed = database["proto_items"][PROTO_SEED_CODE[seme_id]]
    if proto.has_reached_max_global_quantity():
    #if proto_seed.max_global_quantity != 0 and proto_seed.current_global_quantity >= proto_seed.max_global_quantity:
        log.bug("Troppi semi %s in gioco nel database" % proto_seed.code, log_stack=False)
        #seed_max = True
        return
    else:
        quantity_seed = random.randint(2, 5)
        print "seed insertion:", seme_id, ":", quantity_seed
        while quantity_seed > 0:
            content = proto_seed.CONSTRUCTOR(proto_seed.code)
            content.inject(peperoncino)
            quantity_seed -= 1
#- Fine Funzione -
