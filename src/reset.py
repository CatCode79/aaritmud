# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle aree e dei relativi resets.
"""

#= IMPORT ======================================================================

import random
import weakref

from twisted.internet import error, reactor

from src.calendar   import calendar
from src.color      import color_first_upper
from src.config     import config
from src.database   import database
from src.defer      import defer
from src.element    import Element, Flags
from src.engine     import engine
from src.enums      import DIR, DOOR, FLAG, LOG, MONTH, PART, RESET, ROOM, TO
from src.exit       import Exit, Wall
from src.interpret  import send_input
from src.log        import log
from src.gamescript import check_trigger
#from src.loop       import UnstoppableLoop
from src.utility    import copy_existing_attributes, is_number

from src.entitypes.money import random_moneys


#= CLASSI ======================================================================

class AreaResetsSuperclass(object):
    def get_error_message_resets(self):
        """
        Ritorna un messaggio di errore al primo reset che trova errato.
        """
        for room_reset in self.room_resets:
            msg = room_reset.get_error_message()
            if msg:
                return msg
            # Se vi è un room reset che si attiva alle stesse coordinate e allo
            # stesso momento allora è errore
            counter = 0
            for room_reset2 in self.room_resets:
                if room_reset == room_reset2:
                    continue
                if (room_reset.destination.x == room_reset2.destination.x
                and room_reset.destination.y == room_reset2.destination.y
                and room_reset.destination.z == room_reset2.destination.z
                and room_reset.minute == room_reset2.minute
                and room_reset.hour == room_reset2.hour
                and room_reset.day == room_reset2.day
                and room_reset.month == room_reset2.month
                and room_reset.year == room_reset2.year):
                    counter += 1
            if counter != 0:
                return "Ci sono %d room reset con le stesse coordinate (%d %d %d) e la stessa data (%d %d %d %s %d)" % (
                    counter,
                    room_reset.destination.x, room_reset.destination.y, room_reset.destination.z,
                    room_reset.minute, room_reset.hour, room_reset.day, room_reset.month, room_reset.year)

        return ""
    #- Fine Metodo -

    def get_room_reset(self, x, y, z):
        if x < -32000 or x > 32000:
            log.bug("x è una coordinata non valida: %d" % x)
            return None

        if y < -32000 or y > 32000:
            log.bug("y è una coordinata non valida: %d" % y)
            return None

        if z < -32000 or z > 32000:
            log.bug("z è una coordinata non valida: %d" % z)
            return None

        # ---------------------------------------------------------------------

        for room_reset in self.room_resets:
            if room_reset.destination.x == x and room_reset.destination.y == y and room_reset.destination.z == z:
                return room_reset

        return None
    #- Fine Metodo -

    def defer_reset_events(self):
        for room_reset in self.room_resets:
            if not room_reset.reset_event:
                room_reset.defer_reset_event(self)
    #- Fine Metodo -

    def stop_reset_events(self, except_these=None):
        """
        Serve a fermare tutti i reset e a pulire il riferimento per permettere
        un eventuale print di traceback.
        """
        if not except_these:
            except_these = []

        for room_reset in self.room_resets:
            if not room_reset.proto_room:
                log.bug("proto_room non valida per room_reset %r" % room_reset)
                continue
            if room_reset.proto_room.code in except_these:
                continue
            if room_reset.reset_event:
                try:
                    room_reset.reset_event.cancel()
                except (error.AlreadyCancelled, error.AlreadyCalled):
                    pass
                room_reset.reset_event = None
    #- Fine Metodo -


class RoomReset(object):
    """
    Gestisce un Reset relativo alle stanze.
    """
    PRIMARY_KEY = ""  # Questa classe fa sempre parte di liste, quindi non ha un attributo che fa da chiave primaria
    VOLATILES   = ["reset_event", "already_checked"]
    MULTILINES  = ["comment"]
    SCHEMA      = {"destination"   : ("src.room", "Destination"),
                   "messages"      : ("", "str"),
                   "entity_resets" : ("src.reset", "EntityReset"),
                   "exit_resets"   : ("src.reset", "ExitReset"),
                   "wall_resets"   : ("src.reset", "WallReset")}
    REFERENCES  = {"proto_room" : ["proto_rooms"]}
    WEAKREFS    = {}

    def __init__(self):
        self.comment       = ""   # Eventuale commento al room-reset
        self.proto_room    = None # Stanza prototipo da resettare
        self.destination   = None # Coordinate spaziali di destinazione per il resetting di questa room
        self.minute        = -1   # Minuto in cui viene resettata
        self.hour          = -1   # Ora in cui viene resettata
        self.day           = -1   # Giorno del mese in cui viene resettata
        self.month         = Element(MONTH.NONE)  # Mese in cui viene resettata
        self.year          = -1   # Anno in cui viene resettata, evento una tantum
        self.messages      = []   # Messaggi di echo letti da tutti coloro che sono nella stanza quando resetta
        self.entity_resets = []   # Lista dei reset di entità nella stanza
        self.exit_resets   = []   # Lista dei reset delle uscite nella stanza
        self.wall_resets   = []   # Lista dei reset delle mura nella stanza

        # Attributi Volatili:
        self.reset_event   = None  # Call later relativa l'evento di reset
        # L'attributo already_checked è impostato dinamicamente e solo se
        # se l'opzione per controllare i riferimenti è attiva
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%r alle %d %d %s %s %d" % (
            self.destination, self.minute, self.hour, self.day, self.month, self.year)
    #- Fine Metodo -

    def get_error_message(self):
        if not self.proto_room:
            msg = "proto_room non valida: %r" % self.proto_room
        elif self.minute < -1 or self.minute > config.minutes_in_hour - 1:
            return "minute non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.minute, config.minutes_in_hour - 1)
        elif self.hour < -1 or self.hour > config.hours_in_day - 1:
            return "hour non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.hour, config.hours_in_day - 1)
        elif self.day < -1 or self.day > config.days_in_month or self.day == 0:
            return "day non è un valore valido: %s (dev'essere tra -1 e %s)" % (self.day, config.days_in_month)
        elif self.month.get_error_message(MONTH, "month") != "":
            msg = self.month.get_error_message(MONTH, "month")
        elif self.year < -1:
            msg = "year non è un valore valido: %d (dev'essere maggiore di -1)" % self.year
        elif get_error_message_entity_resets(self) != "":
            msg = get_error_message_entity_resets(self)
        else:
            return ""

        return "(room_reset) %s" % msg
    #- Fine Metodo -

    def has_defined_date(self, check_year=False):
        """
        Ritorna vero se ha almeno uno degli attributi relativi alla data rpg
        definito.
        """
        if check_year not in (True, False):
            log.bug("check_year non è un parametro valido: %s" % check_year)
            return False

        # ---------------------------------------------------------------------

        if (self.minute != -1
        or  self.hour   != -1
        or  self.day    != -1
        or  self.month  != MONTH.NONE
        or (self.year   != -1 and check_year)):
            return True
        else:
            return False
    #- Fine Metodo -

    def finalize(self):
        """
        Inizializza eventuali valori non esplicitati dai buider riguardo la
        data di reset, se per esempio è stato impostato il mese ma non il
        resto degli attributi temporali di unità temporale minore questi
        vengono impostati per far scattare il reset all'inizio del mese.
        """
        if self.month != MONTH.NONE:
            # In questo caso l'inizio del mese
            if self.day == -1:
                self.day = 1
            if self.hour == -1:
                self.hour = 0
            if self.minute == -1:
                self.minute = 0

        if self.day != -1:
             # In questo caso all'inizio del giorno
            if self.hour == -1:
                self.hour = 0
            if self.minute == -1:
                self.minute = 0

        if self.hour != -1:
            # In questo caso basta impostarlo all'inizio dell'ora
            if self.minute == -1:
                self.minute = 0
    #- Fine Metodo -

    def defer_reset_event(self, area, avoid_zero_seconds=False):
        """
        Resetta le stanze e le entità dell'area, ma solo per quelle che hanno
        una data e/o un'ora precisa, il resto viene resettato alla partenza del
        Mud in una funzione apposita.
        """
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return

        # ---------------------------------------------------------------------

        if self.reset_event:
            # (bb) A volte nei timemachine capita e non ho compreso bene quanto
            # sia grave, per ora viene effettuata una pulizia dell'evento e
            # non un return dal metodo
            log.bug("reset_event già definito per il room reset %d %d %d %s" % (
                self.destination.x, self.destination.y, self.destination.z, area.code))
            try:
                self.reset_event.cancel()
            except (error.AlreadyCancelled, error.AlreadyCalled):
                pass
            self.reset_event = None
            #return

        if self.has_defined_date():
            # (bb) Mettiamo il caso che la get_real_seconds_to sopra ricavi un
            # tempo di 2 secondi, e che il reattore non venga avviato entro tali
            # 2 secondi, in questo caso il reset non viene avviato, attenzione!!
            # (è un baco ipotetico)
            seconds = calendar.get_real_seconds_to(self.minute, self.hour, self.day, self.month, self.year, force_advance=True)
            if seconds < 0:
                log.bug("secondi reali negativi: %d per il reset alle coordinate %d %d %d %s" % (
                    seconds, self.destination.x, self.destination.y, self.destination.z, area.code))
                return
            elif seconds == 0 and avoid_zero_seconds:
                # Serve ad evitare chiamate successive allo stesso reset
                return
            if config.use_subsequent_resets:
                self.reset_event = reactor.callLater(seconds, self.reset, area)
        else:
            self.reset(area)
    #- Fine Metodo -

    def reset(self, area):
        """
        Esegue il resetting di una stanza.
        """
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return False

        # ---------------------------------------------------------------------

        # Evita di sovrascrivere room già pronte a quella coordinata,
        # (bb) Tuttavia c'è il problema che non resetta correttamente alcune
        # stanze e che magari ci si trovano delle stanze diurne di notte,
        # questo perché magari il room reset di default è una stanza diurna ma
        # il mud si avvia di notte; è un problema che va a scemare man mano che
        # il mud è attivo e con le persistenze portate tra un boot ed un altro
        coords = "%d %d %d" % (self.destination.x, self.destination.y, self.destination.z)
        if not coords in area.rooms:
            # Controlla che se anche sembra non esservi nessuna stanza nell'area
            # alle coordinate volute potrebbe esservi nel database per errori
            # di riferimenti (non è comunque detto che sia effettivamente un
            # errore, magari è una locazione temporaneamente rimossa dal gioco
            # tramite un gamescript), tenta di correggere il problema
            for room in database["rooms"].itervalues():
                if (room.prototype and self.proto_room
                and room.prototype.code == self.proto_room.code
                and room.x == self.destination.x
                and room.y == self.destination.y
                and room.z == self.destination.z
                and room.area == self.destination.area):
                    log.bug("È stata trovata comunque una stanza nel database rooms con le stesse coordinate: coordinate %s (%s)" % (
                        coords, room.code))
                    break
            else:
                from src.room import Room
                room = Room(self.proto_room.code)

            room.inject_to_area(area, coords)
            if not engine.booting:
                log.reset("%s reset della stanza %s nell'area %s alle coordinate %s (che non contenevano nulla)." % (
                    str(calendar), room.code, area.code, coords))
        # Esegue un reset di una stanza, esegue una modifica degli attributi
        # della stanza senza rimpiazzarla tutta, in particolare viene
        # mantenuto il contenuto (oggetti, mob e giocatori)
        else:
            room = area.rooms[coords]
            # Controlla che la stanza alle coordinate esista nel database
            # delle stanze, tenta di correggere il problema
            if room.code not in database["rooms"]:
                log.bug("Non è stata trovata nessuna stanza %s nel database delle rooms (che si trova invece alle coordinate %s dell'area %s)" % (
                    room.code, coords, room.area.code))
                database["rooms"][room.code] = room

            if self.has_defined_date():
                old_exits = {}
                for direction in room.exits:
                    old_exits[direction] = room.exits[direction]

                # Dopo aver copiato gli attributi è importantissimo reinizializzare
                # il codice, altrimenti il sistema di persistenza si ritrova il
                # codice del prototipo come nome del file
                room.reinit_code(self.proto_room.code)
                copy_existing_attributes(self.proto_room, room, except_these_attrs=["code"])
                room.after_copy_existing_attributes()

                room.reset_doors(area, old_exits)

                if not engine.booting:
                    log.reset("%s: reset della stanza %s nell'area %s alle coordinate %s (che contenevano già qualcosa)." % (
                        str(calendar), room.code, area.code, coords))

        if self.messages:
            room.act("\n%s" % color_first_upper(random.choice(self.messages)))

        # Resetta tutte le entità nella stanza
        reset_path = "%d %d %d %s" % (room.x, room.y, room.z, room.prototype.code)
        for entity_reset in self.entity_resets:
            force_break = entity_reset.reset(room, reset_path)
            if force_break:
                break

        # (TD) in futuro questo pezzo direi che non esisterà a favore del
        # sistema di loop
        # Se questo reset ha una data rpg impostata allora tra un minuto
        # rpg controlla quando debba richiamare l'evento del reset stesso
        if self.has_defined_date():
            if self.reset_event:
                try:
                    self.reset_event.cancel()
                except (error.AlreadyCancelled, error.AlreadyCalled):
                    pass
                self.reset_event = None
            reactor.callLater(config.seconds_in_minute, self.defer_reset_event, area)

        return check_trigger(room, "on_reset", room)
    #- Fine Metodo -

    def check_event(self):
        if hasattr(self, "already_checked"):
            return
        if not self.reset_event:
            log.check_reset("room reset con data %d %d %d %s per la stanza %s senza evento" % (
                self.minute,
                self.hour,
                self.day,
                self.month,
                self.proto_room.code))
            #setattr(self, "already_checked", True)  # (TT)
    #- Fine Metodo -


class EntityReset(object):
    """
    Gestisce un reset relativo alle entità.
    """
    PRIMARY_KEY = ""  # Non ne ha, come per la classe RoomReset
    VOLATILES   = ["area"]
    MULTILINES  = ["comment"]
    SCHEMA      = {"destination"   : ("src.Room", "Destination"),
                   "inputs"        : ("", "str"),
                   "messages"      : ("", "str"),
                   "probability"   : ("", "percent"),
                   "entity_resets" : ("src.reset", "EntityReset")}
    REFERENCES  = {"proto_entity" : ["proto_mobs", "proto_items"]}
    WEAKREFS    = {}

    def __init__(self):
        self.comment       = ""   # Eventuale commento all'entity-reset
        self.proto_entity  = None # Entità prototipo da resettare
        self.destination   = None # Coordinate spaziali di destinazione per il resetting di questa entità
        self.minute        = -1   # Minuto in cui viene resettata
        self.hour          = -1   # Ora in cui viene resettata
        self.day           = -1   # Giorno del mese in cui viene resettata
        self.month         = Element(MONTH.NONE)  # Mese in cui viene resettata
        self.year          = -1   # Anno in cui viene resettata, evento una tantum
        self.type          = Element(RESET.NONE)  # Tipologia di reset
        self.probability   = 100  # Probabilità da 1 a 100 che un'entità venga resettata, una volta resettata la probabilità che questa venga repoppata è sempre del 100%, questa etichetta ha senso solo per le tipologie di reset che inseriscono nel gioco un'entità
        self.quantity      = 1    # Quantità di copie uguali da resettare
        self.wear_mode     = Flags(PART.NONE)  # Come viene vestita l'entità su di un altra, è volutamente possibile vestire stanze (anche se non ha senso), è volutamente possibile inserire una modalità di wear inesistente per l'oggetto, il campo ha senso solo per PUT e ADD
        self.inputs        = []   # Lista di comandi da cui sceglierne uno a caso e eseguirlo durante il reset
        self.messages      = []   # Messaggio di act letto da tutti coloro che sono nella stanza quando l'entità resetta
        self.entity_resets = []   # Lista dei possibili reset di entità contenute nell'entità
    #- Fine Inizializzazione -

    def get_error_message(self):
        if not self.proto_entity:
            msg = "proto_entity non valida"
        elif self.minute < -1 or self.minute > config.minutes_in_hour - 1:
            return "minute non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.minute, config.minutes_in_hour - 1)
        elif self.hour < -1 or self.hour > config.hours_in_day - 1:
            return "hour non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.hour, config.hours_in_day - 1)
        elif self.day < -1 or self.day > config.days_in_month or self.day == 0:
            return "day non è un valore valido: %s (dev'essere tra -1 e %s)" % (self.day, config.days_in_month)
        elif self.month.get_error_message(MONTH, "month") != "":
            msg = self.month.get_error_message(MONTH, "month")
        elif self.year < -1:
            msg = "year non è un valore valido: %d (dev'essere maggiore di -1)" % self.year
        elif self.probability <= 0 or self.probability > 100:
            msg = "probability non è un valore valido: %d (dev'essere tra 1 e 100 compresi)" % self.probabily
        elif self.type.get_error_message(RESET, "type") != "":
            msg = self.type.get_error_message(RESET, "type")
        elif self.quantity < 1:
            msg = "quantity è errata: %d" % self.quantity
        elif get_error_message_entity_resets(self) != "":
            msg = get_error_message_entity_resets(self)
        else:
            return ""

        return "(reset_entity) %s" % msg
    #- Fine Metodo -

    def has_defined_date(self, check_year=False):
        """
        Ritorna vero se ha almeno uno degli attributi relativi alla data rpg
        definito.
        """
        if check_year not in (True, False):
            log.bug("check_year non è un parametro valido: %s" % check_year)
            return False

        # ---------------------------------------------------------------------

        if (self.minute != -1
        or  self.hour   != -1
        or  self.day    != -1
        or  self.month  != MONTH.NONE
        or (self.year   != -1 and check_year)):
            return True
        else:
            return False
    #- Fine Metodo -

    def reset(self, location, reset_path, log_type=LOG.RESET, avoid_recursion=False):
        """
        Resetta un singolo tipo di entità.
        """
        if not location:
            log.bug("location non è un parametro valido: %r" % location)
            return

        if not reset_path:
            log.bug("reset_path non è un parametro valido per proto_entity %s alla locazione %s: %r" % (
                self.proto_entity.code, location, reset_path))
            return

        if log_type not in (LOG.RESET, LOG.REPOP):
            log.bug("log_type non è un parametro valido: %r" % log_type)
            return

        # ---------------------------------------------------------------------

        # Può capitare quando è stato definito un codice di prototipo
        # inesistente nel database e che quindi non è stato referenziato
        # durante il fread
        if not self.proto_entity:
            log.bug("Impossibile resettare il proto_entity per la locazione superiore %s perché non valido: %r (codice entità da resettare inesistente?)" % (
                location.code, self.proto_entity))
            return

        # Ricava la quantità voluta da resettare in una variabile a parte così
        # da non andare a toccare l'attributo
        reset_counter = self.quantity

        if self.type in (RESET.NONE, RESET.PUT, RESET.BURIED, RESET.GROWING):
            contained_entities = []
            for contained_entity in getattr(location, self.proto_entity.ACCESS_ATTR.replace("proto_", "")):
                if contained_entity.code.startswith("%s#" % self.proto_entity.code):
                    contained_entities.append(contained_entity)

            # Invia il messaggio solo se effettivamente verranno inserite
            # delle nuove entità
            if self.messages and reset_counter > len(contained_entities):
                message = random.choice(self.messages)
                if message[0] == "*":
                    location.act("\n%s" % color_first_upper(message[1 : ]))

            loop_counter = reset_counter
            while loop_counter > 0:
                if contained_entities:
                    content = contained_entities.pop(0)
                    if not self.check_status(content, log_type=log_type):
                        continue
                    # Controlla se aggiungere comunque del contenuto, ma solo se
                    # l'entità è di quantità singola perché altrimenti andremmo
                    # a duplicare il contenuto a tot entità, cosa (attualmente)
                    # non voluta. Ricordo che durante un check di repop non
                    # vengono aggiunte altre entità ma solo controllato lo stato
                    if log_type == LOG.RESET and content.quantity == 1:
                        for sub_reset in self.entity_resets:
                            sub_reset_path = reset_path + " %r=%s" % (self.type.enum_element, self.proto_entity.code)
                            sub_reset.reset(content, sub_reset_path)
                    if content.prototype.code == self.proto_entity.code:
                        loop_counter -= content.quantity
                elif self.proto_entity.max_global_quantity == 0 or self.proto_entity.current_global_quantity < self.proto_entity.max_global_quantity:
                    # I repop eseguono il loro lavoro solo per un'entità per volta:
                    if log_type == LOG.REPOP and self.quantity - reset_counter  >= 1:
                        loop_counter -= 1
                        continue
                    if len(self.wear_mode) > 0 and self.quantity > 1:
                        log.bug("Non è possibile vestire %s per una quantità superiore a 1: %d. (container %s)" % (self.proto_entity.code, self.quantity, container.code))
                        break
                    if log_type == LOG.REPOP or self.probability == 100 or self.probability >= random.randint(1, 100):
                        if log_type == LOG.RESET:
                            sub_reset_path = reset_path + " %r=%s" % (self.type.enum_element, self.proto_entity.code)
                        else:
                            sub_reset_path = reset_path
                        force_break = self._put_or_add_to(location, sub_reset_path, log_type, avoid_recursion)
                        if force_break:
                            break
                    reset_counter -= 1
                loop_counter -= 1

            if not engine.booting and self.quantity - reset_counter > 0:
                if log_type == LOG.REPOP:
                    log.repop("%s: Repop dell'entità %s nel contenitore %s." % (
                        str(calendar), self.proto_entity.code, location.code))
                else:
                    log.reset("%s: RESET.PUT dell'entità %s nel contenitore %s (quantità da inserire: %d, quantità inserite: %d)." % (
                        str(calendar), self.proto_entity.code, location.code, self.quantity, self.quantity - reset_counter))
        elif self.type == RESET.ADD:
            if self.proto_entity.max_global_quantity == 0 or self.proto_entity.current_global_quantity < self.proto_entity.max_global_quantity:
                if self.messages:
                    message = random.choice(self.messages)
                    if message[0] == "*":
                        location.act("\n%s" % color_first_upper(message[1 : ]))

                while reset_counter > 0:
                    if log_type == LOG.REPOP or self.probability == 100 or self.probability >= random.randint(1, 100):
                        if log_type == LOG.RESET:
                            sub_reset_path = reset_path + " %r=%s" % (self.type.enum_element, self.proto_entity.code)
                        else:
                            sub_reset_path = reset_path
                        force_break = self._put_or_add_to(location, sub_reset_path, log_type, avoid_recursion)
                        if force_break:
                            break
                    reset_counter -= 1

            if not engine.booting and self.quantity - reset_counter > 0:
                log.msg("%s: RESET.ADD dell'entità %s nel contenitore %s (quantità aggiunte: %d)." % (
                    str(calendar), self.proto_entity.code, location.code, self.quantity), log_type=log_type)
        elif self.type == RESET.REMOVE:
            entities_to_remove = []
            for contained_entity in getattr(location, self.proto_entity.ACCESS_ATTR.replace("proto_", "")):
                if reset_counter <= 0:
                    break
                if contained_entity.code.startswith("%s#" % self.proto_entity.code):
                    if contained_entity.quantity <= reset_counter:
                        entities_to_remove.append((contained_entity, contained_entity.quantity))
                        reset_counter -= contained_entity.quantity
                    else:
                        entities_to_remove.append((contained_entity, contained_entity.quantity - reset_counter))
                        reset_counter -= contained_entity.quantity - reset_counter

            # Invia il messaggio solo se effettivamente verranno rimosse entità
            if self.messages and entities_to_remove:
                message = random.choice(self.messages)
                if message[0] == "*":
                    location.act("\n%s" % color_first_upper(message[1 : ]))

            for contained_entity, qty in entities_to_remove:
                contained_entity.extract(qty, use_repop=False)

            if not engine.booting:
                log.reset("%s: RESET.REMOVE dell'entità %s dal contenitore %s (quantità da rimuovere: %d, quantità rimosse: %d)." % (
                    str(calendar), self.proto_entity.code, location.code, self.quantity, self.quantity - reset_counter))
        else:
            log.bug("Tipologia di reset errata o non ancora supportata: %r" % self.type)
    #- Fine Funzione -

    def _put_or_add_to(self, location, reset_path, log_type, avoid_recursion):
        if not location:
            log.bug("location non è un parametro valido: %r" % location)
            return False

        if not reset_path:
            log.bug("reset_path non è un parametro valido: %r" % reset_path)
            return False

        if log_type not in (LOG.RESET, LOG.REPOP):
            log.bug("log_type non è un parametro valido: %r" % log_type)
            return

        # ---------------------------------------------------------------------

        factory_class = self.proto_entity.CONSTRUCTOR
        entity = factory_class(self.proto_entity.code)
        if not entity:
            log.bug("entity creata dalla factory_class %r non è valida: %r" % (factory_class, entity))
            return False

        if self.messages:
            message = random.choice(self.messages)
            if message[0] != "*":
                if location.IS_ROOM:
                    location.act("\n%s" % color_first_upper(message))
                else:
                    location.act("\n%s" % color_first_upper(message), TO.OTHERS, entity)

        # Questa riga deve trovarsi prima del RepopLater
        entity.reset_path = reset_path

        if not location.area:
            log.bug("location %s non ha un'area valida per il resetting di %s" % (location.code, entity.code))
            return
        elif location.area.repop_time > 0 and FLAG.NO_REPOP not in self.proto_entity.flags:
            entity.repop_later = RepopLater(self, entity, location)

        # Imposta alcune caratteristiche di stato dell'entità
        entity.wear_mode = self.wear_mode.copy()
        if self.type == RESET.BURIED:
            entity.flags += FLAG.BURIED
        if self.type == RESET.GROWING:
            entity.flags += FLAG.GROWING
            if entity.entitype == ENTITYPE.SEED:
                entity.flags += FLAG.BURIED
            if entity.plant_type:
                entity.plant_type.start_growth(entity, "plant_type")
            if target.seed_type:
                target.seed_type.start_growth(entity, "seed_type")

        # Inietta l'entità in gioco
        entity.inject(location, avoid_recursion=avoid_recursion)

        # Se l'entità appena resettata è un mob allora vi inserisce, flag
        # permettendo, delle monete da rubare o saccheggiare
        if entity.IS_MOB and entity.value > 0 and FLAG.VALUE_IS_ONLY_COST not in entity.flags:
            map(lambda money: money.inject(entity), random_moneys(entity.value, race=entity.race))

        # Resetta ricorsivamente i reset contenuti da questa entità
        for sub_reset in self.entity_resets:
            sub_reset_path = reset_path + " %r=%s" % (self.type.enum_element, self.proto_entity.code)
            sub_reset.reset(entity, sub_reset_path)

        # Ecco che finalmente possiamo raggruppare l'entità senza danni
        entity.location.group_entities()

        # Invia il comando solo dopo che le entità che contiene questa sono
        # state inserite così tutto funziona nel qual caso interagisse con esse
        if self.inputs:
            input = random.choice(self.inputs)
            send_input(entity, input)

        if log_type == LOG.RESET:
            return check_trigger(entity, "on_reset", entity)
        else:
            return check_trigger(entity, "on_repop", entity)
    #- Fine Metodo -

    def check_status(self, entity, log_type=LOG.RESET):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return False

        # -------------------------------------------------------------------------

        changed = False

        if FLAG.NO_CHECK_STATUS in entity.flags:
            return True

        if len(self.wear_mode) > 0:
            if entity.location.IS_ROOM:
                log.bug("Le stanze (%s) non possono essere vestite di %s: %r" % (entity.location.code, entity.code, self.wear_mode))
                return False
            elif self.quantity > 1:
                log.bug("Non è possibile vestire %s per una quantità superiore a 1: %d. (A)" % (self.proto_entity.code, self.quantity))
                return False
            else:
                if entity.wear_mode != self.wear_mode:
                    entity.wear_mode = self.wear_mode.copy()
                    changed = True
        else:
            if len(entity.wear_mode) > 0:
                entity.wear_mode = self.wear_mode.copy()
                changed = True

        if entity.door_type and entity.door_type.flags != self.proto_entity.door_type.flags:
            entity.door_type.flags = self.proto_entity.door_type.flags.copy()
            changed = True
        if entity.container_type and entity.container_type.flags != self.proto_entity.container_type.flags:
            entity.container_type.flags = self.proto_entity.container_type.flags.copy()
            changed = True

        if changed:
            log.msg("È stato cambiato lo stato dell'entità %s in %s" % (entity.code, entity.location.code), log_type=log_type)

        return True
    #- Fine Funzione -


class ExitReset(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"exit"        : ("src.exit", "Exit"),
                   "destination" : ("src.room", "Destination")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, direction=DIR.NONE):
        self.comment     = ""        # Commento relativo al reset dell'uscita
        self.destination = None      # Coordinate spaziali relative alla room in cui bisogna manipolare l'uscita
        self.minute      = -1
        self.hour        = -1
        self.day         = -1
        self.month       = Element(MONTH.NONE)
        self.year        = -1
        self.direction   = direction # Direzione in cui manipola l'uscita
        self.exit        = None      # Exit da aggiungere, sostituire o, se rimane a None, eliminare
        self.door        = None      # Door da aggiungere, sostituire o, se rimane a None, eliminare (TD) pensare se togliere il sistema attuale delle door resettate assieme alla room
        #self.exit_flags  = None
        #self.door_flags = None
    #- Fine Inizializzazione -

    def get_error_message(self):
        if self.direction.get_error_message(DIR, "direction") != "":
            msg = self.direction.get_error_message(DIR, "direction")
        elif self.minute < -1 or self.minute > config.minutes_in_hour - 1:
            msg = "minute non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.minute, config.minutes_in_hour - 1)
        elif self.hour < -1 or self.hour > config.hours_in_day - 1:
            msg = "hour non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.hour, config.hours_in_day - 1)
        elif self.day < -1 or self.day > config.days_in_month or self.day == 0:
            msg = "day non è un valore valido: %s (dev'essere tra -1 e %s)" % (self.day, config.days_in_month)
        elif self.month.get_error_message(MONTH, "month") != "":
            msg = self.month.get_error_message(MONTH, "month")
        elif self.year < -1:
            msg = "year non è un valore valido: %d (dev'essere maggiore di -1)" % self.year
        else:
            return ""

        return "(exit_reset) %s" % msg
        return msg
    #- Fine Metodo -


class WallReset(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"wall"        : ("src.exit", "Wall"),
                   "destination" : ("src.room", "Destination")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, direction=DIR.NONE):
        self.comment     = ""        # Commento relativo al reset dell'uscita
        self.destination = None      # Coordinate spaziali relative alla room in cui bisogna manipolare il muro
        self.direction   = direction # Direzione in cui manipola l'uscita
        self.wall        = None      # Wall da aggiungere, sostituire o, se rimane a None, eliminare
    #- Fine Inizializzazione -

    def get_error_message(self):
        if self.direction.get_error_message(DIR, "direction") != "":
            return self.direction.get_error_message(DIR, "direction")
        elif self.minute < -1 or self.minute > config.minutes_in_hour - 1:
            return "minute non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.minute, config.minutes_in_hour - 1)
        elif self.hour < -1 or self.hour > config.hours_in_day - 1:
            return "hour non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.hour, config.hours_in_day - 1)
        elif self.day < -1 or self.day > config.days_in_month or self.day == 0:
            return "day non è un valore valido: %s (dev'essere tra -1 e %s)" % (self.day, config.days_in_month)
        elif self.month.get_error_message(MONTH, "month") != "":
            return self.month.get_error_message(MONTH, "month")
        elif self.year < -1:
            msg = "year non è un valore valido: %d (dev'essere maggiore di -1)" % self.year
        else:
            return ""

        return "(wall_reset) %s" % msg
    #- Fine Metodo -


class HasResetLocationSuperclass(object):
    # (BB) non riesce a trovare la chiave in opekus, eppure è lì:
    #	EntityResets:
    #		Quantity:	1
    #		Type:		RESET.PUT
    #		ProtoEntity:	opekus_item_asse-giaciglio
    #		EntityResets:
    #			Quantity:	1
    #			Type:		RESET.PUT
    #			ProtoEntity:	opekus_item_paglia-container
    #			EntityResets:
    #				Quantity:	1
    #				Type:		RESET.PUT
    #				ProtoEntity:	opekus_item_chiave-sacello
    #			End
    #		End
    #	End
    # (TD) Questo è un punto delicato che meriterebbe discussione:
    # Una room reset (campi coltivati) possiede un entity reset (contadino),
    # dopo tot di tempo al posto dei campi coltivati viene inserita una room
    # differente (campi innevati) che non possiede l'entity reset del contadino.
    # Tuttavia il contadino continuerà a repoppare nonostante la stanza non sia
    # quella originale perché il check si basa sulle coordinate. È un difetto
    # o un pregio? Dipende... forse dovrei inserire una flag a riguardo ma
    # vorrei prima far andare il sistema per un po'
    def has_reset_on_location(self, area=None, entity_with_location=None):
        """
        Ritorna vero se l'entità si trova ancora nella locazione originaria di
        reset.
        """
        if self.IS_PLAYER:
            log.bug("In questo metodo l'entità non può essere un giocatore: %s" % self.code)
            return False

        if not area:
            area = self.area

        if not entity_with_location:
            entity_with_location = self

        # Avvisa dell'errore dell'area non valida ed esce, il problema deve
        # essere necessariamente risolto a priori
        if not area:
            if self.location:
                area = self.location.area
            elif self.previous_location and self.previous_location():
                area = self.previous_location().area
            extract_descr  = "EXTRACTED " if FLAG.EXTRACTED in self.flags else "NOT EXTRACTED "
            extract_descr += " WEAKLY_EXTRACTED" if FLAG.WEAKLY_EXTRACTED in self.flags else " NOT WEAKLY_EXTRACTED"
            if self == entity_with_location:
                log.bug("area non valida per %s che si trova in %r: %r (%s)." % (
                    self.code, self.location, area, extract_descr))
            else:
                log.bug("area non valida per %s che si trova in %r e per entity_with_location=%s: %r (%s)." % (
                    self.code, self.location, entity_with_location.code, area, extract_descr))
            return

        # Ricava a ritroso la lista delle entità che contengono self, quindi
        # l'ultima ad essere ricavata è la stanza, che poi diventa la prima
        #della lista
        location_list = []
        target = entity_with_location
        while True:
            if not target.location:
                break
            location_list.append(target.location)
            if target.location.IS_ROOM:
                break
            target = target.location
        location_list = list(reversed(location_list))

        # Controlla che tutte le locazioni in cui l'entità self si trova siano
        # quelle del reset originale; la prima ad essere controllata è la
        # stanza, quindi in linea di massima la variabile location_reset viene
        # inizializzata nella prima parte del ciclo
        location_reset = None
        for location in location_list:
            #print location.code
            if location.IS_ROOM:
                #print "IS_ROOM", location.x, location.y, location.z
                for room_reset in area.room_resets:
                    #print room_reset.destination.x, room_reset.destination.y, room_reset.destination.z
                    location_reset = room_reset
                    # (Non esegue il check sul codice della stanza della proto_room
                    # del room_reset perché viene ritenuto lecito che entità resettate
                    # tramite room reset differenti si possano poi trovare in stanze
                    # con codice differente e resettate successivamente)
                    if (location.x == room_reset.destination.x
                    and location.y == room_reset.destination.y
                    and location.z == room_reset.destination.z):
                        if FLAG.REPOP_ON_COORDS_AND_CODE in self.flags:
                            if room_reset.proto_room.code != location.prototype.code:
                                continue
                        if location == location_list[-1]:
                            #print "True"
                            return True
                        else:
                            #print "trovato"
                            break
                else:
                    #print "non trovato"
                    break
            elif not location.IS_PLAYER:
                #print "not IS_ROOM"
                if location_reset:
                    #print "location_reset"
                    for entity_reset in location_reset.entity_resets:
                        location_reset = entity_reset
                        if entity_reset.type == RESET.REMOVE:
                            continue
                        #print "entity_reset.proto_entity:", entity_reset.proto_entity.code
                        if entity_reset.proto_entity.code == location.prototype.code:
                            if location == location_list[-1]:
                                #print "True"
                                return True
                            else:
                                #print "trovato"
                                break
                    else:
                        #print "non trovato"
                        break

        #print "False"
        return False
    #- Fine Metodo -


class DoorResetSuperclass(object):
    def reset_doors(self, area, old_exits=None):
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return

        # ---------------------------------------------------------------------

        # (TD) Sì ok, fa schifo, ma il sistema sarà così fino a che non mi
        # deciderò ad inserire dei metodi reset dentro tutti gli oggetti
        # caricabili
        old_exits2 = {}
        if old_exits:
            for direction in old_exits:
                old_exits2[direction] = old_exits[direction].copy()
        else:
            old_exits = {}

        # Dopo la copia di tutti gli attributi da una room di prototipi i valori
        # di exit.door validi non sono più dei riferimenti a delle porte ma
        # delle stringhe identificative del codice dell'entità prototipo da
        # utilizzare come porta. Per questo serve quindi recuperare la vecchia
        # porta, se esistente, e copiare gli attributi dell'entità prototipo
        # dell'entità porta da resettare
        for direction, exit in self.exits.iteritems():
            # All'inizio l'exit.door se non ancora resettata contiene la stringa
            # con il codice del prototipo da utilizzare per il reset
            if not exit.door:
                continue
            door_proto_code = exit.door
            try:
                type = door_proto_code.split("_")[1]
            except AttributeError:
                # (bb) è un baco spammoso che non dovrebbe capitare... eppure... bho!
                #log.bug("door_proto_code non è un codice ma un'entità: %s" % door_proto_code.code)
                continue
            if door_proto_code not in database["proto_%ss" % type]:
                log.bug("exit.door non è un codice proto_items o proto_mobs: %s alla stanza %s" % (exit.door, self.code))
                continue
            if (old_exits and direction in old_exits and old_exits[direction].door
            and old_exits[direction].door.prototype.code == door_proto_code):
                exit.door = old_exits[direction].door
                copy_existing_attributes(database["proto_%ss" % type][door_proto_code], exit.door, except_these_attrs=["code"])
                exit.door.reinit_code(old_exits[direction].door.prototype.code)
                exit.door.location = self
                # (BB) il sistema è bacato, bisogna creare degli entity_reset appositi
                if exit.door.repop_later:
                    exit.door.repop_later.location = self
            else:
                # Se vi era precedentemente una porta allora la rimuove
                # (la rimuove in quantità di 1 perché per definizione una porta
                # sugli stipiti può rimanere solo in quantità di 1)
                if old_exits and direction in old_exits and old_exits[direction].door:
                    old_exits[direction].door.extract(1, use_repop=False)
                if exit.door and hasattr(exit.door, "extract"):
                    exit.door.extract(1, use_repop=False)
                door_proto = database.get_proto_entity(door_proto_code)
                exit.door = door_proto.CONSTRUCTOR(door_proto_code)
                exit.door.inject(self)
                # (BB) il sistema è bacato, bisogna creare degli entity_reset appositi
                if self.area.repop_time > 0 and FLAG.NO_REPOP not in exit.door.prototype.flags:
                    # (TD) per ora è così, senza l'entity_reset passato, in
                    # futuro sarebbe utopicamente meglio che esistessero
                    # solo le ExitReset al posto del metodo reset_doors
                    exit.door.repop_later = RepopLater(None, exit.door, self)

            # Gestisce i messaggi di reset delle porte
            if not old_exits2 or direction not in old_exits2:
                continue
            old_exit = old_exits2[direction]
            if not old_exit.door or not old_exit.door.door_type:
                continue
            if DOOR.CLOSED in old_exit.door.door_type.flags and DOOR.CLOSED not in exit.door.door_type.flags:
                self._reverse_open_or_close(exit, direction, "open", "Una folata d'aria $a $n a %s.", "[sandybrown]apre[close]")
            elif DOOR.CLOSED not in old_exit.door.door_type.flags and DOOR.CLOSED in exit.door.door_type.flags:
                self._reverse_open_or_close(exit, direction, "close", "Una folata d'aria $a $n a %s.", "[saddlebrown]chiude[close]")
    #- Fine Metodo -

    def _reverse_open_or_close(self, exit, direction, message_attr, default_message, verb):
        reset_message = getattr(exit.door.door_type, "reset_%s_message" % message_attr)
        if not reset_message:
            reset_message = default_message % direction

        exit.door.act(reset_message, TO.OTHERS, exit.door, verb, direction, send_to_location=self)

        # Recupera la porta che c'è dall'altro lato
        reverse_door = self.get_door(direction, direct_search=False)
        if not reverse_door or not reverse_door.door_type:
            return

        # In teoria destination_room dovrebbe essere sempre valida
        destination_room = self.get_destination_room(direction)
        if not destination_room:
            return

        # Se le porte sono asincrone dall'altro lato fa visualizzare il
        # messaggio di apertura della porta in questo lato, sempre che
        # dall'altro lato si possa vedere la porta che si apre
        if DOOR.ASYNCHRONOUS in exit.door.door_type.flags:
            if DOOR.CLOSED not in reverse_door.door_type.flags:
                exit.door.act(reset_message, TO.OTHERS, exit.door, verb, direction.reverse_dir, send_to_location=destination_room)
        # Se le porte sono sincronizzate allora apre anche l'altro lato
        # facendo visualizzare anche il messaggio apposito
        else:
            if DOOR.CLOSED in exit.door.door_type.flags:
                reverse_door.door_type.flags += DOOR.CLOSED
            else:
                reverse_door.door_type.flags -= DOOR.CLOSED
            reverse_door.act(reset_message, TO.OTHERS, reverse_door, verb, direction.reverse_dir, send_to_location=destination_room)

        if DOOR.CLOSED in exit.door.door_type.flags:
            was_status = "chiusa"
        else:
            was_status = "aperta"
        log.msg("%s: reset della porta %s, ora è %s" % (
            str(calendar), exit.door.code, was_status), log_type=LOG.RESET)
    #- Fine Metodo -


#-------------------------------------------------------------------------------

class RepopLater(object):
    """
    Serve a gestiore un repop di un'entità eseguito dopo un certo tot di tempo.
    Inoltre serve anche a far ritornare una determinata caratteristica al suo
    stato originario, le caratteristiche controllate sono:
    open/close
    lock/unlock
    bolt/unbolt
    wear/unwear
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {"entity"    : ["items", "mobs"],
                   "location" : ["rooms", "items", "mobs"]}

    def __init__(self, entity_reset, entity, location):
        self.entity_reset = entity_reset          # Entità reset da utilizzare per il repop
        self.entity       = weakref.ref(entity)   # Entità di cui controllarne lo stato
        self.location     = weakref.ref(location) # Locazione in cui repopparla
        self.reset_path   = entity.reset_path     # Path di reset, viene salvato a parte perché a volte entity viene estratto e non è più possibile ricavarne informazioni
        # (TD) (bb) per ora tengo il check sulle door
        if not self.reset_path and not entity.door_type:
            log.bug("Inizializzazione di reset_path non valida in un repop later di %s in %s" % (entity.code, location))
    #- Fine Inizializzazione -

    def __str__(self):
        r = "<%r" % self.entity_reset

        if self.entity():
            r += " %s" % self.entity().code
        else:
            r += " %r" % self.entity()

        if self.location():
            r += " %s>" % self.location().code
        else:
            r += " %r>" % self.location()

        return r
    #- Fine Metodo -

    def equals(self, repop_later2):
        if not repop_later2:
            return False

        if self.entity_reset != repop_later2.entity_reset:
            return False

        if not self.entity() or not repop_later2.entity():
            return False
        if not self.location() or not repop_later2.location():
            return False

        if self.entity().prototype.code != repop_later2.entity().prototype.code:
            return False
        if self.location().code != repop_later2.location().code:
            return False
        if self.reset_path != repop_later2.reset_path:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def is_valid(self):
        if self.entity and self.entity() and self.location and self.location():
            return True
        else:
            return False
    #- Fine Metodo -

    def get_repop_time(self):
        """
        Questo metodo esegue il calcolo del repop a seconda dell'area in cui
        si trova location, ciò significa che se quest'ultimo è stato spostato
        dall'area originale allora anche il suo tempo di repop varia,
        è una cosa voluta (tutto questo discorso vale solo per le entità).
        """
        # Ritornando 0 si indica che non bisogna repoppare
        if not self.is_valid():
            return 0

        location = self.location()
        minutes = random.randint(int(location.area.repop_time - location.area.repop_time/10),
                                 int(location.area.repop_time + location.area.repop_time/10))
        if minutes <= 0:
            minutes = 1
        return minutes * 60
    #- Fine Metodo -

    def defer_repop(self):
        location = self.location()
        entity = self.entity()

        if not self.entity_reset:
            # (TD) (BB)
            if not entity or not entity.door_type:
                log.bug("entity_reset non è valido per %s e %s: %r" % (
                    entity.code if entity else "?", location.code if location else "?", self.entity_reset))
            return

        repop_time = self.get_repop_time()
        if repop_time > 0:
            #print "defer repop...", repop_time, entity.code if entity else "?", location.code if location else "?"
            return defer(repop_time, self.repop)
    #- Fine Metodo -

    def repop(self):
        location = self.location()
        entity = self.entity()

        if not self.entity_reset:
            # (TD) (BB)
            if not entity or not entity.door_type:
                log.bug("entity_reset non è valido per %s e %s: %r" % (
                    entity.code if entity else "?", location.code if location else "?", self.entity_reset))
            return

        #print "repop!", entity.code if entity else "?", location.code if location else "?"
        self.entity_reset.reset(location, self.reset_path, log_type=LOG.REPOP)
    #- Fine Metodo -

    def defer_check_status(self):
        location = self.location()
        entity = self.entity()

        repop_time = self.get_repop_time()
        if repop_time > 0:
            #print "defer check status...", entity.code if entity else "?", location.code if location else "?"
            return defer(repop_time, self.check_status)
    #- Fine Metodo -

    def check_status(self):
        """
        I check status vengono eseguiti dopo aver digitato alcuni comandi
        (per esempio open e close); se tuttavia il repop_later dell'entità non
        viene trovato valido il check di stato non viene eseguito poiché
        significa che è già stato attivato un repop sull'entità e quindi ogni
        qualsiasi ulteriore controllo, in un tempo minore di quello di repop,
        viene visto come inutile.
        """
        entity = self.entity()
        location = self.location()

        if not entity or not location:
            return

        if not entity.has_reset_on_location():
            return

        #print "check status!", entity.code if entity else "?", location.code if location else "?"
        if self.entity_reset:
            self.entity_reset.check_status(entity, log_type=LOG.REPOP)
        else:
            check_status(entity, log_type=LOG.REPOP)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def finalize_room_resets():
    for area in database["areas"].itervalues():
        for room_reset in area.room_resets:
            room_reset.finalize()
#- Fine Funzione -


def get_error_message_entity_resets(reset):
    """
    Questa funzione controlla anche che non vi siano reset di entità uguali
    nella stessa locazione, ciò serve ad evitare problemi poi con i repop che
    non capirebbero di dover inserire una entità in gioco (relativa ad un entity
    reset) perché la trovano già inserita (che però sarebbe relativa all'altro
    entity reset).
    Esempio: mettiamo caso di resettare nella stessa locazione con un entity
    reset due spade, e con un altro entity reset altre due spade, in gioco
    vi saranno 4 spade (in realtà c'è un baco in aarit, sempre relativo a
    questo problema ma che sarebbe risolvibile, e in gioco vi sarebbero 2 di
    spade, ma facciamo finta di nulla), a questo un giocatore passa e raccoglie
    una spada, scatta il timer per il repop della nuova spada, una volta che
    il timer finisce viene controllato il numero di spade nella locazione, ne
    sono rimaste 3, controlla il numero di quante deve eventualmente al massimo
    repopparne e poiché il repop si rifà al numero di quantity resettata
    precedentemente questo numero vale 2, quindi non repopperà nulla poiché
    2 < 3.
    Tale esempio è molto semplice ed è per far capire il nocciolo del problema,
    il caso specifico sarebbe facilmente correggibile accorpando dinamicamente
    tali entity reset in un unico solo, il problema c'è quando differenti
    entity reset con stessa entità prototipo resettano contenuti differenti...
    E lì sarebbe un ginepraio da correggere lato repop, considerando poi che
    i repop volutamente non controllano il contenuto (che può essere stato
    manipolato dal giocatore) il problema è di difficile risoluzione, quindi
    la morale della favola qual'è?
    Che anche Aarit ha i suoi limiti! E il messaggio di errore qui sotto, se lo
    otterrete, ne è un esempio :D
    """
    if not reset:
        log.bug("reset non è un parametro valido: %r" % reset)
        return ""

    # -------------------------------------------------------------------------

    prototypes = []
    for entity_reset in reset.entity_resets:
        if entity_reset.proto_entity in prototypes:
            return "Reset già impostato per l'entità %r nella stessa locazione, ve ne deve essere per forza uno solo, la soluzione di solito è creare una nuova entità per evitare la doppiezza." % entity_reset.proto_entity
        else:
            prototypes.append(entity_reset.proto_entity)

        if entity_reset.get_error_message() != "":
            return entity_reset.get_error_message()

    return ""
#- Fine Funzione -


def start_repop_laters():
    """
    Avvia le deferred relative ai repop.
    """
    # Ricerca prima eventuali reset path erronei (relativi magari a bachi sui
    # dati di persistenze remote portate di release in release) e cerca di
    # correggerli; la correzione comunque è relativa, viene cercato il primo
    # reset utile allo scopo e gli viene appioppata la reset path relativa:
    # è una pezza insomma...
    for table_name in ("items", "mobs"):
        for entity in database[table_name].itervalues():
            if FLAG.NO_REPOP in entity.flags:
                continue
            if entity.reset_path:
                values = entity.reset_path.split()
                if len(values) < 4 or not is_number(values[0]) or not is_number(values[1]) or not is_number(values[2]) or values[3] not in database["proto_rooms"]:
                    for area in database["areas"].itervalues():
                        for room_reset in area.room_resets:
                            reset_path = try_to_correct_reset_path(entity, room_reset.entity_resets)
                            if reset_path:
                                break
                        if reset_path:
                            break
                    message = "Si sta cercando di correggere la reset_path non valida per l'entità %s: %s" % (entity.code, entity.reset_path)
                    if reset_path:
                        x, y, z = room_reset.destination.x, room_reset.destination.y, room_reset.destination.z
                        entity.reset_path = "%d %d %d %s%s" % (x, y, z, room_reset.proto_room.code, reset_path)
                        log.bug(message + " ... OK! (%s)" % entity.reset_path)
                    else:
                        log.bug(message + " ... Fallito!")
            else:
                # (TT) Da valutare se anche qui non si necessita di un check di qualche tipo
                pass

    # Ora viene eseguito lo start dei repop later vero e proprio
    for table_name in ("items", "mobs"):
        for entity in database[table_name].itervalues():
            if FLAG.NO_REPOP in entity.flags:
                continue

            if entity.reset_path:
                values = entity.reset_path.split()
                if len(values) >= 4 and is_number(values[0]) and is_number(values[1]) and is_number(values[2]) and values[3] in database["proto_rooms"]:
                    x = int(values[0])
                    y = int(values[1])
                    z = int(values[2])
                    proto_room_code = values[3]
                    for area in database["areas"].itervalues():
                        index = 4
                        for room_reset in area.room_resets:
                            if room_reset.proto_room.code != proto_room_code:
                                continue
                            if room_reset.destination.x != x:
                                continue
                            if room_reset.destination.y != y:
                                continue
                            if room_reset.destination.z != z:
                                continue
                            search_entity_reset(entity, x, y, z, proto_room_code, room_reset.entity_resets, area, values, 4)
                else:
                    log.bug("reset_path non valida per l'entità %s: %s" % (entity.code, entity.reset_path))
            else:
                # Imposta solo le porte sui cardini, che sono un caso particolare
                if not entity.door_type:
                    continue
                if not entity.is_hinged():
                    continue
                entity.repop_later = RepopLater(None, entity, entity.location)
                entity.repop_later.defer_check_status()
#- Fine Metodo -


def try_to_correct_reset_path(entity, entity_resets, reset_path=""):
    if not entity:
        lof.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    for entity_reset in entity_resets:
        if entity_reset.proto_entity == entity.prototype:
            reset_path_piece = " %r=%s" % (entity_reset.type.enum_element, entity_reset.proto_entity.code)
            return reset_path + reset_path_piece

    for entity_reset in entity_resets:
        if entity_reset.entity_resets:
            reset_path_piece = " %r=%s" % (entity_reset.type.enum_element, entity_reset.proto_entity.code)
            reset_path = try_to_correct_reset_path(entity, entity_reset.entity_resets, reset_path + reset_path_piece)
            if reset_path:
                return reset_path

    return ""
#- Fine Metodo -


def defer_all_reset_events():
    """
    Prepara l'esecuzione a catena di tutti i reset.
    """
    for area in database["areas"].itervalues():
        area.defer_reset_events()
#- Fine Funzione -


def check_room_reset_events():
    # Controlla proprio a metà strada tra l'attivazione dei reset precedente
    # e quella successiva
    seconds = config.seconds_in_minute / 2.0

    for area in database["areas"].itervalues():
        for room_reset in area.room_resets:
            if room_reset.reset_event or not room_reset.has_defined_date(check_year=False):
                continue
            d = defer(seconds, room_reset.check_event)
            d.addErrback(room_reset.log_error)
#- Fine Funzione -


def stop_all_reset_events():
    for area in database["areas"].itervalues():
        area.stop_reset_events()
#- Fine Funzione -


# (TD) funzione che esiste come pezza alla reset_doors che non può di base
# passare la entit_resets relativa alle door (perché non esiste) quindi al
# posto del metodo check_status viene eseguita questa funzione
# (TD) cambiarli tramite comandi o messaggi per un maggiore realismo
def check_status(entity, log_type):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    if FLAG.NO_CHECK_STATUS in entity.flags:
        return

    changed = False
    # (bb) manca il check sul wear

    if entity.door_type and entity.door_type.flags != entity.prototype.door_type.flags:
        entity.door_type.flags = entity.prototype.door_type.flags.copy()
        changed = True
    if entity.container_type and entity.container_type.flags != entity.prototype.container_type.flags:
        entity.container_type.flags = entity.prototype.container_type.flags.copy()
        changed = True

    if changed:
        log.msg("È stato cambiato lo stato dell'entità %s in %s" % (entity.code, entity.location.code), log_type=log_type)
#- Fine Funzione -


def search_entity_reset(entity, x, y, z, proto_room_code, entity_resets, area, values, index):
    for entity_reset in entity_resets:
        if len(values) <= 4:
            log.bug("La reset_path %s non è formata da più di 4 valori (deve esservi almeno un valore in più che identifica l'entity_reset): %d (per l'entità %s %s %s)" % (
                entity.reset_path, len(values), entity.code, FLAG.EXTRACTED in entity.flags, FLAG.WEAKLY_EXTRACTED in entity.flags))
            continue

        if "=" not in values[index]:
            log.bug("Il carattere = non si trova nel valore identificativo un'entity reset: %s" % values[index])
            continue
        type, entity_code = values[index].split("=")

        if repr(entity_reset.type.enum_element) != type:
            continue
        if entity_reset.proto_entity.code != entity_code:
            continue

        index += 1
        if index >= len(values):
            coords = "%d %d %d" % (x, y, z)
            if coords not in area.rooms:
                log.bug("Impossibile trovare le coordinate %s nell'area %s" % (coords, area.code))
                continue
            room = area.rooms[coords]
            if room.prototype.code == proto_room_code or FLAG.REPOP_ON_COORDS_AND_CODE not in entity.flags:
                entity.repop_later = RepopLater(entity_reset, entity, room)
                if FLAG.REPOP_ONLY_ON_EXTRACT not in entity.flags:
                    if entity.has_reset_on_location():
                        entity.repop_later.defer_check_status()
                        #log.repop("Riavviato il check status per %s in %s" % (entity.code, room.code))
                    else:
                        entity.repop_later.defer_repop()
                        #log.repop("Riavviato il repop per %s in %s" % (entity.code, room.code))
            else:
                # Con l'attuale sistema non è possibile ricavare con
                # certezza da quale locazione è stata resettata l'entità,
                # poiché tale locazione potrebbe non essere più nel
                # gioco, in tali casi il ciclo di repop potrebbe essere
                # "rotto" e non funzionare più a meno di un altro reset
                # dell'entità nella locazione originaria
                pass
            return

        search_entity_reset(entity, x, y, z, proto_room_code, entity_reset.entity_resets, area, values, index)
#- Fine Funzione -


def stop_all_repops():
    for table_name in ("items", "mobs"):
        for data in database[table_name].itervalues():
            if data.deferred_repop:
                data.deferred_repop.pause()
                data.deferred_repop = None
#- Fine Funzione -
