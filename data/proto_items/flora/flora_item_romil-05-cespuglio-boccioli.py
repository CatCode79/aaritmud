# -*- coding: utf-8 -*-

import copy
import random

import_path = "data.proto_items.flora.flora_item_romil-01-seme-vivo"
flora_item_module = __import__(import_path, globals(), locals(), [""])

Genotipo             = flora_item_module.Genotipo
Gameti               = flora_item_module.Gameti

dominance_level      = flora_item_module.dominance_level
dict_len             = flora_item_module.dict_len
cb                   = flora_item_module.cb
init_element         = flora_item_module.init_element
max_prob             = flora_item_module.max_prob
min_prob             = flora_item_module.min_prob
global_cheapest_prob = flora_item_module.global_cheapest_prob
global_highest_prob  = flora_item_module.global_highest_prob

ricalcola_genotipo   = flora_item_module.ricalcola_genotipo

#crea_specials        = flora_item_module.crea_specials
specials_to_entity   = flora_item_module.specials_to_entity


#= COSTANTI ====================================================================

PROTO_ROSA_CODE = "flora_item_romil-10-rosa"


#= FUNZIONI ====================================================================


def on_next_stage(old_entity, new_entity, choised_attr, entities):
    if old_entity.specials and 'ancestors' in old_entity.specials and old_entity.specials['ancestors']:
        print "#### ROMIL - NEXT STAGE - *** copia pedigree ***"
        for key in old_entity.specials:
            new_entity.specials[key] = old_entity.specials[key]
    else:
        print "#### ROMIL - NEXT STAGE - *** nessuna copia ***"
    # qui mi limito a prendere le rose già caricate nel cespuglio,
    # le scorro applicando genotipo ed esprimendolo in modo ascii
    # applico a n-1 rose una mutazione che è solo visiva e non inficia sulle successive generazioni
    # è solo un vezzo.
    # La mutazione vera sarà da implementare altrove, magari dopo fecondazione

    if new_entity.iter_contains():

        # Crea un genotipo vuoto per ricreare quello del cespuglio
        cespuglio_genotipo = Genotipo()
        cespuglio_genotipo.importa_specials(new_entity)

        for flower_entity in new_entity.iter_contains(use_reversed=True):
            # Qui scorre il gruppo fisico come 1 oggetto unico
            if flower_entity.prototype.code == PROTO_ROSA_CODE:
                for enne in xrange(flower_entity.quantity):

                    splitted = flower_entity.split_entity(1)

                    # Creo un genotipo e ci copio quello del cespuglio
                    rosa_genotipo = copy.deepcopy(cespuglio_genotipo)

                    original = True
                    if enne > 0:
                        original = False
                        rosa_genotipo.mutazione()

                    ricalcola_genotipo(rosa_genotipo)
                    
                    # Copio dati nelle specials
                    #crea_specials(rosa_genotipo, splitted)
                    rosa_genotipo.crea_specials(splitted)

                    # Copio le specials nella short/name/decr/value
                    specials_to_entity(splitted)
    return False
