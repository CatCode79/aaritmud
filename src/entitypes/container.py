# -*- coding: utf-8 -*-

"""
Modulo per la gestione della tipologia di entità relativa ad un contenitore.
"""


#= IMPORT ======================================================================

from src.element   import Flags
from src.enums     import CONTAINER, SEX, TRUST
from src.utility   import copy_existing_attributes

from src.entitypes.__openable__ import OpenableGenericType


#= CLASSI ======================================================================

class Container(OpenableGenericType):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"max_weight" : ("", "weight")}
    REFERENCES  = {}
    WEAKREFS    = {}

    CLOSED_FLAG = CONTAINER.CLOSED
    SECRET_FLAG = CONTAINER.SECRET

    def __init__(self):
        super(Container, self).__init__()

        self.flags      = Flags(CONTAINER.NONE)  # Flag speciali di contenitore, sono praticamente uguali a quelle della porta
        self.max_weight = 0  # Massimo peso in grammi riempibile
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        msg = super(Container, self).get_error_message(entity)
        if msg:
            return msg
        elif self.flags.get_error_message(CONTAINER, "flags") != "":
            return self.flags.get_error_message(CONTAINER, "flags")
        # Viene accettato il valore zero per fare degli oggetti che sembrano
        # contenitori ma che non possono contenere nulla
        elif self.max_weight < 0:
            return "max_weight è minore di 0: %d" % self.max_weight

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Container()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, container2):
        if not container2:
            return False

        if not super(Container, self).equals(container2):
            return False

        if self.flags != container2.flags:
            return False
        if self.max_weight != container2.max_weight:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_status(self, sex, looker=None):
        status = ""

        if CONTAINER.CLOSED in self.flags:
            # Se il contenitore è segreto non visualizza lo stato di aperto o chiuso
            if CONTAINER.SECRET not in self.flags:
                if sex == SEX.FEMALE:
                    status += " chiusa"
                else:
                    status += " chiuso"
        else:
            if sex == SEX.FEMALE:
                status += " aperta"
            else:
                status += " aperto"

        if looker and looker.trust >= TRUST.MASTER and CONTAINER.SECRET in self.flags:
            status += " (secret)"

        return status
    #- Fine Metodo -
