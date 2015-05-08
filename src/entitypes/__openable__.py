# -*- coding: utf-8 -*-

"""
Codice per la gestione generica delle porte e dei contenitori.
"""


#= IMPORT ======================================================================

from src.color    import color_first_upper
from src.database import database
from src.enums    import TO
from src.log      import log


#= CLASSI ======================================================================

class OpenableGenericType(object):
    """
    Classe generica per la tipologia di Door e Container.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    # DOOR.CLOSED o CONTAINER.CLOSE a seconda della classe che eredita questa
    CLOSED_FLAG = None
    SECRET_FLAG = None

    def __init__(self):
        self.comment                = ""
        self.key_code               = ""   # Codice della chiave che serve ad aprire la porta
        self.pick_lock_difficulty   = 0    # Livello di difficoltà per il pick lock
        self.entity_open_message    = ""   # Messaggio d'apertura stile act all'entità che apre
        self.target_open_message    = ""   # Messaggio d'apertura stile act all'entità door
        self.others_open_message    = ""   # Messaggio d'apertura stile act a tutti gli altri
        self.entity_close_message   = ""   # Messaggio di chiusura stile act all'entità che apre
        self.target_close_message   = ""   # Messaggio di chiusura stile act all'entità door
        self.others_close_message   = ""   # Messaggio di chiusura stile act a tutti gli altri
        self.entity_lock_message    = ""   # Messaggio di blocco(key) stile act all'entità che apre
        self.target_lock_message    = ""   # Messaggio di blocco(key) stile act all'entità door
        self.others_lock_message    = ""   # Messaggio di blocco(key) stile act a tutti gli altri
        self.entity_unlock_message  = ""   # Messaggio di sblocco(key) stile act all'entità che apre
        self.target_unlock_message  = ""   # Messaggio di sblocco(key) stile act all'entità door
        self.others_unlock_message  = ""   # Messaggio di sblocco(key) stile act a tutti gli altri
        self.entity_eatkey_message  = ""   # Messaggio di distruzione(key) stile act all'entità che sblocca
        self.others_eatkey_message  = ""   # Messaggio di distruzione(key) stile act a tutti gli altri
        self.target_eatkey_message  = ""   # Messaggio di distruzione(key) stile act alla chiave
        self.entity_unbolt_message  = ""   # Messaggio di svincolo(bolt) stile act all'entità che apre
        self.target_unbolt_message  = ""   # Messaggio di svincolo(bolt) stile act all'entità door
        self.others_unbolt_message  = ""   # Messaggio di svincolo(bolt) stile act a tutti gli altri
        self.entity_bolt_message    = ""   # Messaggio di blocco(bolt) stile act all'entità che apre
        self.target_bolt_message    = ""   # Messaggio di blocco(bolt) stile act all'entità door
        self.others_bolt_message    = ""   # Messaggio di blocco(bolt) stile act a tutti gli altri
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if self.key_code and self.key_code not in database["proto_items"]:
            return "key_code non è un codice di oggetto prototipo valido: %s" % self.key_code
        elif self.pick_lock_difficulty < 0:
            return "pick_lock_difficulty non può essere negativo: %s" % self.pick_lock_difficulty

        # L'esistenza dei diversi messaggi è slegata tra loro, ovvero possono
        # essere inizializzati tutti come solo uno di loro o, naturalmente,
        # nessuno, quindi non vi è bisogno di controllarli

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None):
        raise NotImplementedError
    #- Fine Metodo -

    def equals(self, openable2):
        if not openable2:
            return False

        if self.comment != openable2.comment:
            return False
        if self.key_code != openable2.key_code:
            return False
        if self.pick_lock_difficulty != openable2.pick_lock_difficulty:
            return False
        if self.entity_open_message != openable2.entity_open_message:
            return False
        if self.target_open_message != openable2.target_open_message:
            return False
        if self.others_open_message != openable2.others_open_message:
            return False
        if self.entity_close_message != openable2.entity_close_message:
            return False
        if self.target_close_message != openable2.target_close_message:
            return False
        if self.others_close_message != openable2.others_close_message:
            return False
        if self.entity_lock_message != openable2.entity_lock_message:
            return False
        if self.target_lock_message != openable2.target_lock_message:
            return False
        if self.others_lock_message != openable2.others_lock_message:
            return False
        if self.entity_unlock_message != openable2.entity_unlock_message:
            return False
        if self.target_unlock_message != openable2.target_unlock_message:
            return False
        if self.others_unlock_message != openable2.others_unlock_message:
            return False
        if self.entity_eatkey_message != openable2.entity_eatkey_message:
            return False
        if self.others_eatkey_message != openable2.others_eatkey_message:
            return False
        if self.target_eatkey_message != openable2.target_eatkey_message:
            return False
        if self.entity_unbolt_message != openable2.entity_unbolt_message:
            return False
        if self.target_unbolt_message != openable2.target_unbolt_message:
            return False
        if self.others_unbolt_message != openable2.others_unbolt_message:
            return False
        if self.entity_bolt_message != openable2.entity_bolt_message:
            return False
        if self.target_bolt_message != openable2.target_bolt_message:
            return False
        if self.others_bolt_message != openable2.others_bolt_message:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def send_open_messages(self, entity, target, verbs, direction=None, destination_room=None, target_on_destination=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return False

        # ---------------------------------------------------------------------

        if self.entity_open_message:
            message = self.entity_open_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "%s $N." % color_first_upper(verbs["you"])
        entity.act(message, TO.ENTITY, target, destination_room, target_on_destination)

        if self.others_open_message:
            message = self.others_open_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$n %s $N." % verbs["it"].lower()
        entity.act(message, TO.OTHERS, target, destination_room, target_on_destination)

        if entity != target:
            if self.target_open_message:
                message = self.target_open_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "$n ti %s." % verbs["it"].lower()
            entity.act(message, TO.TARGET, target, destination_room, target_on_destination)
    #- Fine Metodo -

    def send_close_messages(self, entity, target, verbs, direction=None, destination_room=None, target_on_destination=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return False

        # ---------------------------------------------------------------------

        if self.entity_close_message:
            message = self.entity_close_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "%s $N." % color_first_upper(verbs["you"])
        entity.act(message, TO.ENTITY, target, destination_room, target_on_destination)

        if self.others_close_message:
            message = self.others_close_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$n %s $N." % verbs["it"].lower()
        entity.act(message, TO.OTHERS, target, destination_room, target_on_destination)

        if entity != target:
            if self.target_close_message:
                message = self.target_close_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "$n ti %s." % verbs["it"].lower()
            entity.act(message, TO.TARGET, target, destination_room, target_on_destination)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def send_lock_messages(self, entity, target, verbs, direction=None, destination_room=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return False

        # ---------------------------------------------------------------------

        if self.entity_lock_message:
            message = self.entity_lock_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "%s $N." % color_first_upper(verbs["you"])
        entity.act(message, TO.ENTITY, target, destination_room)

        if self.others_lock_message:
            message = self.others_lock_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$n %s $N." % verbs["it"].lower()
        entity.act(message, TO.OTHERS, target, destination_room)

        if entity != target:
            if self.target_lock_message:
                message = self.target_lock_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "$n ti %s." % verbs["it"].lower()
            entity.act(message, TO.TARGET, target, destination_room)
    #- Fine Metodo -

    def send_unlock_messages(self, entity, target, verbs, direction=None, destination_room=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return False

        # ---------------------------------------------------------------------

        if self.entity_unlock_message:
            message = self.entity_unlock_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "%s $N." % color_first_upper(verbs["you"])
        entity.act(message, TO.ENTITY, target, destination_room)

        if self.others_unlock_message:
            message = self.others_unlock_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$n %s $N." % verbs["it"].lower()
        entity.act(message, TO.OTHERS, target, destination_room)

        if entity != target:
            if self.target_unlock_message:
                message = self.target_unlock_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "$n ti %s." % verbs["it"].lower()
            entity.act(message, TO.TARGET, target, destination_room)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def send_eatkey_messages(self, entity, target, key, direction=None, destination_room=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        # ---------------------------------------------------------------------

        if self.entity_eatkey_message:
            message = self.entity_unlock_message
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$N ti si polverizza in mano"
        entity.act(message, TO.ENTITY, key, destination_room)

        if self.others_eatkey_message:
            message = self.entity_unlock_message
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$N si polverizza fra le mani di $n"
        entity.act(message, TO.OTHERS, key, destination_room)

        if entity != target:
            if self.target_eatkey_message:
                message = self.entity_unlock_message
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "Tu che sei $N ti polverizzi"
            entity.act(message, TO.TARGET, key, destination_room)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def send_bolt_messages(self, entity, target, verbs, direction=None, destination_room=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return False

        # ---------------------------------------------------------------------

        if self.entity_bolt_message:
            message = self.entity_bolt_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "%s $N." % color_first_upper(verbs["you"])
        entity.act(message, TO.ENTITY, target, destination_room)

        if self.others_bolt_message:
            message = self.others_bolt_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$n %s $N." % verbs["it"].lower()
        entity.act(message, TO.OTHERS, target, destination_room)

        if entity != target:
            if self.target_bolt_message:
                message = self.target_bolt_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "$n ti %s." % verbs["it"].lower()
            entity.act(message, TO.TARGET, target, destination_room)
    #- Fine Metodo -

    def send_unbolt_messages(self, entity, target, verbs, direction=None, destination_room=None):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return False

        # ---------------------------------------------------------------------

        if self.entity_unbolt_message:
            message = self.entity_unbolt_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you"])
                else:
                    message = message % verbs["you"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "%s $N." % color_first_upper(verbs["you"])
        entity.act(message, TO.ENTITY, target, destination_room)

        if self.others_unbolt_message:
            message = self.others_unbolt_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it"])
                else:
                    message = message % verbs["it"].lower()
            if "%dir" in message:
                if message.startswith("%dir"):
                    message = message % color_first_upper(direction.to_dir2)
                else:
                    message = message % direction.to_dir2.lower()
        else:
            message = "$n %s $N." % verbs["it"].lower()
        entity.act(message, TO.OTHERS, target, destination_room)

        if entity != target:
            if self.target_unbolt_message:
                message = self.target_unbolt_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["it"])
                    else:
                        message = message % verbs["it"].lower()
                if "%dir" in message:
                    if message.startswith("%dir"):
                        message = message % color_first_upper(direction.to_dir2)
                    else:
                        message = message % direction.to_dir2.lower()
            else:
                message = "$n ti %s." % verbs["it"].lower()
            entity.act(message, TO.TARGET, target, destination_room)
    #- Fine Metodo -
