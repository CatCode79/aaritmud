# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

import random

from twisted.internet import reactor

from src.enums import TO


#= FUNZIONI ====================================================================

def on_reset(entity):
    start_to_bothering_me(entity)
#- Fine Funzione -


def start_to_bothering_me(entity):
    entity.act("Vi rompo le palle perché mi va' parapunzipunzipà!", TO.OTHERS)
    entity.act("Vi rompo le palle perché mi va' parapunzipunzipà!", TO.ENTITY)
    reactor.callLater(random.randint(10, 20), start_to_bothering_me, entity)
#- Fine Funzione -
