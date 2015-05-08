# -*- coding: utf-8 -*-

"""
Codice per la gestione generica delle tipologie cibo e bevande.
"""


#= IMPORT ======================================================================

from src.color   import color_first_upper
from src.enums   import TO
from src.log     import log
from src.utility import copy_existing_attributes


#= CLASSI ======================================================================

class SwallowableGenericType(object):
    """
    Classe generica per la tipologia di Food e Drink.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"vegetable" : ("", "percent"),
                    "animal"   : ("", "percent")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment        = ""
        # Se la somma degli attributi vegetable e animal non è uguale a 100
        # significa che il resto del cibo è formato da liquido dissetante,
        # acqua o sangue chessia.
        self.animal         =  0  # Indica in percentuale quanto il cibo è di origine animale
        self.vegetable      =  0  # Indica in percentuale quanto il cibo è di origine vegetale
        self.cooking_damage =  0  # Danni inflitti da un'impropria preparazione del cibo
        self.hours          =  0  # Ore dalla preparazione del cibo
        self.entity_message = ""  # Messaggio inviato a chi mangia
        self.target_message = ""  # Messaggio inviato a chi è mangiato
        self.others_message = ""  # Messaggio inviato a tutti gli altri
        self.affects        = []  # Lista degli effetti che si attivano mangiando
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if self.vegetable < 0 or self.vegetable > 100:
            return "vegetable non è un valore tra 0 e 100: %d" % self.vegetable
        elif self.animal < 0 or self.animal > 100:
            return "animal non è un valore tra 0 e 100: %d" % self.animal
        elif self.animal + self.vegetable > 100:
            return "animal e vegetable superano il 100%%. animal: %d vegetable: %d" % (self.animal, self.vegetable)
        # (TD) check sugli effetti
        # L'esistenza dei diversi messaggi è slegata tra loro, ovvero possono
        # essere inizializzati tutti come solo uno di loro o, ovviamente,
        # nessuno
        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = SwallowableGenericType()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, swallowable2):
        if not swallowable2:
            return False

        if self.comment != swallowable2.comment:
            return False
        if self.animal != swallowable2.animal:
            return False
        if self.vegetable != swallowable2.vegetable:
            return False
        if self.cooking_damage != swallowable2.cooking_damage:
            return False
        if self.hours != swallowable2.hours:
            return False
        if self.entity_message != swallowable2.entity_message:
            return False
        if self.target_message != swallowable2.target_message:
            return False
        if self.others_message != swallowable2.others_message:
            return False

        if len(self.affects) != len(swallowable2.affects):
            return False
        for affect in self.affects:
            for affect2 in swallowable2.affects:
                if affect == affect2:
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def send_messages(self, entity, target, verbs):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return

        # ---------------------------------------------------------------------

        if self.entity_message:
            message = self.entity_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
        else:
            sating_descr = ""
            if entity.IS_ITEM or entity.hunger <= 0:
                sating_descr = ", saziandoti."
            if entity == target:
                message = "Ti %s%s" % (verbs["you"].lower(), sating_descr)
            else:
                message = "%s $N%s" % (color_first_upper(verbs["you"]), sating_descr)
        entity.act(message, TO.ENTITY, target)

        if self.others_message:
            message = self.others_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
        else:
            if entity == target:
                message = "$n si %s!" % verbs["it"]
            else:
                message = "$n %s $N" % verbs["it"]
        entity.act(message, TO.OTHERS, target)

        if entity != target:
            message = ""
            if self.target_message:
                message = self.target_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
            else:
                message = "$n ti %s" % verbs["it"].lower()
            entity.act(message, TO.TARGET, target)
    #- Fine Metodo -
