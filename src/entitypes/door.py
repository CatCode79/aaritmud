# -*- coding: utf-8 -*-

"""
Modulo per la gestione della tipologia di entità utilizzabile con il comando
enter: i portali.
"""


#= IMPORT ======================================================================

from src.calendar import calendar
from src.element  import Flags
from src.enums    import DIR, DOOR, SEX, TO, TRUST
from src.log      import log
from src.utility  import copy_existing_attributes

from src.entitypes.__openable__ import OpenableGenericType


#= CLASSI ======================================================================

class Door(OpenableGenericType):
    #PRIMARY_KEY = ""
    #VOLATILES   = []
    #MULTILINES  = []
    #SCHEMA      = {}
    #REFERENCES  = {}
    #WEAKREFS    = {}

    CLOSED_FLAG = DOOR.CLOSED
    SECRET_FLAG = DOOR.SECRET

    def __init__(self):
        super(Door, self).__init__()

        self.flags                      = Flags(DOOR.NONE)
        self.bash_difficulty            = 0    # Livello di difficoltà per il bash
        self.pass_door_difficulty       = 0    # Livello di difficoltà per il pass door
        self.destination_open_message   = ""   # Messaggio d'apertura stile act a tutti gli altri al di là della porta
        self.destination_close_message  = ""   # Messaggio di chiusura stile act a tutti gli altri al di là della porta
        self.destination_lock_message   = ""   # Messaggio di blocco(key) stile act a tutti gli altri al di là della porta
        self.destination_unlock_message = ""   # Messaggio di sblocco(key) stile act a tutti gli altri al di là della porta
        self.destination_bolt_message   = ""   # Messaggio di sprangata(bolt) stile act a tutti gli altri al di là della porta
        self.destination_unbolt_message = ""   # Messaggio di desprangata(bolt) stile act a tutti gli altri al di là della porta
        self.reset_open_message         = ""   # Messaggio di apertura di una porta tramite un reset
        self.reset_close_message        = ""   # Messaggio di chiusura di una porta tramite un reset
        self.open_icon                  = ""   # Icona rappresentante la porta aperta di giorno
        self.open_icon_night            = ""   # Icona rappresentante la porta aperta di notte
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        msg = super(Door, self).get_error_message(entity)
        if msg:
            return msg
        elif self.flags.get_error_message(DOOR, "flags") != "":
            return self.flags.get_error_message(DOOR, "flags")
        elif self.bash_difficulty < 0:
            return "bash_difficulty non può essere negativo: %s" % self.bash_difficulty
        elif self.pass_door_difficulty < 0:
            return "pass_door_difficulty non può essere negativo: %s" % self.pass_door_difficulty

        # L'esistenza dei diversi messaggi è slegata tra loro, ovvero possono
        # essere inizializzati tutti come solo uno di loro o, naturalmente,
        # nessuno, quindi non vi è bisogno di controllarli

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Door()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, door2):
        if not door2:
            return False

        if not super(Door, self).equals(door2):
            return False

        if self.flags != door2.flags:
            return False
        if self.bash_difficulty != door2.bash_difficulty:
            return False
        if self.pass_door_difficulty != door2.pass_door_difficulty:
            return False
        if self.destination_open_message != door2.destination_open_message:
            return False
        if self.destination_close_message != door2.destination_close_message:
            return False
        if self.destination_lock_message != door2.destination_lock_message:
            return False
        if self.destination_unlock_message != door2.destination_unlock_message:
            return False
        if self.destination_bolt_message != door2.destination_bolt_message:
            return False
        if self.destination_unbolt_message != door2.destination_unbolt_message:
            return False
        if self.reset_open_message != door2.reset_open_message:
            return False
        if self.reset_close_message != door2.reset_close_message:
            return False
        if self.open_icon != door2.open_icon:
            return False
        if self.open_icon_night != door2.open_icon_night:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_status(self, sex, looker=None):
        status = ""

        if DOOR.CLOSED in self.flags:
            if sex == SEX.FEMALE:
                status += " chiusa"
            else:
                status += " chiuso"
        else:
            if sex == SEX.FEMALE:
                status += " aperta"
            else:
                status += " aperto"

        if looker and looker.trust >= TRUST.MASTER and DOOR.SECRET in self.flags:
            status += " (secret)"

        return status
    #- Fine Metodo -

    def get_icon(self):
        icon = ""
        if calendar.is_night():
            icon = self.open_icon_night

        if not icon:
            icon = self.open_icon

        return icon
    #- Fine Metodo -

    #---------------------------------------------------------------------------

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

        super(Door, self).send_open_messages(entity, target, verbs, direction, destination_room, target_on_destination)

        if destination_room and direction:
            target = target_on_destination or target
            if self.destination_open_message:
                message = self.destination_open_message
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
                message = "Qualcuno, dall'altra parte, %s $N %s" % (verbs["it"].lower(), direction.reverse_dir.to_dir2)
            entity.act(message, TO.OTHERS, target, destination_room, target_on_destination, send_to_location=destination_room)
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

        super(Door, self).send_close_messages(entity, target, verbs, direction, destination_room, target_on_destination)

        # Cose riguardanti solo le porte
        if destination_room and direction:
            target = target_on_destination or target
            if self.destination_close_message:
                message = self.destination_close_message
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
                message = "Qualcuno, dall'altra parte, %s $N %s" % (verbs["it"].lower(), direction.reverse_dir.to_dir2)
            entity.act(message, TO.OTHERS, target, destination_room, target_on_destination, send_to_location=destination_room)
    #- Fine Metodo -

    #---------------------------------------------------------------------------

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

        super(Door, self).send_lock_messages(entity, target, verbs, direction, destination_room)

        if destination_room:
            if self.destination_lock_message:
                message = self.destination_lock_message
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
                message = "Qualcuno, dall'altra parte, %s $N %s" % (verbs["it"].lower(), direction.reverse_dir.to_dir2)
            entity.act(message, TO.OTHERS, target, destination_room, send_to_location=destination_room)
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

        super(Door, self).send_unlock_messages(entity, target, verbs, direction, destination_room)

        if destination_room:
            if self.destination_unlock_message:
                message = self.destination_unlock_message
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
                message = "Qualcuno, dall'altra parte, %s $N %s" % (verbs["it"].lower(), direction.reverse_dir.to_dir2)
            entity.act(message, TO.OTHERS, target, destination_room, send_to_location=destination_room)
    #- Fine Metodo -

    #---------------------------------------------------------------------------

    def send_unbolt_messages(self, entity, target, verbs, destination_room=None, direction=None):
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

        super(Door, self).send_unbolt_messages(entity, target, verbs, direction, destination_room)

        if destination_room and direction:
            if self.destination_unbolt_message:
                message = self.destination_unbolt_message
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
                message = "Qualcuno, dall'altra parte, %s $N %s" % (verbs["it"].lower(), direction.reverse_dir.to_dir2)
            entity.act(message, TO.OTHERS, target, destination_room, send_to_location=destination_room)
    #- Fine Metodo -

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

        super(Door, self).send_bolt_messages(entity, target, verbs, direction, destination_room)

        # Cose riguardanti solo le porte
        if destination_room and direction:
            if self.destination_bolt_message:
                message = self.destination_bolt_message
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
                message = "Qualcuno, dall'altra parte, %s $N %s" % (verbs["it"].lower(), direction.reverse_dir.to_dir2)
            entity.act(message, TO.OTHERS, target, destination_room, send_to_location=destination_room)
    #- Fine Metodo -

#= FUNZONI =====================================================================

# (TD) convertirla in classe da mixinare in Entity
def _is_secret_door(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if entity.IS_ROOM:
        return False

    if not entity.door_type:
        return False

    if DOOR.SECRET not in entity.door_type.flags:
        return False

    return True
#- Fine Funzione -
