# -*- coding: utf-8 -*-

"""
Modulo per la delle entità indossabili.
"""


#= IMPORT ======================================================================

from src.element import Flags
from src.enums   import TO, WEAR
from src.log     import log
from src.utility import copy_existing_attributes


#= CLASSI ======================================================================

class Wear(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"modes" : ("src.element", "Flags")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment               = ""
        self.modes                 = []  # Sono una lista di flag di parti che rappresentano i differenti modi di indossare un'entità
        self.flags                 = Flags(WEAR.NONE)  # Flag dei vestiti
        self.affects               = []  # Affect aggiunti quando si indossa l'oggetto
        self.entity_wear_message   = ""  # Messaggio inviato a chi indossa
        self.target_wear_message   = ""  # Messaggio inviato a chi è indossato
        self.others_wear_message   = ""  # Messaggio inviato a tutti gli altri
        self.entity_remove_message = ""  # Messaggio inviato a chi si rimuove l'oggetto indossato
        self.target_remove_message = ""  # Messaggio inviato a chi è stato rimosso
        self.others_remove_message = ""  # Messaggio inviato a tutti gli altri che vedono l'azione della rimozione
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if not self.modes:
            return "modes non è valido: %r" % self.modes
        # (TD) check sugli effetti
        # L'esistenza dei diversi messaggi è slegata tra loro, ovvero possono
        # essere inizializzati tutti come solo uno di loro o, ovviamente,
        # nessuno
        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Wear()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, wear2):
        if not wear2:
            return False

        if self.comment != wear2.comment:
            return False

        if len(self.modes) != len(wear2.modes):
            return False
        for mode in self.modes:
            for mode2 in wear2.modes:
                if mode == mode2:
                    break
            else:
                return False

        if len(self.affects) != len(wear2.affects):
            return False
        for affect in self.affects:
            for affect2 in wear2.affects:
                if affect == affect2:
                    break
            else:
                return False

        if self.entity_wear_message != wear2.entity_wear_message:
            return False
        if self.target_wear_message != wear2.target_wear_message:
            return False
        if self.others_wear_message != wear2.others_wear_message:
            return False
        if self.entity_remove_message != wear2.entity_remove_message:
            return False
        if self.target_remove_message != wear2.target_remove_message:
            return False
        if self.others_remove_message != wear2.others_remove_message:
            return False

        return True
    #- Fine Metodo -

    def get_upper_weared(self, target):
        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return False

        # ---------------------------------------------------------------------

        for en in target.location.iter_contains():
            if en.under_weared == target:
                return en

        return None
    #- Fine Metodo -


def send_wear_messages(entity, target, verb_you, verb_it, part_descriptions):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verb_you:
        log.bug("verb_you non è un parametro valido: %r" % verb_you)
        return

    if not verb_it:
        log.bug("verb_it non è un parametro valido: %r" % verb_it)
        return

    if not part_descriptions:
        log.bug("part_descriptions non è un parametro valido: %r" % part_descriptions)
        return

    # ---------------------------------------------------------------------

    wear_type = target.wear_type

    if wear_type.entity_wear_message:
        message = wear_type.entity_wear_message
        if "%part" in message:
            if message.startswith("%part"):
                message = message.replace("%part", color_first_upper(part_descriptions[TO.ENTITY]))
            else:
                message = message.replace("%part", part_descriptions[TO.ENTITY].lower())
    else:
        message = "%s $N %s." % (verb_you, part_descriptions[TO.ENTITY])
    entity.act(message, TO.ENTITY, target)

    if wear_type.others_wear_message:
        message = wear_type.others_wear_message
        if "%part" in message:
            if message.startswith("%part"):
                message = message.replace("%part", color_first_upper(part_descriptions[TO.OTHERS]))
            else:
                message = message.replace("%part", part_descriptions[TO.OTHERS].lower())
    else:
        message = "$n %s $N %s." % (verb_it, part_descriptions[TO.OTHERS])
    entity.act(message, TO.OTHERS, target)

    if wear_type.target_wear_message:
        message = wear_type.target_wear_message
        if "%part" in message:
            if message.startswith("%part"):
                message = message.replace("%part", color_first_upper(part_descriptions[TO.TARGET]))
            else:
                message = message.replace("%part", part_descriptions[TO.TARGET].lower())
    else:
        message = "$n ti %s %s." % (verb_it, part_descriptions[TO.TARGET])
    entity.act(message, TO.TARGET, target)
#- Fine Metodo -


def send_remove_messages(entity, target, verb_you, verb_it, part_descriptions, force_default):
    """
    Non può essere un metodo perché a volte target.wear_type può essere None.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verb_you:
        log.bug("verb_you non è un parametro valido: %r" % verb_you)
        return

    if not verb_it:
        log.bug("verb_it non è un parametro valido: %r" % verb_it)
        return

    if not part_descriptions:
        log.bug("part_descriptions non è un parametro valido: %r" % part_descriptions)
        return

    # -------------------------------------------------------------------------

    wear_type = target.wear_type

    if wear_type and wear_type.entity_remove_message and not force_default:
        message = wear_type.entity_remove_message
        if "%part" in message:
            if message.startswith("%part"):
                message = message.replace("%part", color_first_upper(part_descriptions[TO.ENTITY]))
            else:
                message = message.replace("%part", part_descriptions[TO.ENTITY].lower())
    else:
        message = "%s $N %s." % (verb_you, part_descriptions[TO.ENTITY])
    entity.act(message, TO.ENTITY, target)

    if wear_type and wear_type.others_remove_message and not force_default:
        message = wear_type.others_remove_message
        if "%part" in message:
            if message.startswith("%part"):
                message = message.replace("%part", color_first_upper(part_descriptions[TO.OTHERS]))
            else:
                message = message.replace("%part", part_descriptions[TO.OTHERS].lower())
    else:
        message = "$n %s $N %s." % (verb_it, part_descriptions[TO.OTHERS])
    entity.act(message, TO.OTHERS, target)

    if entity != target:
        if wear_type and wear_type.target_remove_message and not force_default:
            message = wear_type.target_remove_message
            if "%part" in message:
                if message.startswith("%part"):
                    message = message.replace("%part", color_first_upper(part_descriptions[TO.TARGET]))
                else:
                    message = message.replace("%part", part_descriptions[TO.TARGET].lower())
        else:
            message = "$n ti %s %s." % (verb_it, part_descriptions[TO.TARGET])
        entity.act(message, TO.TARGET, target)
#- Fine Metodo -
