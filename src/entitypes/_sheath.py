# -*- coding: utf-8 -*-

"""
Modulo per la tipologie di entità fodero.
"""

#= IMPORT ======================================================================

from src.log import log


#= CLASSI ======================================================================

class SheathType(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {"entity" : ["items", "mobs"]}
    WEAKREFS    = {}

    def __init__(self):
        self.comment = ""
        self.entity  = None
    #- Fine Inizializzazione -
