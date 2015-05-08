# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

"""
Vegetali marci sotterrati a caso nella fossa biologica ma solo quella
primaverile.
"""


#= IMPORT ======================================================================

import random

from src.item  import Item
from src.enums import FLAG
from src.log   import log


#= COSTANTI ====================================================================

PROTO_VEGGY_CODES = ["miniere-kezaf_item_gemma-perla",
                     "villaggio-zingaro_item_buccia-castagna-marcia",
                     "villaggio-zingaro_item_buccia-castagna-marcia",
                     "villaggio-zingaro_item_buccia-castagna-marcia",
                     "villaggio-zingaro_item_buccia-castagna-marcia",
                     "villaggio-zingaro_item_foglia-fragola-marcia",
                     "villaggio-zingaro_item_foglia-fragola-marcia",
                     "villaggio-zingaro_item_foglia-fragola-marcia",
                     "villaggio-zingaro_item_foglia-fragola-marcia",
                     "villaggio-zingaro_item_foglia-radicchio-marcia",
                     "villaggio-zingaro_item_foglia-radicchio-marcia",
                     "villaggio-zingaro_item_foglia-radicchio-marcia",
                     "villaggio-zingaro_item_foglia-radicchio-marcia",
                     "villaggio-zingaro_item_foglia-verza-marcia",
                     "villaggio-zingaro_item_foglia-verza-marcia",
                     "villaggio-zingaro_item_foglia-verza-marcia",
                     "villaggio-zingaro_item_picciolo-melanzana-marcio",
#"flora_item_moneta-00-seme",
#"flora_item_moneta-00-seme",
                     "villaggio-zingaro_item_picciolo-melanzana-marcio",
                     "villaggio-zingaro_item_picciolo-melanzana-marcio",
                     "villaggio-zingaro_item_picciolo-melanzana-marcio",
                     "villaggio-zingaro_item_porro-marcio",
                     "villaggio-zingaro_item_porro-marcio",
                     "villaggio-zingaro_item_porro-marcio",
                     "villaggio-zingaro_item_zucchina-marcia",
                     "villaggio-zingaro_item_zucchina-marcia",
                     "villaggio-zingaro_item_zucchina-marcia",
                     "villaggio-zingaro_item_zucchina-marcia",
                     "villaggio-zingaro_item_zucchina-marcia",
                     "villaggio-zingaro_item_zucchina-marcia"]


#= FUNZIONI ====================================================================

def on_reset(room):
    gen_trash(room)
#- Fine funzione

# Ora che on_reset funziona anche al boot commento il booting
#def on_booting(room):
#    gen_trash(room)
#    return
##- Fine funzione

#def on_init(room):
#    gen_trash(room)
#    return
#- Fine funzione


def gen_trash(room):
    casual_rotten = Item(random.choice(PROTO_VEGGY_CODES))

    #if casual_rotten.max_global_quantity != 0 and casual_rotten.current_global_quantity >= casual_rotten.max_global_quantity: 
    if casual_rotten.has_reached_max_global_quantity():
        #log.bug("limit exceded")
        return

    casual_rotten.flags += FLAG.BURIED

    #log.bug("veggys injection")
    casual_rotten.inject(room)
