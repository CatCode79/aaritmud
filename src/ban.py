# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei ban, le punizioni di Aarit verso i giocatori.
"""

#= IMPORT ======================================================================

import datetime

from src.database import database


#= CLASSI ======================================================================

class Ban(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment", "reason"]
    SCHEMA = {"starting_from" : ("", "datetime")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment       = ""
        self.reason        = ""
        self.starting_from = None
        self.days          = 0
    #- Fine Inizializzazione -


#= FUNZIONI ====================================================================

def count_bans():
    counter = 0

    for player in database["players"].itervalues():
        if player.ban:
            counter += 1

    return counter
#- Fine Funzione -
