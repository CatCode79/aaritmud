# -*- coding: utf-8 -*-

"""
Modulo per la gestione della tipologia di entità utilizzabile con il comando
enter: i portali.
"""


#= IMPORT ======================================================================

import random

from src.color    import color_first_upper
from src.database import database
from src.element  import Flags
from src.enums    import PORTAL, TO
from src.utility  import copy_existing_attributes


#= CLASSI ======================================================================

class Portal(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"destination" : ("src.room", "Destination")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment                = ""
        self.flags                  = Flags(PORTAL.NONE)  # Flags relative ai portali
        self.destination            = None  # Destinazione raggiunta entrando nell'entità
        self.target_code            = ""    # Se impostata è l'entità che il portale raggiunge, se ve ne sono più istanze dello stesso tipo raggiunge la prima che capita
        self.entity_no_room_message = ""    # Messaggio di non funzionamento del portale per l'entità che entra
        self.target_no_room_message = ""    # Messaggio di non funzionamento del portale per il medesimo
        self.others_no_room_message = ""    # Messaggio di non funzionamento del portale per tutti gli altri
        self.entity_enter_message   = ""    # Messaggio d'entrata stile act all'entità che entra
        self.target_enter_message   = ""    # Messaggio d'entrata stile act all'entità portale
        self.others_enter_message   = ""    # Messaggio d'entrata stile act a tutti gli altri
        self.entity_exit_message    = ""    # Messaggio d'uscita stile act all'entità che entra
        self.target_exit_message    = ""    # Messaggio d'uscita stile act all'entità portale
        self.others_exit_message    = ""    # Messaggio d'uscita stile act a tutti gli altri
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if not self.destination and not self.target_code:
            return "destination e target_code sono tutte e due non validi: %r" % self.destination

        # L'esistenza dei diversi messaggi è slegata tra loro, ovvero possono
        # essere inizializzati tutti come solo uno di loro o, ovviamente,
        # nessuno
        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Portal()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, portal2):
        if not portal2:
            return False

        if self.comment != portal2.comment:
            return False
        if self.flags != portal2.flags:
            return False
        if self.destination.equals(portal2.destination):
            return False
        if self.target_code != portal2.target_code:
            return False
        if self.entity_no_room_message != portal2.entity_no_room_message:
            return False
        if self.target_no_room_message != portal2.target_no_room_message:
            return False
        if self.others_no_room_message != portal2.others_no_room_message:
            return False
        if self.entity_enter_message != portal2.entity_enter_message:
            return False
        if self.target_enter_message != portal2.target_enter_message:
            return False
        if self.others_enter_message != portal2.others_enter_message:
            return False
        if self.entity_exit_message != portal2.entity_exit_message:
            return False
        if self.target_exit_message != portal2.target_exit_message:
            return False
        if self.others_exit_message != portal2.others_exit_message:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_destination_room(self, target):
        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return None

        # ---------------------------------------------------------------------

        destination_room = None
        if self.destination:
            # Potrebbe essere normale che non esista nessuna stanza alle
            # coordinate e che quindi destination_room sia a None, dipende
            # dai reset
            destination_room = self.destination.get_room()

        if destination_room:
            # Se oltre alle coordinate di destinazione è stata definita
            # l'etichetta con il codice dell'entità a cui puntare si assicura
            # che almeno un'entità di quel tipo esista nella stanza.
            if self.target_code:
                type = self.target_code.split("_", 2)[1]
                for entity in getattr(destination_room, type):
                    if (hasattr(entity, "prototype") and entity.prototype.code == self.target_code
                    or entity.code == self.target_code):
                        return destination_room
                return None
            # Altrimenti se non è stato impostato nessun target ritorna come
            # destinazione la stanza alle coordinate
            else:
                return destination_room

        # Se è stato impostato un codice di entità come obiettivo del portale
        # cerca tutte le istanze di quel tipo e ne pesca una a caso
        if self.target_code:
            entities = []
            type = self.target_code.split("_", 2)[1]
            for entity in database[type + "s"].itervalues():
                if (hasattr(entity, "prototype") and entity.prototype.code == self.target_code
                or entity.code == self.target_code):
                    entities.append(entity)
            if entities:
                return random.choice(entities).location

        # Se arriva fino a qui significa che tutte le entità con quel codice
        # sono attualmente state estratte dal Mud (uccise per esempio)
        return None
    #- Fine Metodo -

    def send_no_room_messages(self, entity, target, verbs):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        # ---------------------------------------------------------------------

        if self.entity_no_room_message:
            message = "\n" + self.entity_no_room_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["infinitive"])
                else:
                    message = message % verbs["infinitive"].lower()
        else:
            message = "\nProvi ad %s in $N ma qualcosa non funziona..." % verbs["infinitive"]
        entity.act(message, TO.ENTITY, target)

        if self.others_no_room_message:
            message = self.others_no_room_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["infinitive"])
                else:
                    message = message % verbs["infinitive"].lower()
        else:
            message = "$n prova ad %s dentro $N ma qualcosa non funziona..." % verbs["infinitive"]
        entity.act(message, TO.OTHERS, target)

        if entity != target:
            if self.target_no_room_message:
                message = self.target_no_room_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["infinitive"])
                    else:
                        message = message % verbs["infinitive"].lower()
            else:
                message = "$n prova ad %s dentro te ma non hai il collegamento di destinazione." % verbs["infinitive"]
            entity.act(message, TO.TARGET, target)
    #- Fine Metodo -

    def send_enter_messages(self, entity, target, verbs, fleeing):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        # ---------------------------------------------------------------------

        # (TD) Se l'entità conosce target fare visualizzare questo messaggio,
        # altrimenti fare visualizzare un postfisso: 'andando chissà dove'
        if fleeing:
            verb = "Fuggi"
        else:
            verb = color_first_upper(verbs["you"])
        if self.entity_enter_message:
            message = "\n" + self.entity_enter_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verb)
                else:
                    message = message % verb.lower()
        else:
            if entity == target:
                message = "[royalblue]%s[close] in te stess$o.\n" % verb
            else:
                message = "[royalblue]%s[close] in $N.\n" % verb
        entity.act(message, TO.ENTITY, target, entity.location, entity.previous_location())

        if fleeing:
            verb = "fugge"
        else:
            verb = verbs["it"].lower()
        if self.others_enter_message:
            message = self.others_enter_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verb)
                else:
                    message = message % verb.lower()
        else:
            if entity == target:
                message = "$n [royalblue]%s[close] in sé stess$o andando chissà dove..." % verb
            else:
                message = "$n [royalblue]%s[close] in $N andando chissà dove..." % verb
        entity.act(message, TO.OTHERS, target, entity.location, entity.previous_location())

        if entity != target:
            if fleeing:
                verb = "fugge"
            else:
                verb = verbs["it"].lower()
            if self.target_enter_message:
                message = self.target_enter_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verb)
                    else:
                        message = message % verb.lower()
            else:
                message = "$n [royalblue]%s[close] in te." % verb
            entity.act(message, TO.TARGET, target, entity.location, entity.previous_location())
    #- Fine Metodo -

    def show_exit_messages(self, entity, target, verbs, fleeing):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return

        # ---------------------------------------------------------------------

        if self.entity_exit_message:
            message = "\n" + self.entity_exit_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["you2"])
                else:
                    message = message % verbs["you2"].lower()
        else:
            message = "\n%s in $l." % verbs["you2"]
        entity.act(message, TO.ENTITY, target)

        if self.others_exit_message:
            message = self.others_exit_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message % color_first_upper(verbs["it2"])
                else:
                    message = message % verbs["it2"].lower()
        else:
            message = "$n %s da chissà dove..." % verbs["it2"]
        entity.act(message, TO.OTHERS, target)

        if entity != target:
            if self.target_exit_message:
                message = self.target_exit_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message % color_first_upper(verbs["destination2"])
                    else:
                        message = message % verbs["destination2"].lower()
            else:
                message = "$n %s da te in $l." % verbs["destination2"]
            entity.act(message, TO.TARGET, target, entity.location, entity.previous_location())
    #- Fine Metodo -
