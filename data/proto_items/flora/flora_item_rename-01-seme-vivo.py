# -*- coding: utf-8 -*-

from src.defer import defer

# === COSTANTI =================================================================

PROTO_CESPUGLIO_CODE = "flora_item_rename-07-cespuglio-semi"

# === FUNZIONI =================================================================

def on_next_stage(old_entity, new_entity, choised_attr, entities):
    if not old_entity.specials or 'ancestors' not in old_entity.specials:
        new_entity.specials['ancestors']=False
    else:
        for key in old_entity.specials.keys():
            new_entity.specials[key] = old_entity.specials[key]
    return False

def after_inject(seme, room):
    # Defer necessaria perché l'inject avviene priam che sian assegnate 
    # le special dal next_stage del cespuglio di semi

    # ORCOCAN!
    # Se passo alla defer seme e poi faccio un seme.location dice che non esiste quando invece
    # non crea problemi se lo faccio qui. PERCHE'?
    print ">>> inserimento seme via inject ()"
    if seme.location.IS_ITEM and seme.location.prototype.code == PROTO_CESPUGLIO_CODE:
        cespuglio = seme.location
    else:
        cespuglio = None
    defer(1, after_inject_deferred, seme, cespuglio)
    return False

def after_inject_deferred(seme, cespuglio):
    print ">>> inserimento seme via inject (after defer)"
    #if seme.location.IS_ITEM and seme.location.prototype.code == PROTO_CESPUGLIO_CODE:
    #    cespuglio = seme.location
        # qui stampa un dict vuoto come se l'inject avvenisse prima che la next stage precedente abbia messo i valori di specials
    if cespuglio and cespuglio.specials:
        print " <<<<----CESPUGLIO SPECIALS----->>>>"
        try:
            print cespuglio.specials
            for key in cespuglio.specials:
                seme.specials[key] = cespuglio.specials[key]
        except AttributeError:
            print "nessuna special a 'sto cacchio di cespuglio", cespuglio
    # funziona su icreate
    # funziona su reboot all'atto del reset del file area 
    else:
        print "no inside cespuglio or cespuglio special cespuglio "
        seme.specials['ancestors'] = False
        #set_ancestors(seme)
    return False

#def after_reset(seme):
#    print ">>> inserimento seme via reset"
#    set_ancestors(seme)
#    return False

def set_ancestors(seme):
    if not seme.specials:
        seme.specials['ancestors'] = False
    return False


### metodo per passare alle special il valori come sctringa
#dict1 = {'one':1, 'two':2, 'three': {'three.1': 3.1, 'three.2': 3.2 }}
#str1 = str(dict1)
#
#dict2 = eval(str1)
#
#print dict1==dict2
