# -*- coding: utf-8 -*-

"""
Modulo per la gestione degli oggetti del Mud.
"""


#= IMPORT ======================================================================

import random

from src.behaviour  import BehaviourUpdaterSuperclass
from src.config     import config
from src.engine     import engine
from src.entity     import ProtoEntity
from src.enums      import FLAG, RACE
from src.element    import Element, Flags
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import copy_existing_attributes


#= CLASSI ======================================================================

class ProtoItem(ProtoEntity):
    PRIMARY_KEY = "code"
    VOLATILES   = ProtoEntity.VOLATILES + []
    MULTILINES  = ProtoEntity.MULTILINES + []
    SCHEMA      = {"behaviour" : ("src.behaviour", "ItemBehaviour"),
                   "destroy"   : ("src.commands.command_destroy", "Destroy")}
    SCHEMA.update(ProtoEntity.SCHEMA)
    REFERENCES  = {}
    REFERENCES.update(ProtoEntity.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(ProtoEntity.WEAKREFS)

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = False
    IS_EXIT   = False
    IS_WALL   = False
    IS_ACTOR  = False
    IS_MOB    = False
    IS_ITEM   = True
    IS_PLAYER = False
    IS_EXTRA  = False
    IS_PROTO  = True

    ACCESS_ATTR   = "proto_items"
    CONSTRUCTOR = None  # Classe Item una volta che viene definita a fine modulo

    def __init__(self, code=""):
        super(ProtoItem, self).__init__()

        self.code    = code or ""
        self.destroy = None

        # Eventuale inizializzazione dei punti, la vita sarebbe intesa come condizione
        if self.max_life == 0:
            self.max_life = config.starting_points
        if self.life == 0:
            self.life = self.max_life
    #- Fine Inizializzazione -

    def get_error_message(self):
        msg = super(ProtoItem, self).get_error_message()
        if msg:
            pass
        elif "_item_" not in self.code:
            msg = "code di oggetto senza l'identificativo _item_ al suo interno"
        # (TD) aggiungere altri messaggi d'errore
        else:
            return ""

        # Se arriva fino a qui ha trovato un errore
        if type(self) == ProtoItem:
            log.bug("(ProtoItem: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    def dies(self, opponent=None, auto_loot=False, teleport_corpse=False, quantity=1):
        force_return = check_trigger(self, "before_die", self, opponent)
        if force_return:
            return
        if opponent:
            force_return = check_trigger(opponent, "before_dies", self, opponent)
            if force_return:
                return

        self.life = 0
        # Se l'entità era già stata rotta allora stavolta la fa sparire
        if self.code.startswith("rip_item_broken-"):
            remains, use_repop = None, True
        else:
            remains, use_repop = self.make_remains(auto_loot)

        force_return = check_trigger(self, "after_die", self, opponent)
        if force_return:
            return
        if opponent:
            force_return = check_trigger(opponent, "after_dies", self, opponent)
            if force_return:
                return

        self.extract(quantity, use_repop=use_repop)
    #- Fine Metodo -

    def get_area_code(self):
        """
        Ritorna il codice dell'area carpendolo dal proprio codice.
        """
        if "_item_" in self.code:
            return self.code.split("_item_", 1)[0]
        else:
            log.bug("Codice errato per l'entità %s: %s" % (self.__class__.__name__, self.code))
            return ""
    #- Fine Metodo -


class Item(ProtoItem, BehaviourUpdaterSuperclass):
    """
    Istanza di un oggetto.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ProtoItem.VOLATILES + ["prototype", "location", "contents"]
    MULTILINES  = ProtoItem.MULTILINES + []
    SCHEMA      = {"specials" : ("", "str")}
    SCHEMA.update(ProtoItem.SCHEMA)
    REFERENCES  = {"area" : ["areas"]}
    REFERENCES.update(ProtoItem.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(ProtoItem.WEAKREFS)

    ACCESS_ATTR = "items"
    IS_PROTO    = False
    CONSTRUCTOR = None  # Classe Item una volta che viene definita a fine modulo

    # Qui non bisogna passare altri attributi oltre il code, perché altrimenti
    # offuscherebbero gli attributi prototype
    def __init__(self, code=""):
        super(Item, self).__init__()
        BehaviourUpdaterSuperclass.__init__(self)

        self.code = ""
        self.prototype = None
        if code:
            self.reinit_code(code)
            copy_existing_attributes(self.prototype, self, except_these_attrs=["code"])
            self.after_copy_existing_attributes()

        # Variabili proprie di una istanza di oggetto:
        self.area        = None
        self.experience  = 0  # Esperienza accumulata prima di poter livellare
        self.specials    = {}  # E' una lista di variabili speciali, possono essere utilizzate come delle flags, vengono aggiunte di solito nei gamescript

        check_trigger(self, "on_init", self)
    # - Fine della Inizializzazione -

    def get_error_message(self):
        msg = super(Item, self).get_error_message()
        if msg:
            pass
        elif not self.code:
            msg = "codice identificativo dell'oggetto non valido."
        elif self.race.get_error_message(RACE, "race") != "":
            return self.race.get_error_message(RACE, "race")
        # (TD)
        else:
            return ""
        # Se arriva fino a qui ha trovato un errore
        if type(self) == Item:
            log.bug("(Item: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    #- Metodi strettamente relativi agli actor ---------------------------------

    def is_drunk(self):
        return False
    #- Fine Metodo -

    def has_drunk_walking(self):
        return False, False
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def skin_colorize(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # ---------------------------------------------------------------------

        return "[pink]%s[close]" % argument
    #- Fine Metodo -

    def eye_colorize(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # ---------------------------------------------------------------------

        return "[black]%s[close]" % argument
    #- Fine Metodo -

    def hair_colorize(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # ---------------------------------------------------------------------

        return "[black]%s[close]" % argument
    #- Fine Metodo -


def create_random_item(item=None):
    if not item:
        item = Item()
    item.code = "limbo_item_random"
    # (TD) da finire
    pass

    return item
#- Fine Funzione -


#= FINALIZE ====================================================================

ProtoItem.CONSTRUCTOR = Item
Item.CONSTRUCTOR = Item
