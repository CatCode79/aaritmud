# -*- coding: utf-8 -*-

"""
Modulo per le entità di tipo arma.
"""


#= IMPORT ======================================================================

from src.element import Element, Flags
from src.enums   import WEAPON, WEAPONFLAG
from src.log     import log
from src.utility import copy_existing_attributes


#= CLASSI ======================================================================

class Weapon(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment  = ""
        self.category = Element(WEAPON.NONE)   # Tipo di arma
        self.flags    = Flags(WEAPONFLAG.NONE) # Flag di arma
        self.damage   = ""  # Danno dell'arma, se vuoto viene ricavato automaticamente tramite una tabella
    #- Fine Inizializzazione -

    def __str__(self):
        return "%r: %s" % (self, sorted(self.__dict__))
    #- Fine Metodo -

    def get_error_message(self, entity):
        if self.category.get_error_message(WEAPON, "category") != "":
            return self.category.get_error_message(WEAPON, "category")
        elif self.flags.get_error_message(WEAPONFLAG, "flags") != "":
            return self.category.get_error_message(WEAPONFLAG, "flags")

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Weapon()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, weapon2):
        if not weapon2:
            return False

        if self.comment != weapon2.comment:
            return False
        if self.category != weapon2.category:
            return False
        if self.flags != weapon2.flags:
            return False
        if self.damage != weapon2.damage:
            return False

        return True
    #- Fine Metodo -
