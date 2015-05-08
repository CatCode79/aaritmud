# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Un oggetto che conta le volte che sente un repop


#= IMPORT ======================================================================

from src.defer    import defer, defer_random_time


#= COSTANTI ====================================================================

DELAY = 1

#= FUNZIONI ====================================================================

def on_repop(item):
    if not item.specials or not "numero_di_repop" in item.specials:
        item.specials["numero_di_repop"] = 0
    print "oggetto numero random repopped"
    defer(DELAY, loop_test, item)
#- Fine Funzione -


def loop_test(item):
    #print "oggetto numero random updatinig"
    item.specials["numero_di_repop"] +=1
    item.descr = "Qui ti trovi di fronte al terribile %d!" % item.specials["numero_di_repop"]
    defer(DELAY, loop_test, item)
    
