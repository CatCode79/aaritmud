# -*- coding: utf-8 -*-

#= DESCRIZIONE ======================================================================

# serve per rinpinguare le miniere con gemme casuali sepolte

# ad ogni mezzanotte lo script sceglie due room a caso delle miniere
# rimuove eventuali gemme presenti con il flag BURIED
# al loro posto c'è probabilità del 50% che venga generata ed interrata
# una nuova gemma

# c'è temporanemante la possibilità di far scattare lo script facendo "touch" nella
# room ma unicamente per ragioni di test/debug

#= IMPORT ======================================================================

import random

from src.database import database
from src.log       import log
from src.item      import Item
from src.enums     import FLAG

#= COSTANTI ====================================================================

PROTO_GEMS_CODES = ["miniere-kezaf_item_gemma-acquamarina",
        "miniere-kezaf_item_gemma-agata",
        "miniere-kezaf_item_gemma-alessandrite",
# l'ambra non ha senso in miniera
#        "miniere-kezaf_item_gemma-ambra",
        "miniere-kezaf_item_gemma-ametista",
        "miniere-kezaf_item_gemma-ametrino",
        "miniere-kezaf_item_gemma-andalusite",
        "miniere-kezaf_item_gemma-berillo",
        "miniere-kezaf_item_gemma-citrino",
# Non ha senso in miniera
#        "miniere-kezaf_item_gemma-corallo",
        "miniere-kezaf_item_gemma-crisoberillo",
        "miniere-kezaf_item_gemma-cromo-diopside",
        "miniere-kezaf_item_gemma-diamante",
        "miniere-kezaf_item_gemma-diaspro-comune",
        "miniere-kezaf_item_gemma-diaspro-sanguigno",
        "miniere-kezaf_item_gemma-diaspro-verde",
        "miniere-kezaf_item_gemma-giada",
        "miniere-kezaf_item_gemma-granato-demantoide",
        "miniere-kezaf_item_gemma-granato-mandarino",
        "miniere-kezaf_item_gemma-granato-rodolite",
        "miniere-kezaf_item_gemma-granato-tzavorite",
        "miniere-kezaf_item_gemma-iolite",
        "miniere-kezaf_item_gemma-kunzite",
        "miniere-kezaf_item_gemma-lapislazzuli",
        "miniere-kezaf_item_gemma-morganite",
        "miniere-kezaf_item_gemma-onice",
        "miniere-kezaf_item_gemma-opale",
        "miniere-kezaf_item_gemma-opale-di-fuoco",
        "miniere-kezaf_item_gemma-peridoto",
# la perla troverà altre collocazioni
#        "miniere-kezaf_item_gemma-perla",
        "miniere-kezaf_item_gemma-pietra-di-luna-1",
        "miniere-kezaf_item_gemma-pietra-di-luna",
        "miniere-kezaf_item_gemma-quarzo",
        "miniere-kezaf_item_gemma-quarzo-rosa",
        "miniere-kezaf_item_gemma-rubino",
        "miniere-kezaf_item_gemma-smeraldo",
        "miniere-kezaf_item_gemma-spinello",
        "miniere-kezaf_item_gemma-tanzanite",
        "miniere-kezaf_item_gemma-topazio",
        "miniere-kezaf_item_gemma-tormalina-arcobaleno",
        "miniere-kezaf_item_gemma-tormalina-blu",
        "miniere-kezaf_item_gemma-tormalina-gialla",
        "miniere-kezaf_item_gemma-tormalina-multicolore",
        "miniere-kezaf_item_gemma-tormalina-paraiba",
        "miniere-kezaf_item_gemma-tormalina-rubellite",
        "miniere-kezaf_item_gemma-tormalina-verde",
        "miniere-kezaf_item_gemma-turchese",
        "miniere-kezaf_item_gemma-zaffiro",
        "miniere-kezaf_item_gemma-zaffiro-padparadscha",
        "miniere-kezaf_item_gemma-zircone"]

GEMS_WEIGHT_DICT = {"miniere-kezaf_item_gemma-acquamarina":5,
        "miniere-kezaf_item_gemma-agata":5,
        "miniere-kezaf_item_gemma-alessandrite":5,
        "miniere-kezaf_item_gemma-ametista":5,
        "miniere-kezaf_item_gemma-ametrino":5,
        "miniere-kezaf_item_gemma-andalusite":5,
        "miniere-kezaf_item_gemma-berillo":5,
        "miniere-kezaf_item_gemma-citrino":5,
        "miniere-kezaf_item_gemma-crisoberillo":5,
        "miniere-kezaf_item_gemma-cromo-diopside":5,
        "miniere-kezaf_item_gemma-diamante":5,
        "miniere-kezaf_item_gemma-diaspro-comune":5,
        "miniere-kezaf_item_gemma-diaspro-sanguigno":5,
        "miniere-kezaf_item_gemma-diaspro-verde":5,
        "miniere-kezaf_item_gemma-giada":5,
        "miniere-kezaf_item_gemma-granato-demantoide":5,
        "miniere-kezaf_item_gemma-granato-mandarino":5,
        "miniere-kezaf_item_gemma-granato-rodolite":5,
        "miniere-kezaf_item_gemma-granato-tzavorite":5,
        "miniere-kezaf_item_gemma-iolite":5,
        "miniere-kezaf_item_gemma-kunzite":5,
        "miniere-kezaf_item_gemma-lapislazzuli":5,
        "miniere-kezaf_item_gemma-morganite":5,
        "miniere-kezaf_item_gemma-onice":5,
        "miniere-kezaf_item_gemma-opale":5,
        "miniere-kezaf_item_gemma-opale-di-fuoco":5,
        "miniere-kezaf_item_gemma-peridoto":5,
        "miniere-kezaf_item_gemma-pietra-di-luna-1":5,
        "miniere-kezaf_item_gemma-pietra-di-luna":5,
        "miniere-kezaf_item_gemma-quarzo":5,
        "miniere-kezaf_item_gemma-quarzo-rosa":5,
        "miniere-kezaf_item_gemma-rubino":5,
        "miniere-kezaf_item_gemma-smeraldo":5,
        "miniere-kezaf_item_gemma-spinello":5,
        "miniere-kezaf_item_gemma-tanzanite":5,
        "miniere-kezaf_item_gemma-topazio":5,
        "miniere-kezaf_item_gemma-tormalina-arcobaleno":5,
        "miniere-kezaf_item_gemma-tormalina-blu":5,
        "miniere-kezaf_item_gemma-tormalina-gialla":5,
        "miniere-kezaf_item_gemma-tormalina-multicolore":5,
        "miniere-kezaf_item_gemma-tormalina-paraiba":5,
        "miniere-kezaf_item_gemma-tormalina-rubellite":5,
        "miniere-kezaf_item_gemma-tormalina-verde":5,
        "miniere-kezaf_item_gemma-turchese":5,
        "miniere-kezaf_item_gemma-zaffiro":5,
        "miniere-kezaf_item_gemma-zaffiro-padparadscha":5,
        "miniere-kezaf_item_gemma-zircone":5}

#= FUNZIONI ====================================================================

def after_touch(entity, target, descr, detail, behavioured):
    return gem_gen(None)
#- Fine funzione

def on_midnight(room):
    return gem_gen(None)
#- Fine funzione


#def on_booting(room):
    #log.bug("on_booting global miniere")
#    return gem_gen(room)
#- Fine funzione

def gem_gen(unused_room):
    sum_relative_weight = 0
    for gem_code in GEMS_WEIGHT_DICT:
        print "--> relative weight sum <--", sum_relative_weight
        sum_relative_weight += GEMS_WEIGHT_DICT[gem_code]
    print "--> final reative weight sum <--", sum_relative_weight

    area = database["areas"]["miniere-kezaf"]
    rooms = area.rooms.values()
    log.bug("start miniere kezaf", log_stack=False)

    rooms_to_fill = len(rooms) - 2
    print "rooms_to_fill ", rooms_to_fill
    for room in random.sample(rooms, rooms_to_fill):
        for content in room.iter_contains():
            if FLAG.BURIED in content.flags:
                log.bug("gem extraction: %s" % content.code, log_stack=False) 
                content.extract(1)
        if random.randint(0,1):
            casual_gem_code = random.chioce(PROTO_GEMS_CODES)
            if casual_gem_code.has_reached_max_global_quantity():
                log.bug("extract causa excedeed of: %s" % casual_gem_code, log_stack=False) 
            else:
                casual_gem = Item(casual_gem_code)
                casual_gem.flags += FLAG.BURIED
                log.bug("insertion of: %s" % casual_gem.code, log_stack=False) 
                casual_gem.inject(room)

#            if not casual_gem:
#                log.bug("not casual gem: %s" % casual_gem, log_stack=False)
#                return
#            casual_gem.flags += FLAG.BURIED
#        
#            if casual_gem.has_reached_max_global_quantity():
#                log.bug("extract causa excedeed of: %s" % casual_gem.code, log_stack=False) 
#                casual_gem.extract(1)
#            else:
#                log.bug("insertion of: %s" % casual_gem.code, log_stack=False) 
#                casual_gem.inject(room)

#            if casual_gem.max_global_quantity == 0 or casual_gem.current_global_quantity < casual_gem.max_global_quantity: 
#                log.bug("insertion of: %s" % casual_gem.code, log_stack=False) 
#                casual_gem.inject(room)
#            else:
#                log.bug("extract causa excedeed of: %s" % casual_gem.code, log_stack=False) 
#                casual_gem.extract(1)
    return True

#- Fine funzione
def pimpaleone(sum_relative_weight):
    casual_int = random.randint(1,sum_relative_weight)
    gei = 0
    for index in GEMS_WEIGHT_DICT:
        gei += index
        if casual_int <= gei:
            return GEMS_WEIGHT_DICT[index]
        return False
