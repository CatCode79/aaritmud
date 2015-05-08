# -*- coding: utf-8 -*-

from src.defer import defer

# === FUNZIONI =================================================================
def after_inject(seme, room):
    print ">>> inserimento seme via inject ()"
    if seme.location.IS_ITEM:
        print "######## seme è in oggetto"
        cespuglio = seme.location
    else:
        print "######## seme non è in oggetto"
        cespuglio = None
    defer(1, after_inject_deferred, seme, cespuglio)
    return False

def after_inject_deferred(seme, cespuglio):
    print ">>> inserimento semaccio via inject (after defer)"
    if cespuglio and cespuglio.specials:
        print " <<<<----CESPUGLIO SPECIALS----->>>>"
        try:
            print cespuglio.specials
            for key in cespuglio.specials:
                seme.specials[key] = cespuglio.specials[key]
        except AttributeError:
            print "nessuna special a 'sto cacchio di cespuglio", cespuglio
    else:
        print "no inside cespuglio or cespuglio special cespuglio "
        try:
            print "assegno le speciali"
            seme.specials['ancestors'] = False
        except AttributeError:
            print "nessuna special assegnabile a sto schifo di semaccio", seme
       
    return False
