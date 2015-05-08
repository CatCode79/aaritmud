# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Serve per rinpinguare le miniere con gemme casuali sepolte

# Ad ogni mezzanotte lo script sceglie delle room a caso nelle miniere e
# rimuove eventuali gemme presenti con il flag BURIED.
# Al loro posto c'è probabilità del 50% che venga generata ed interrata
# una nuova gemma sulla base dell'indice di rarità della gemma stessa
# (tale indice è nel dizionario).

# NB: C'è temporanemante la possibilità di far scattare lo script facendo
# "touch" nella room ma unicamente per ragioni di test/debug


#= IMPORT ======================================================================

import random

from src.database import database
from src.log      import log
from src.item     import Item
from src.enums    import FLAG


#= COSTANTI ====================================================================

GEM_WEIGHTS = {"miniere-kezaf_item_gemma-grezza-acquamarina":5,
               "miniere-kezaf_item_gemma-grezza-agata":5,
               "miniere-kezaf_item_gemma-grezza-ametista":5,
               "miniere-kezaf_item_gemma-grezza-ametrino":5,
               "miniere-kezaf_item_gemma-grezza-azzurrite":5,
               "miniere-kezaf_item_gemma-grezza-berillo":5,
               "miniere-kezaf_item_gemma-grezza-corniola":5,
               "miniere-kezaf_item_gemma-grezza-crisoberillo":5,
               "miniere-kezaf_item_gemma-grezza-crisocolla":5,
               "miniere-kezaf_item_gemma-grezza-crisoprasio":5,
               "miniere-kezaf_item_gemma-grezza-cromo-diopside":5,
               "miniere-kezaf_item_gemma-grezza-diamante":5,
               "miniere-kezaf_item_gemma-grezza-diaspro-comune":5,
               "miniere-kezaf_item_gemma-grezza-diaspro-sanguigno":5,
               "miniere-kezaf_item_gemma-grezza-diaspro-verde":5,
               "miniere-kezaf_item_gemma-grezza-eliodoro":5,
               "miniere-kezaf_item_gemma-grezza-ematite":5,
               "miniere-kezaf_item_gemma-grezza-giada":5,
               "miniere-kezaf_item_gemma-grezza-granato-demantoide":5,
               "miniere-kezaf_item_gemma-grezza-granato-mandarino":5,
               "miniere-kezaf_item_gemma-grezza-granato-rodolite":5,
               "miniere-kezaf_item_gemma-grezza-granato-tuperite":5,
               "miniere-kezaf_item_gemma-grezza-iolite":5,
               "miniere-kezaf_item_gemma-grezza-kezafite":5,
               "miniere-kezaf_item_gemma-grezza-klirbite":5,
               "miniere-kezaf_item_gemma-grezza-lapislazzuli":5,
               "miniere-kezaf_item_gemma-grezza-malachite":5,
               "miniere-kezaf_item_gemma-grezza-mirnite":5,
               "miniere-kezaf_item_gemma-grezza-occhio-di-tigre":5,
               "miniere-kezaf_item_gemma-grezza-onice":5,
               "miniere-kezaf_item_gemma-grezza-opale":5,
               "miniere-kezaf_item_gemma-grezza-opale-di-fuoco":5,
               "miniere-kezaf_item_gemma-grezza-ossidiana":5,
               "miniere-kezaf_item_gemma-grezza-ossidiana-nivea":5,
               "miniere-kezaf_item_gemma-grezza-peridoto":5,
               "miniere-kezaf_item_gemma-grezza-pietra-di-tenox":5,
               "miniere-kezaf_item_gemma-grezza-pirite":5,
               "miniere-kezaf_item_gemma-grezza-quarzo-citrino":5,
               "miniere-kezaf_item_gemma-grezza-quarzo-comune":5,
               "miniere-kezaf_item_gemma-grezza-quarzo-ialino":5,
               "miniere-kezaf_item_gemma-grezza-quarzo-rosa":5,
               "miniere-kezaf_item_gemma-grezza-rubino":5,
               "miniere-kezaf_item_gemma-grezza-smeraldo":5,
               "miniere-kezaf_item_gemma-grezza-spinello":5,
               "miniere-kezaf_item_gemma-grezza-sugilite":5,
               "miniere-kezaf_item_gemma-grezza-tainite":5,
               "miniere-kezaf_item_gemma-grezza-topazio":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-arcobaleno":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-blu":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-di-kalte":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-gialla":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-multicolore":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-rubellite":5,
               "miniere-kezaf_item_gemma-grezza-tormalina-verde":5,
               "miniere-kezaf_item_gemma-grezza-turchese":5,
               "miniere-kezaf_item_gemma-grezza-uzijite":5,
               "miniere-kezaf_item_gemma-grezza-zaffiro":5,
               "miniere-kezaf_item_gemma-grezza-zaffiro-di-kalte":5,
               "miniere-kezaf_item_gemma-grezza-zircone":5}

# Le gemme vengono caricate con un maxlife compreso fra:
MIN_GEM_LIFE = 6
MAX_GEM_LIFE = 12
MIN_GEM_VIGOUR = 6
MAX_GEM_VIGOUR = 12


#= FUNZIONI ====================================================================

def after_touch(entity, target, descr, detail, behavioured):
    return gem_generation(None)
#- Fine funzione


def on_midnight(room):
    return gem_generation(None)
#- Fine funzione


def gem_generation(unused_room):
    sum_relative_weight = 0
    for gem_code in GEM_WEIGHTS:
        #print "--> relative weight sum <--", sum_relative_weight
        sum_relative_weight += GEM_WEIGHTS[gem_code]
    #print "--> final reative weight sum <--", sum_relative_weight

    area = database["areas"]["miniere-kezaf"]
    rooms = area.rooms.values()
    #log.bug("start miniere kezaf", log_stack=False)
    rooms_to_fill = len(rooms) - 2
    #print "rooms_to_fill ", rooms_to_fill

    for room in random.sample(rooms, rooms_to_fill):
        for content in room.iter_contains(use_reversed=True): #maledetto, maledetto reversed!
            if FLAG.BURIED in content.flags:
                #log.bug("gem extraction: %s" % content.code, log_stack=False)
                content.extract(1)

        if random.randint(0, 1) == 0:
            #print gem_code_generator(sum_relative_weight)
            chosed_gem_code = gem_code_generator(sum_relative_weight)
            casual_gem = database["proto_items"][chosed_gem_code]
            if not casual_gem:
                log.bug("not casual gem: %s" % casual_gem, log_stack=False)
                return
        
            if casual_gem.has_reached_max_global_quantity():
                log.bug("not inject causa maxquantity of: %s" % casual_gem.code, log_stack=False)
            else:
                casual_gem = Item(chosed_gem_code)
                casual_gem.flags += FLAG.BURIED

                casual_gem.max_vigour = random.randint(MIN_GEM_VIGOUR, MAX_GEM_VIGOUR)
                casual_gem.vigour = random.randint(1,casual_gem.max_vigour)
                casual_gem.max_life = random.randint(MIN_GEM_LIFE, MAX_GEM_LIFE)
                casual_gem.life = random.randint(1,casual_gem.max_life)

                casual_gem.inject(room)

#            #if casual_gem.max_global_quantity == 0 or casual_gem.current_global_quantity < casual_gem.max_global_quantity:
#                casual_gem = Item(chosed_gem_code)
#                casual_gem.flags += FLAG.BURIED
#
#                casual_gem.max_vigour = random.randint(MIN_GEM_VIGOUR, MAX_GEM_VIGOUR)
#                casual_gem.vigour = random.randint(1,casual_gem.max_vigour)
#                casual_gem.max_life = random.randint(MIN_GEM_LIFE, MAX_GEM_LIFE)
#                casual_gem.life = random.randint(1,casual_gem.max_life)
#
#                casual_gem.inject(room)
#                #log.bug("insertion of: %s" % casual_gem.code, log_stack=False) 
#            else:
#                log.bug("not inject causa maxquantity of: %s" % casual_gem.code, log_stack=False)

    return True
#- Fine Funzione -


def gem_code_generator(sum_relative_weight):
    casual_int = random.randint(1, sum_relative_weight)
    #print "gem_code_generator casual int: ", casual_int

    gei = 0
    for gem_code in GEM_WEIGHTS:
        gei += GEM_WEIGHTS[gem_code]
        #print "gei from gem_code_generator: " ,gei
        if casual_int <= gei:
            #print "gem code returned from gem_code_generator: ", gem_code
            return gem_code

    print "return None from gem_code_generator"
    return None
#- Fine Funzione -
