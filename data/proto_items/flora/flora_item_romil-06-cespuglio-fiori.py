# -*- coding: utf-8 -*-


#= COMMENT =====================================================================

# Qui c'è l'aspetto più intrigante: la fecondazione
# ogni seme è generato con parte del genotipo dei genitori
# e l'altra parte presa dai cespugli vicini (stessa room)
# La fecondazione esterna (fra cespugli diversi) ha luogo solo se qualcuno
# o qualcosa tocca un cespuglio in fiore.


#= IMPORT ======================================================================

import random

from src.commands.command_emote import command_emote
#from src.socials.social_sneeze  import social_sneeze
from src.interpret              import interpret

import_path = "data.proto_items.flora.flora_item_romil-01-seme-vivo"
flora_item_module = __import__(import_path, globals(), locals(), [""])

Genotipo             = flora_item_module.Genotipo
Gameti               = flora_item_module.Gameti

# IMPORTO TUTTO CHE NON HO BALLE DI GUARDARE COSA MI SERVE E COSA NO
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

PROTO_SEME_CODE = "flora_item_romil-01-seme-vivo"
PROTO_ROSA_CODE = "flora_item_romil-10-rosa"


#= FUNZIONI ====================================================================

def before_touched(entity, cespuglio, detail, descr, behavioured):
    # Il valore di cespuglio.quantity è ad uno anche se è parte di un gruppo fisico.

    if not cespuglio.specials or 'ancestors' not in cespuglio.specials:
        print "#### ROMIL - TOUCH - specials NON presenti"
        # (TD) da gestire, ricreare i genotipi
        # Se un trust alto icrea il cespuglio accanto agli altri,
        # crasha tutto in fase di fecondazione
        return

    # (TD) dopo 2 o 3 volte che si tocca dovrebbe perdere la sua efficacia
    command_emote(cespuglio, "comincia ad oscillare spargendo un po' di polline.")
    interpret(entity, "sneeze", show_input=False, show_prompt=False)
    if not cespuglio.location.IS_ROOM:
        # (TD) In vaso sarà un dramma da gestire
        return

    room = cespuglio.location
    cespugli = []
    
    for item in room.iter_contains(use_reversed=True):
        if item.IS_ITEM and item.prototype.code == cespuglio.prototype.code:
            for x in xrange(item.quantity):
                if 'genotipo' in splitted_cespuglio.__dict__ and splitted_cespuglio.genotipo.gameti_propri != []:
                    # evito inutili ripetizioni nel caso qualcuno tocchi più volte
                    continue
                # Splitto i cespugli e in ciascuno metto un metodo Genotipo in cui
                # carico il genoma e ricavo i due gameti
                splitted_cespuglio = item.split_entity(1)
                splitted_cespuglio.genotipo = Genotipo()
                splitted_cespuglio.genotipo.importa_specials(splitted_cespuglio)
                # ora metto una lista con i due gameti per ciascun cespuglio 
                splitted_cespuglio.genotipo.gameti_propri = splitted_cespuglio.genotipo.get_gameti()
                cespugli.append(splitted_cespuglio)

    print "numero cespugli che han generato i loro gameti: ", len(cespugli)   
    # per ogni cespuglio metto nell'apposita lista del Genotipo la lista di tutti gli alleli degli altri cespugli
    for item in cespugli:
        for en in cespugli:
            if item != en:
                if not item.specials and 'already_touched' not in item.specials:
                    item.genotipo.gameti_altrui += en.genotipo.gameti_propri

    print 'cespugli: ',  cespugli
    print 'cespugli[0]', cespugli[0]
    print 'cespugli[0].genotipo', cespugli[0].genotipo
    print 'cespugli[0].genotipo.gameti_propri', cespugli[0].genotipo.gameti_propri
    cespuglio.specials['already_touched'] = True
    return True
            

def on_next_stage(old_entity, new_entity, choised_attr, entities):
    # (TD) Qui se cade il mud fra un touch e un next stage si perde tutta la fecondazione

    print "Next_Stage cespuglio in fiore"
    if old_entity.specials and 'ancestors' in old_entity.specials and old_entity.specials['ancestors']:
        print "#### ROMIL - NEXT STAGE - *** copia pedigree ***"
        for key in old_entity.specials:
            new_entity.specials[key] = old_entity.specials[key]
        old_entity.specials['already_touched'] = False
    else:
        print "#### ROMIL - NEXT STAGE - *** nessuna copia ***"
        # (TD) qui bisogna generare il genotipo con la stessa procedura che nel seed_del_seme 

    for item in new_entity.iter_contains(use_reversed=True):
        if item.IS_ITEM and item.prototype.code == PROTO_SEME_CODE:
            for x in xrange(item.quantity):
                # Splitto i semii e in ciascuno metto un metodo Genotipo in cui
                # carico il genoma e ricavo i due gameti
                splitted_seme = item.split_entity(1)
                # (TD) Se il gameti propri è vuoto, significa che nessuno ha fatto il touch delle piante
                # fiorite e che non c'è neppure Genotipo() attaccato
                if 'genotipo' not in old_entity.__dict__ or old_entity.genotipo.gameti_propri == []:
                    #old_entity.genotipo = Genotipo()
                    #old_entity.genotipo.importa_specials(old_entity)
                    #old_entity.genotipo.gameti_propri = old_entity.genotipo.get_gameti()
                    ##nel caso in cui ci sia autofecondazione tengo gli stessi gameti nello stesso ordine
                    #random_g_proprio = old_entity.genotipo.gameti_propri[0]
                    for key in old_entity.specials:
                        splitted_seme.specials[key] = old_entity.specials[key]
                
                else:
                    random_g_proprio = random.choice(old_entity.genotipo.gameti_propri)

                    # Se il gameti altrui è vuoto pesca dai propri il secondo (autofecondazione)
                    if old_entity.genotipo.gameti_altrui == []:
                        #random_g_altrui = old_entity.genotipo.gameti_propri[1]
                        random_g_altrui = random.choice(old_entity.genotipo.gameti_propri)
                    else:
                        random_g_altrui  = random.choice(old_entity.genotipo.gameti_altrui)
                    splitted_seme.genotipo = Genotipo()
                    splitted_seme.genotipo.fecondazione(random_g_proprio, random_g_altrui)
                    ricalcola_genotipo(splitted_seme.genotipo)
                    #crea_specials(splitted_seme.genotipo, splitted_seme)
                    splitted_seme.genotipo.crea_specials(splitted_seme)
    return False
