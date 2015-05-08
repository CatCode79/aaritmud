# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle aree e dei relativi resets.
"""


#= IMPORT ======================================================================

import random

from src.calendar    import calendar
from src.climate     import Meteo
from src.config      import config
from src.data        import Data
from src.database    import database
from src.element     import Element, Flags
from src.enums       import AREA, COLOR, DIR, RACE
from src.exit        import Exit
from src.item        import create_random_item
from src.log         import log
from src.mob         import create_random_mob
from src.reset       import AreaResetsSuperclass
from src.utility     import is_same, is_prefix


#= CLASSI ======================================================================

class Area(Data, AreaResetsSuperclass):
    """
    Contiene tutte le informazioni di un'area e i metodi per gestirla.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ["max_players", "upper_limit", "lower_limit",
                   "rooms", "players", "mobs", "items",
                   "room_scripts", "mob_scripts", "item_scripts", "player_scripts",
                   "meteo", "proto_rooms", "proto_mobs", "proto_items"]
    MULTILINES  = ["descr"]
    SCHEMA      = {"climates"                  : ("src.climate",      "Climate"),
                   "maze"                      : ("src.games.maze",   "Maze"),
                   "wumpus"                    : ("src.games.wumpus", "Wumpus"),
                   "wild"                      : ("src.wild",         "Wild"),
                   "room_resets"               : ("src.reset",        "RoomReset"),
                   "echoes_dawn"               : ("", "str"),
                   "echoes_dawn_no_sun"        : ("", "str"),
                   "echoes_sunrise"            : ("", "str"),
                   "echoes_sunrise_no_sun"     : ("", "str"),
                   "echoes_noon"               : ("", "str"),
                   "echoes_noon_no_sun"        : ("", "str"),
                   "echoes_sunset"             : ("", "str"),
                   "echoes_sunset_no_sun"      : ("", "str"),
                   "echoes_dusk"               : ("", "str"),
                   "echoes_dusk_no_moon"       : ("", "str"),
                   "echoes_dusk_full_moon"     : ("", "str"),
                   "echoes_midnight"           : ("", "str"),
                   "echoes_midnight_no_moon"   : ("", "str"),
                   "echoes_midnight_full_moon" : ("", "str")}

    REFERENCES  = {}
    WEAKREFS    = {}

    IS_AREA   = True
    IS_DESCR  = False
    IS_ROOM   = False
    IS_EXIT   = False
    IS_WALL   = False
    IS_ACTOR  = False
    IS_MOB    = False
    IS_ITEM   = False
    IS_PLAYER = False
    IS_EXTRA  = False
    IS_PROTO  = False

    def __init__(self, code=""):
        self.comment        = ""
        self.code           = code # Codice identificativo dell'area
        self.name           = ""   # Nome esteso
        self.short          = ""   # Descrizioni breve dell'area
        self.short_night    = ""   # Descrizioni breve notturna dell'area
        self.descr          = ""   # Descrizione dell'area per la pagina web della lista delle aree
        self.creators       = ""   # Lista dei creatori, vale il codice dell'account  (TD) in futuro sarà una lista per poter ricavare il riferimento
        self.level          = 1    # Livello base per tutte le entità dell'area, se viene modificato questo anche tutte le entità aumentano o diminuiscono di livello in proporzione
        self.flags          = Flags(AREA.NONE)
#       self.races          = Flags(RACE.NONE)  # Razze che si possono incontrare principalmente nell'area  (TD)
        self.color          = Element(COLOR.NONE)  # Colore dell'area
        self.music          = ""   # File mid avviato quando uno entra nell'area
        self.music_wild     = ""   # File mid avviato quando uno esce dall'area ed entra nella wild
        self.climates       = {}   # Informazioni climatiche dell'area relativamente alle stagioni
        self.maze           = None # Informazioni relative al labirinto
        self.wumpus         = None # Informazioni relative alle aree wumpus
        self.wild           = None # Struttura relativa alla wilderness
        self.landfill_code  = ""   # Codice della stanza prototipo in cui verranno inseriti gli oggetti "da buttare"
        self.repop_time     = 0    # Minuti reali tra un repop di un'entità ed un'altro
        self.room_resets    = []   # Lista dei reset dell'area

        # Attributi relativi alle liste dei messaggi di echo
        self.echoes_dawn               = []
        self.echoes_dawn_no_sun        = []
        self.echoes_sunrise            = []
        self.echoes_sunrise_no_sun     = []
        self.echoes_noon               = []
        self.echoes_noon_no_sun        = []
        self.echoes_sunset             = []
        self.echoes_sunset_no_sun      = []
        self.echoes_dusk               = []
        self.echoes_dusk_no_moon       = []
        self.echoes_dusk_full_moon     = []
        self.echoes_midnight           = []
        self.echoes_midnight_no_moon   = []
        self.echoes_midnight_full_moon = []

        # Attributi volatili:
        self.max_players    = 0  # Numero massimo di giocatori che sono stati presenti contemporaneamente nell'area nella sessione di gioco
        self.upper_limit    = 0  # Limite di coordinata Z verso l'alto oltre la quale si esce dall'area
        self.lower_limit    = 0  # Limite di coordinata Z verso il basso oltre la quale si esce dall'area
        self.rooms          = {} # Stanze in-game nelle rispettive coordinate
        self.players        = [] # Giocatori in-game che si trovano nelll'area
        self.mobs           = [] # Mob in-game che si trovano nell'area
        self.items          = [] # Oggetti in-game che si trovano nell'area
        self.meteo          = Meteo()  # Informazioni meteo in-game dell'area
        self.gamescripts    = {}   # Gamescript a livello di area

        # Liste relative ai dati modello dell'area, i prototipi
        self.proto_rooms    = {}
        self.proto_mobs     = {}
        self.proto_items    = {}
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s" % (super(Area, self).__repr__, self.code)
    #- Fine Metodo -

    def get_error_message(self):
        """
        Ritorna un messaggio di errore se la struttura dell'area contiene delle
        anomalie, altrimenti se tutto è corretto ritorna una stringa vuota.
        """
        if not self.code:
            msg = "code dell'area non valido"
        elif not self.code.islower():
            msg = "code dell'area per convenzione deve essere scritto in minuscolo: %s" % self.code
        elif not self.short:
            msg = "short dell'area non valido: %r" % self.short
        elif not self.name:
            msg = "name dell'area non valido: %r" % self.name
        elif not self.descr:
            msg = "descr dell'area non valida: %r" % self.descr
        elif self.get_error_message_creators() != "":
           msg = self.get_error_message_creators()
        elif self.level <= 0:
            msg = "Il livello di un'area non può essere uguale a 0 o negativo: %d" % self.level
#       elif self.races.get_error_message(RACE, "races") != "":
#           msg = self.races.get_error_message(RACE, "races")
        elif self.flags.get_error_message(AREA, "flags") != "":
            msg = self.flags.get_error_message(AREA, "flags")
        elif self.color.get_error_message(COLOR, "color") != "":
            msg = self.color.get_error_message(COLOR, "color")
        elif self.get_error_message_climates() != "":
            msg = self.get_error_message_climates()
        elif self.maze and self.maze.get_error_message() != "":
            msg = self.maze.get_error_message()
        elif self.wumpus and self.wumpus.get_error_message() != "":
            msg = self.wumpus.get_error_message()
        elif self.repop_time < config.min_repop_time or self.repop_time > config.max_repop_time:
            msg = "il repop time deve essere compreso tra %d e %d minuti invece è: %d" % (
                config.min_repop_time, config.max_repop_time, self.repop_time)
        elif not self.landfill_code and not self.wild:
            msg = "landfill_code dell'area non valido: %r" % self.landfill_code
        elif self.get_error_message_resets() != "":
            msg = self.get_error_message_resets()
        else:
            return ""

        # Se arriva qui c'è un messaggio d'errore da inviare
        log.error("(Area: %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    def get_error_message_creators(self):
        if self.creators:
            from src.database import database
            hint = "controllare di aver inserito il nome con la maiuscola"
            for name in self.creators.split():
                if name not in database["accounts"]:
                    #return "area %s non ha trovato nell'etichetta Creators un nome tra quelli degli account: %s (%s)" % (
                    #    self.code, name, hint)
                    continue

        return ""
    #- Fine Metodo -

    def get_error_message_climates(self):
        for climate in self.climates:
            if climate.get_error_message() != "":
                return climate.get_error_message()

        return ""
    #- Fine Metodo -

    # (TD)
    def get_pedantic_messages(self):
        messages = []

        if not self.short_night and "@empty_short_night" not in self.comment:
            messages.append("short_night non è stata scritta, da ignorare nel qual caso nell'area non sussistano grossi cambiamenti di luce o altro, tra giorno e notte. (@empty_short_night)")

        length = len(remove_colors(getattr(self, "descr")))
        if length > config.max_google_translate * 2 and "@descr_too_long" not in self.comment:
            messages.append("descr è più lunga di %d caratteri: %d (@descr_too_long)" % (config.max_google_translate * 2, length))

        for i, message in enumerate(messages):
            messages[i] = "(Area: code %s) %s" % (self.code, message)

        return messages
    #- Fine Metodo -

    def get_name(self, looker=None):
        # (TD) fare il sistema di self.name
        if calendar.is_night() and self.short_night:
            return self.short_night
        else:
            return self.short
    #- Fine Metodo -

    def extract_rooms(self, except_these=None):
        if except_these is None:
            except_these = []

        for room in reversed(self.rooms.values()):
            if room.prototype.code not in except_these:
                room.extract(1)

        # (TD) L'estrazione del resto delle altre entità non dovrebbe servire,
        # tuttavia in futuro sarebbe il caso di aggiungere un check per
        # controllare i riferimenti
    #- Fine Metodo -

    # (TT) Questo metodo è uguale a quello in entity.py, possibilità di accorpare?
    def iter_contains(self, entity_tables=None, use_reversed=False):
        """
        È curioso come a volte questo metodo possa essere utilizzato per
        iterare i codici dell entità prototipo passando un entity_tables uguale a questo:
        ("proto_items", "proto_mobs", "proto_rooms"); per avere i valori di
        prototipo invece basta utilizzare il metodo iter_protos.
        """
        if not entity_tables:
            entity_tables = ["items", "mobs", "players"]

        if use_reversed:
            for type in entity_tables:
                for content in reversed(getattr(self, type)):
                    yield content
        else:
            for type in entity_tables:
                for content in getattr(self, type):
                    yield content
    #- Fine Metodo -

    def iter_protos(self, entity_tables=None, use_reversed=False):
        if not entity_tables:
            entity_tables = ["proto_items", "proto_mobs", "proto_rooms"]

        if use_reversed:
            for type in entity_tables:
                for content in reversed(getattr(self, type).values()):
                    yield content
        else:
            for type in entity_tables:
                for content in getattr(self, type).values():
                    yield content
    #- Fine Metodo -

    def get_list_of_entities(looker, include_looker="dummy-parameter", avoid_inventory="dummy-parameter", avoid_equipment="dummy-parameter", admin_descrs="dummy-parameter"):
        return getattr(self, entity_type)
    #- Fine Metodo -

    def get_min_coord(self, axis):
        if axis not in ("x", "y", "z"):
            log.bug("axis non è una asse cartesiano valido: %s" % axis)
            return 0

        #----------------------------------------------------------------------

        coords = []
        for room_reset in self.room_resets:
            coords.append(getattr(room_reset.destination, axis))

        if coords:
            return min(coords)
        else:
            return 0
    #- Fine Metodo -

    def get_max_coord(self, axis):
        if axis not in ("x", "y", "z"):
            log.bug("axis non è una asse cartesiano valido: %s" % axis)
            return 0

        #----------------------------------------------------------------------

        coords = []
        for room_reset in self.room_resets:
            coords.append(getattr(room_reset.destination, axis))

        if coords:
            return max(coords)
        else:
            return 0
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def get_area_from_argument(argument, only_exact=False):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return None

    # -------------------------------------------------------------------------

    for area in database["areas"].itervalues():
        if is_same(argument, area.code) or is_same(argument, area.name):
            return area

    if only_exact:
        return None

    for area in database["areas"].itervalues():
        if is_prefix(argument, area.code) or is_prefix(argument, area.name):
            return area

    return None
#- Fine Funzione -


def create_random_area(area, max_rooms, from_room=None, to_direction=DIR.NONE):
    """
    Crea casualmente un'area inserendovi stanze e entità create a loro volta
    casualmente.
    """

    if not area:
        log.bug("area non è un parametro valido: %r" % area)
        return

    if max_rooms < 1 or max_rooms > 1000:
        log.bug("max_rooms non è un parametro valido: %d" % max_rooms)
        return

    if not to_direction:
        log.bug("to_direction non è un parametro valido: %r" % to_direction)
        return

    # -------------------------------------------------------------------------

    from src.room import create_random_room

    max_rooms -= 1
    room = create_random_room()
    room.area = area
    if from_room and to_direction:
        room.x += to_direction.shift
        room.y += to_direction.shift
        room.z += to_direction.shift
        # (TD) Dovrei anche rendere casuale la creazione dell'uscita
        from_room.directions[to_direction] = Exit(to_direction)
        room.direction[to_direction.reverse_dir] = Exit(to_direction.reverse_dir)
    else:
        room.x = 0
        room.y = 0
        room.z = 0

    # Se non esiste già un'altra stanza a quelle coordinate la aggiunge
    coords = "%d %d %d" % room.x, room.y, room.z
    if coords not in area.rooms:
        area.rooms[coords] = room

    # Popola la stanza con mob e oggetti
    # (TD) probabilmente è migliorabile questo punto, almeno a livello di
    # quantità inseribili
    for i in range(random.randint(0, 4)):
        mob = create_random_mob()
        room.mobs.append(mob)
        area.mobs.append(mob)
    for i in range(random.randint(0, 4)):
        item = create_random_item()
        room.items.append(item)
        area.items.append(item)

    # Se non ha ancora raggiunto il numero massimo di stanze creabili per
    # l'area crea altre uscite casuali, il numero di stanze effettivamente
    # create alla fine del processo potrebbe benissimo non essere uguale al
    # valore originale di max_rooms.
    # Per esempio se la prima stanza stanza creata ha zero uscite la creazione
    # dell'area si ferma.
    if max_rooms > 0:
        # Sceglie un numero variabili di direzioni, c'è più probabilità
        # di creare meno direzioni, ma comunque più probabilità di crearne
        # almeno una
        if random.randint(0, 1) == 0:
            directions = random.sample(DIR.elements[1 : ], random.randint(1, 4))
        elif random.randint(0, 1) == 0:
            directions = random.sample(DIR.elements[1 : ], random.randint(0, 8))
        elif random.randint(0, 1) == 0:
            directions = random.sample(DIR.elements[1 : ], random.randint(2, 10))

        for direction in directions:
            create_random_area(area, max_rooms, room, direction)
#- Fine Funzione -
