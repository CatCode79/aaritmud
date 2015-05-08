# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle stanze, uscite, mura e destinazioni.
"""

#= IMPORT ======================================================================

import random

from src.affect      import get_error_message_affects
from src.behaviour   import BehaviourUpdaterSuperclass, room_behaviour_loop
from src.calendar    import calendar
from src.config      import config
from src.color       import remove_colors
from src.data        import Data
from src.database    import database
from src.describable import Describable
from src.element     import EnumElementDict, Element, Flags
from src.engine      import engine
from src.exit        import Exit, Wall
from src.extra       import Extras
from src.enums       import (CONTAINER, DOOR, DIR, EXIT, FLAG, GRAMMAR, LOG,
                             MATERIAL, POSITION, ROOM, SECTOR, SEX, TO)
from src.find_entity import RelativePointSuperclass
from src.gamescript  import import_instance_gamescripts, check_trigger
from src.grammar     import is_masculine, add_article
from src.log         import log
from src.material    import MaterialPercentages
from src.miml        import MIMLParserSuperclass, MIML_SEPARATOR
from src.reset       import DoorResetSuperclass
from src.utility     import put_final_dot, copy_existing_attributes, is_number, clean_string


#= CLASSI ======================================================================

class ProtoRoom(Data, Describable):
    """
    Gestisce un prototipo di stanza.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ["gamescripts"]
    MULTILINES  = ["descr", "descr_night", "descr_hearing", "descr_hearing_night",
                   "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night",
                   "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night"]
    SCHEMA      = {"extras"                    : ("src.extra",      "ExtraDescription"),
                   "width"                     : ("",               "measure"),
                   "depth"                     : ("",               "measure"),
                   "height"                    : ("",               "measure"),
                   "material_percentages"      : ("src.material",   "MaterialPercentage"),
                   "mod_temperature"           : ("",               "percent"),
                   "mod_light"                 : ("",               "percent"),
                   "mod_noise"                 : ("",               "percent"),
                   "filling_depth"             : ("",               "measure"),
                   "exits"                     : ("src.room",       "Exit"),
                   "walls"                     : ("src.room",       "Wall"),
                   "affects"                   : ("src.affect",     "Affect"),
                   "room_behaviour"            : ("src.behaviour",  "RoomBehaviour"),
                   "mob_behaviour"             : ("src.behaviour",  "MobBehaviour"),
                   "item_behaviour"            : ("src.behaviour",  "ItemBehaviour"),
                   "specials"                  : ("",               "str"),
                   "echoes_dawn"               : ("",               "str"),
                   "echoes_dawn_no_sun"        : ("",               "str"),
                   "echoes_sunrise"            : ("",               "str"),
                   "echoes_sunrise_no_sun"     : ("",               "str"),
                   "echoes_noon"               : ("",               "str"),
                   "echoes_noon_no_sun"        : ("",               "str"),
                   "echoes_sunset"             : ("",               "str"),
                   "echoes_sunset_no_sun"      : ("",               "str"),
                   "echoes_dusk"               : ("",               "str"),
                   "echoes_dusk_no_moon"       : ("",               "str"),
                   "echoes_dusk_full_moon"     : ("",               "str"),
                   "echoes_midnight"           : ("",               "str"),
                   "echoes_midnight_no_moon"   : ("",               "str"),
                   "echoes_midnight_full_moon" : ("",               "str")}
    REFERENCES  = {}
    WEAKREFS    = {"owner" : ["players", "proto_mobs", "proto_items"]}

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = True
    IS_EXIT   = False
    IS_WALL   = False
    IS_ACTOR  = False
    IS_MOB    = False
    IS_ITEM   = False
    IS_PLAYER = False
    IS_EXTRA  = False
    IS_PROTO  = True

    ACCESS_ATTR   = "proto_rooms"
    CONSTRUCTOR   = None  # Classe Room una volta che viene definita a fine modulo

    EXTRACTED_FLAG = ROOM.EXTRACTED

    def __init__(self, code="", name=""):
        self.comment                   = ""
        self.code                      = code or ""  # Codice identificativo della stanza
        self.sex                       = Element(SEX.NONE)
        self.name                      = name or ""  # Il nome della stanza
        self.short                     = ""    # Descrizione corta
        self.short_night               = ""    # Descrizione corta notturna
        self.descr                     = ""    # Descrizioni
        self.descr_night               = ""    # Descrizione notturna
        self.descr_hearing             = ""    # Descrizione uditiva
        self.descr_hearing_night       = ""    # Descrizione uditiva notturna
        self.descr_smell               = ""    # Descrizione odorosa
        self.descr_smell_night         = ""    # Descrizione odorosa notturna
        self.descr_touch               = ""    # Descrizione tattile
        self.descr_touch_night         = ""    # Descrizione tattile notturna
        self.descr_taste               = ""    # Descrizione del sapore
        self.descr_taste_night         = ""    # Descrizione del sapore notturna
        self.descr_sixth               = ""    # Descrizione del sesto senso
        self.descr_sixth_night         = ""    # Descrizione del sesto senso notturna
        self.extras                    = Extras()  # Descrizioni extra
        self.icon                      = ""    # Percorso dell'immagine icona che rappresenta la stanza
        self.tile                      = ""    # Percorso dell'immagine tile che rappresenta il settore nella mini-wild
        self.icon_night                = ""    # Nome dell'immagine icona che rappresenta la stanza di notte
        self.sector                    = Element(SECTOR.NONE)  # Tipo di settore
        self.flags                     = Flags(ROOM.NONE)  # Flag
        self.width                     = 0     # Larghezza media dalla parete est a quella ovest in metri
        self.depth                     = 0     # Profodità media dalla parete sud a quella nord in metri
        self.height                    = 0     # Altezza media dal pavimento al soffitto in metri
        self.material_percentages      = MaterialPercentages()  # Materiali di cui sono formate le pareti della stanza
        self.owner                     = None  # Proprietario della stanza
        self.mod_temperature           = 0     # Modificatore della temperatura rispetto a quella media dell'area
        self.mod_light                 = 0     # Modificare della luce nella stanza
        self.mod_noise                 = 0     # Modificatore del rumore rispetto a quello medio dell'area
        self.filling_type              = Element(MATERIAL.NONE)  # Tipo di materiale che copre il pavimento
        self.filling_depth             = 0     # Quanti centimetri è profondo il materiale che copre il pavimento
        self.exits                     = EnumElementDict()  # Uscite che vi sono nelle varie direzioni
        self.walls                     = EnumElementDict()  # Mura che vi sono nelle varie direzioni
        self.affects                   = []    # Lista delle effetti che andranno a colpire i mob e i giocatori all'interno della stanza
        self.room_behaviour            = None
        self.mob_behaviour             = None
        self.item_behaviour            = None
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
        self.music                     = ""    # File mid inviato quando un pg entra nella stanza
        self.specials                  = {}  # E' una lista di variabili speciali, possono essere utilizzate come delle flags, vengono aggiunte di solito nei gamescript

        # Variabili volatili
        self.affect_infos              = []
        self.gamescripts               = {}  # Dizionario delle differenti funzioni di gamescript
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s" % (super(ProtoRoom, self).__repr__(), self.code)
    #- Fine Metodo -

    def get_error_message(self):
        from src.entity import remove_little_words

        if not self.code:
            msg = "code non è valido: %r" % self.code
        elif "_room_" not in self.code:
            msg = "code di stanza senza l'identificativo _room_ al suo interno"
        elif not self.name:
            msg = "name non è valido: %r" % self.name
        elif not self.short:
            msg = "short non è valida: %r" % self.short
        elif self.short and remove_colors(self.short)[0].isupper() and clean_string(self.short)[0] != remove_little_words(self.short)[0]:
            #msg = "short non deve iniziare con la maiuscola a meno che non sia voluto: %s" % self.short
            return ""
        elif self.short_night and remove_colors(self.short_night)[0].isupper() and clean_string(self.short_night)[0] != remove_little_words(self.short_night)[0]:
            #msg = "short_night non deve iniziare con la maiuscola a meno che non sia voluto: %s" % self.short_night
            return ""
        # (TD) sarà bocciato il sistema nomi, quindi vincono le short o i nomi?
        #elif self.name and remove_colors(self.name)[0].isupper() and clean_string(self.name)[0] != remove_little_words(self.name)[0]:
        #    msg = "name non deve iniziare con la maiuscola a meno che non sia voluto: %s" % self.name
        elif self.short and self.short[-1] == ".":
            #msg = "short con un punto finale: %s" % self.short
            return ""
        elif self.short_night and self.short_night[-1] == ".":
            #msg = "short_night con un punto finale: %s" % self.short_night
            return ""
        elif self.name and self.name[-1] == ".":
            #msg = "name con un punto finale: %s" % self.name
            return ""
        elif not self.descr:
            msg = "descr non è valida: %s" % self.descr
        elif self.extras.get_error_message() != "":
            msg = self.extras.get_error_message()
        elif self.sector.get_error_message(SECTOR, "sector") != "":
            msg = self.sector.get_error_message(SECTOR, "sector")
        elif self.flags.get_error_message(ROOM, "flags") != "":
            msg = self.flags.get_error_message(ROOM, "flags")
        elif self.width < 0:
            msg = "width è una lunghezza e non può essere minore di 0: %d" % self.width
        elif self.depth < 0:
            msg = "depth è una lunghezza e non può essere minore di 0: %d" % self.depth
        elif self.height < 0:
            msg = "height è una lunghezza e non può essere minore di 0: %d" % self.height
        elif self.material_percentages.get_error_message(self) != "":
            return self.material_percentages.get_error_message(self)
        elif self.owner and self.owner() not in (database["players"].values() + database["mobs"].values() + database["items"].values()):
            msg = "owner non è un codice di entità valido: %s" % self.owner().code
        elif self.mod_temperature < -1000 or self.mod_temperature > 1000:
            msg = "mod_temperature modificatore in percentuale non è tra -1000 e 1000: %d" % self.mod_temperature
        elif self.mod_light < -1000 or self.mod_light > 1000:
            msg = "mod_light modificatore in percentuale non è tra -1000 e 1000: %d" % self.mod_light
        elif self.mod_noise < -1000 or self.mod_noise > 1000:
            msg = "mod_noise modificatore in percentuale non è tra -1000 e 1000: %d" % self.mod_noise
        elif self.filling_type.get_error_message(MATERIAL, "filling_type") != "":
            msg = self.filling_type.get_error_message(MATERIAL, "filling_type")
        elif self.filling_depth < 0:
            msg = "filling_depth è un'altezza e come tale non può essere minore di zero: %d" % self.filling_depth
        elif self.get_error_message_exits() != "":
            msg = self.get_error_message_exits()
        elif self.get_error_message_walls() != "":
            msg = self.get_error_message_walls()
        elif get_error_message_affects(self.affects) != "":
            msg = get_error_message_affects(self.affects)
        else:
            return ""

        if type(self) == ProtoRoom:
            log.bug("(ProtoRoom: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    def get_pedantic_messages(self):
        messages = []

        if not self.descr_night and "@empty_descr_night" not in self.comment:
            messages.append("descr_night non è stata scritta, da ignorare nel qual caso nella stanza non sussistano grossi cambiamenti di luce o altro, tra giorno e notte. (@empty_descr_night)")

        if not self.descr_hearing and not self.descr_smell and not self.descr_touch and not self.descr_taste and not self.descr_sixth and "@empty_senses" not in self.comment:
            message.append("nessuna descrizione sensoriale oltre quella visiva, sarebbe meglio scriverne almeno una. (@empty_senses)")

        if not self.extras and "@empty_extras" not in self.comment:
            message.append("nessuna descrizione extra impostata, era proprio quello che volevi? (@empty_extras)")

        decrs = ("descr", "descr_night", "descr_hearing", "descr_hearing_night", "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night", "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night")
        for descr in descrs:
            length = len(remove_colors(getattr(self, descr)))
            if length > config.max_google_translate * 2 and "@%s_too_long" % descr not in self.comment:
                messages.append("%s è più lunga di %d caratteri: %d (@%s_too_long)" % (descr, config.max_google_translate * 2, length, descr))

        if type(self) == ProtoRoom:
            for i, message in enumerate(messages):
                messages[i] = "(ProtoRoom: code %s) %s" % (self.code, message)

        return messages
    #- Fine Metodo -

    def get_error_message_exits(self):
        """
        Se c'è un errore nelle uscite ne invia il relativo messaggio.
        """
        if DIR.NONE in self.exits:
            return "Una delle uscita è DIR.NONE oppure una struttura di label Exits/End è vuota"

        for exit in self.exits.itervalues():
            if exit.get_error_message():
                return exit.get_error_message()

        return ""
    #- Fine Metodo -

    def get_error_message_walls(self):
        """
        Se c'è un errore nelle mura ne invia il relativo messaggio.
        """
        for wall in self.walls.itervalues():
            if wall.get_error_message():
                return wall.get_error_message()
        return ""
    #- Fine Metodo -

    def is_extracted(self):
        """
        Indica se la stanza è già stata estratta dal gioco.
        Serve soprattutto negli script contenenti delle deferLater per
        capire se la stanza è ancora in gioco dopo che la deferLater è scattata.
        """
        if ROOM.EXTRACTED in self.flags:
            return True
        return False
    #- Fine Metodo -

    def is_secret_door(self):
        return False
    #- Fine Metodo -

    def get_area_code(self):
        """
        Ritorna il codice dell'area carpendolo dal proprio codice
        """
        if "_room_" in self.code:
            return self.code.split("_room_", 1)[0]

        log.bug("Codice errato per la %s: %s" % (self.__class__.__name__, self.code))
        return ""
    #- Fine Metodo -


class Room(ProtoRoom, BehaviourUpdaterSuperclass, MIMLParserSuperclass, RelativePointSuperclass, DoorResetSuperclass):
    """
    Istanza di un prototipo di stanza.
    Gestisce la stanza vera e propria, cioè quelle che si 'vedono' in gioco.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ProtoRoom.VOLATILES + ["prototype", "looted", "fights", "visited"]
    MULTILINES  = ProtoRoom.MULTILINES + []
    SCHEMA      = {}
    SCHEMA.update(ProtoRoom.SCHEMA)
    REFERENCES  = {"area"    : ["areas"],
                   "players" : ["players"],
                   "mobs"    : ["mobs"],
                   "items"   : ["items"]}
    REFERENCES.update(ProtoRoom.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(ProtoRoom.WEAKREFS)

    ACCESS_ATTR = "rooms"
    IS_PROTO    = False
    CONSTRUCTOR = None  # Classe Room una volta che viene definita a fine modulo

    def __init__(self, code=""):
        super(Room, self).__init__()

        self.code = ""
        self.prototype = None
        if code:
            self.reinit_code(code)
            copy_existing_attributes(self.prototype, self, except_these_attrs=["code"])
            self.after_copy_existing_attributes()

        self.area    = None # Area in cui si trova la stanza
        self.x       = 0    # Coordinata x dell'area in cui si trova
        self.y       = 0    # Coordinata y dell'area in cui si trova
        self.z       = 0    # Coordinata z dell'area in cui si trova
        self.players = []  # Lista dei personaggi nella stanza
        self.mobs    = []  # Lista dei mob nella stanza
        self.items   = []  # Lista degli oggetti nella stanza

        # Variabili volatili
        self.looted  = 0    # Totale delle monete raccolte nella stanza dai giocatori
        self.fights  = 0    # Totale dei combattimenti iniziati nella stanza dai giocatori
        self.visited = 0    # Totale delle volte che la stanza è stata visitata dati giocatori

        check_trigger(self, "on_init", self)
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s %d %d %d %s" % (super(ProtoRoom, self).__repr__(), self.code, self.x, self.y, self.z, self.area.code if self.area else "None")
    #- Fine Metodo -

    def get_error_message(self):
        msg = super(Room, self).get_error_message()
        if msg:
            pass
        elif self.area.code not in database["areas"]:
            msg = "codice dell'area inesistente nel database :%s" % self.area.code
        elif self.looted < 0:
            msg = "looted è una quantità e non può essere minore di 0: %d" % self.looted
        elif self.fights < 0:
            msg = "fights è una quantità e non può essere minore di 0: %d" % self.fights
        elif self.visited < 0:
            msg = "visited è una quantità e non può essere minore di 0: %d" % self.visited
        else:
            return ""

        log.bug("(Room: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    def reinit_code(self, code):
        """
        Inizializza il codice relativo alle entità persistenti.
        """
        if not code:
            log.bug("code non è un parametro valido: %r" % code)
            return

        # ---------------------------------------------------------------------

        old_code = self.code

        if "#" in code:
            self.code  = code
            self.prototype = database["proto_rooms"][code.split("#")[0]]
        else:
            self.code  = "%s#%s" % (code, id(self))
            self.prototype = database["proto_rooms"][code]

        if old_code and old_code in database["rooms"]:
            del(database["rooms"][old_code])
            database["rooms"][self.code] = self
    #- Fine Metodo -

    def after_copy_existing_attributes(self):
        try:
            self.gamescripts = import_instance_gamescripts(self)
        except ImportError:
            self.gamescripts = {}

        # Prepara la cache per i valori di behaviour
        if self.mob_behaviour:
            self.cache_behaviour("mob_behaviour")
        if self.item_behaviour:
            self.cache_behaviour("item_behaviour")
        if self.room_behaviour:
            self.room_behaviour.cache(self)
    #- Fine Metodo -

    def inject_to_area(self, area, coords):
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return

        if not coords:
            log.bug("coords non è un parametro valido: %r" % coords)
            return

        # ---------------------------------------------------------------------

        x, y, z = coords.split()
        if is_number(x):
            self.x = int(x)
        else:
            log.bug("x non è una coordinata valida: %s (stanza %s, area %s)" % (coords, self.code, area.code))
            return
        if is_number(y):
            self.y = int(y)
        else:
            log.bug("y non è una coordinata valida: %s (stanza %s, area %s)" % (coords, self.code, area.code))
            return
        if is_number(z):
            self.z = int(z)
        else:
            log.bug("z non è una coordinata valida: %s (stanza %s, area %s)" % (coords, self.code, area.code))
            return

        if self.area:
            log.bug("La stanza %s possiede già un'area valida: %s" % (self.code, area.code))
        self.area = area

        if coords in area.rooms:
            log.bug("L'area %s possiede già la stanza %s alle coordinate %s" % (area.code, area.rooms[coords].code, coords))
        area.rooms[coords] = self

        if self.code in database["rooms"]:
            log.bug("Il database delle stanze possiede già la stanza %s" % self.code)
        database["rooms"][self.code] = self

        self.reset_doors(area)
    #- Fine Metodo -

    def extract(self, quantity):
        # Per avere lo stesso interfacciamento della extract delle entità v'è il
        # parametro quantity, ma tale parametro è inutilizzato e deve essere
        # sempre impostato a 1 di default.
        # Lo so che potrebbe essere bizzarro come sistema, ma preferisco avere
        # una consistenza nella API del codice di questo tipo.
        if quantity != 1:
            log.bug("parametro quantity per il metodo extract della classe %s è differente da 1: %d" % (self.__class__, quantity))
            quantity = 1

        for entity in self.iter_contains(use_reversed=True):
            entity.extract(use_repop=False)

        coords = "%d %d %d" % (self.x, self.y, self.z)
        if self.area:
            if coords in self.area.rooms:
                del(self.area.rooms[coords])
            else:
                log.bug("Non è stata trovata nessuna coordinata %s nell'area %s per la stanza %s" % (coords, self.area.code, self.code))
        else:
            # Cerca comunque di trovare la stanza da estrarre nelle liste di
            # coordinate delle aree
            for area in database["areas"]:
                if coords in area.rooms:
                    if area.rooms[coords] == self:
                        log.bug("%s non ha l'area valida: %r (ma è stata trovata comunque nell'area %s alle coordinate %s)" % (
                            self.code, self.area, area.code, coords))
                        break
            else:
                log.bug("%s non ha l'area valida: %r (e non è stata trovata nessuna coordinata valida nelle aree)" % (
                    self.code, self.area))

        if self.code in database["rooms"]:
            del(database["rooms"][self.code])
        else:
            log.bug("Stanza %s da estrarre non trovata nel database delle rooms." % self.code)

        # Rimuove l'eventuale presenza della stanza tra quelle sotto behaviour
        if self in room_behaviour_loop.behavioured_rooms:
            room_behaviour_loop.behavioured_rooms.remove(self)

        # A volte è utile conoscere se un'entità è già stata estratta o meno
        # poiché l'entità nonostante sia stata rimossa dal gioco potrebbe
        # ancora venire utilizzata, erroneamente, da una deferLater
        self.flags += ROOM.EXTRACTED
    #- Fine Metodo -

    # - Metodi getter ---------------------------------------------------------

    # (TD) metodo uguale a quello in Entity, usare la Location
    def iter_contains(self, entity_tables=None, use_reversed=False):
        """
        Itera nel contenuto del solo inventario.
        Il parametro use_reversed viene utilizzato il più delle volte per
        evitare che entità estratte durante l'iterazione provochino dei buchi
        nell'iterazione stessa, saltando un'entità. Il tipico sintomo di tale
        problema è che alle entità del ciclo iterativo viene eseguite
        determinate istruzioni/funzione/metodo solo una sì ed una no.
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

    # (TD) metodo (quasi) uguale a quello in Entity, usare la Location
    def _iter_variant_entities(self, variant, entity_tables=None, use_can_see=False):
        """
        Itera tutte le entità contenute e volute.
        Non è ricorsiva per ragioni prestazionali.
        Qui al metodo iter_contains non bisogna assolutamente utilizzare il
        parametro use_reversed per evitare di mischiare senza senso la lista
        generata e inficiare così l'eventuale utilizzo dell'use_reversed
        'superiore' che serve sostanzialmente ad evitare dei buchi se la lista
        iterata viene modificata rimuovendo elementi.
        """
        if variant not in ("all", "opened", "openable", "interactable"):
            log.bug("variant non è un parametro valido: %r" % variant)
            yield None

        # ---------------------------------------------------------------------

        contained_entities = []
        target = self

        while True:
            for contained_entity in target.iter_contains(entity_tables=entity_tables):
                # La room non utilizza il check del can_see
                #if use_can_see and not self.can_see(contained_entity):
                #    continue
                if variant == "opened":
                    if not contained_entity.container_type or CONTAINER.CLOSED in contained_entity.container_type.flags:
                        continue
                if variant == "openable":
                    if not contained_entity.container_type or CONTAINER.LOCKED in contained_entity.container_type.flags:
                        continue
                if variant == "interactable":
                    if ((not contained_entity.container_type or CONTAINER.CLOSED in contained_entity.container_type.flags)
                    and FLAG.INTERACTABLE_FROM_OUTSIDE not in contained_entity.flags):
                        continue
                contained_entities.append(contained_entity)

            if not contained_entities:
                break
            target = contained_entities.pop()

            yield target
    #- Fine Metodo -

    # (TD) metodo uguale a quello in Entity, usare la Location
    def iter_all_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera in tutte le entità contenute.
        """
        if use_reversed:
            return reversed(list(self._iter_variant_entities("all", entity_tables=entity_tables)))
        else:
            return self._iter_variant_entities("all", entity_tables=entity_tables)
    #- Fine Metodo -

    # (TD) metodo uguale a quello in Entity, usare la Location
    def iter_through_opened_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera tutte le entità contenute in tutti i contenitori trovati aperti.
        """
        if use_reversed:
            return reversed(list(self._iter_variant_entities("opened", entity_tables=entity_tables)))
        else:
            return self._iter_variant_entities("opened", entity_tables=entity_tables)
    #- Fine Metodo -

    # (TD) metodo uguale a quello in Entity, usare la Location
    def iter_through_openable_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera tutte le entità contenute in tutti i contenitori trovati apribili
        (cioè non locked).
        """
        if use_reversed:
            return reversed(list(self._iter_variant_entities("openable", entity_tables=entity_tables, use_can_see=use_can_see)))
        else:
            return self._iter_variant_entities("openable", entity_tables=entity_tables, use_can_see=use_can_see)
    #- Fine Metodo -

    # (TD) metodo uguale a quello in Entity, usare la Location
    def iter_only_interactable_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera tutte le entità contenute in tutti i contenitori trovati aperti
        e che abbiano la FLAG.INTERACTABLE_FROM_OUTSIDE.
        """
        if use_reversed:
            interactable_entities = reversed(list(self._iter_variant_entities("interactable", entity_tables=entity_tables, use_can_see=use_can_see)))
        else:
            interactable_entities = self._iter_variant_entities("interactable", entity_tables=entity_tables, use_can_see=use_can_see)

        # Bisogna fare così perché alcune delle entità recuperate dalla variant
        # sono dei contenitori
        for en in interactable_entities:
            if FLAG.INTERACTABLE_FROM_OUTSIDE in en.flags:
                yield en
    #- Fine Metodo -

    # (TD) il metodo è uguale a quello in entity, da accorpare?
    def group_entities(self):
        """
        Controlla se c'è bisogno di accorpare dell'entità in mucchietti uguali.
        """
        if not config.use_physical_grouping:
            return

        # (bb) tuttavia c'è un problema, se l'entità da raggruppare è un
        # parametro di una deferred relativa ad un gamescript allora
        # l'entità verrà cmq estratta nonostante la cosa non sia voluta
        # E' un problema che si risolve solo con un gran refactoring ma
        # è possibile quindi ho deciso di rendere automatico il grouping
        for en in self.iter_contains(entity_tables=["items", "mobs"], use_reversed=True):
            en.group_entity()
    #- Fine Metodo -

    def get_name(self, looker=None):
        """
        Ritorna il nome o la short della stanza, looker viene passato per capire
        se l'osservatore conosce abbastanza bene la stanza da ritornargli il
        nome (sistema di presentazione e memoria).
        """
        result = ""

        # (TD) manca il self.name se l'entità conosce adeguatamente la stanza
        #if "[" in name:
        #    return self.name
        #else:
        #    return "[white]%s[close]" % self.name

        if calendar.is_day() or not self.short_night:
            return self.short
        else:
            return self.short_night
    #- Fine Metodo -

    def get_descr(self, type="", looker=None):
        """
        Ritorna la descrizione della stanza.
        """
        if type:
            type = "_" + type

        # Recupera la descrizione notturna o diurna
        descr = ""
        if calendar.is_night():
            descr = getattr(self, "descr%s_night" % type)
        if not descr:
            descr = getattr(self, "descr%s" % type)

        if MIML_SEPARATOR in descr:
            descr = self.parse_miml(descr, looker)
        if "$" in descr:
            descr = looker.replace_act_tags_name(descr, looker=looker, target=self)
        if "$" in descr:
            descr = looker.replace_act_tags(descr, target=self)

        # Può accadere per le descrizioni sensoriali differenti da quelli
        # della vista
        if not descr:
            if not type:
                log.bug("descr non valida con type a %s per la stanza %s: %r" % (
                    type, self.code, descr))
            return ""

        if self.ASCIIART_TAG_OPEN in descr:
            descr = self.convert_asciiart_linefeeds(descr)
        else:
            descr = put_final_dot(descr)

        if ".\n" in descr:
            descr = descr.replace(".\n", ".<br>")
        if "!\n" in descr:
            descr = descr.replace("!\n", "!<br>")
        if "?\n" in descr:
            descr = descr.replace("?\n", "?<br>")
        if "\n" in descr:
            descr = descr.replace("\n", " ")

        return descr
    #- Fine Metodo -

    def is_dark(self):
        """
        Ritorna vero se la stanza in cui si trova l'entità è buia.
        """
        # (TD)
        return False
    #- Fine Metodo -

    # (TD) stesso metodo in entity.py, magari accorpare in Location
    def is_empty(self):
        if self.items or self.mobs or self.players:
            return False
        else:
            return True
    #- Fine Metodo -

    def get_destination(self, direction=DIR.NONE):
        """
        Ricava la destinazione dalla room di partenza verso la direzione passata.
        L'argomento direction è un elemento di enumerazione DIR.
        Attenzione che questa funzione non esegue controlli sulle porte o sui muri.
        """
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return None

        # -------------------------------------------------------------------------

        # Se viene passata la direzione none, allora ritorna la destinazione
        # della stanza attuale
        if direction == DIR.NONE:
            destination = Destination()
            destination.x    = self.x
            destination.y    = self.y
            destination.z    = self.z
            destination.area = self.area
            return destination

        # Se in quella direzione c'è già una destinazione voluta la ritorna
        # Di solito se esiste una destinazione specifica serve a spostarsi tra
        # un'area e un'altra oppure tramite un teletrasporto (o direzioni illogiche)
        if direction in self.exits and self.exits[direction].destination:
            return self.exits[direction].destination

        # Altrimenti ricava la destinazione verso quella direzione nell'attuale area
        coords = "%d %d %d" % (
            self.x + direction.shift[0],
            self.y + direction.shift[1],
            self.z + direction.shift[2])
        if coords in self.area.rooms:
            destination = Destination()
            destination.x    = self.x + direction.shift[0]
            destination.y    = self.y + direction.shift[1]
            destination.z    = self.z + direction.shift[2]
            destination.area = self.area
            return destination

        # E' possibilissimo che non trovi nessuna stanza alle coordinate
        # dell'area quindi se arriva qui normalmente non è un errore
        return None
    #- Fine Metodo -

    def get_destination_room(self, direction=DIR.NONE):
        """
        Chiama il metodo get_destination e get_room in successione.
        Esiste per evitare codice boilerplate.
        """
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return None

        # -------------------------------------------------------------------------

        destination = self.get_destination(direction)
        if not destination:
            return None

        destination_room = destination.get_room()
        if not destination_room:
            # E' una cosa abbastanza normale in realtà, visto che lato building
            # si ha la tendenza a creare uscite che non puntano a nulla quando
            # si crea l'area, quindi è commentato per non spammare
            #log.bug("Non è stata trovata una stanza con destinazione valida: %r" % destination)
            return None

        return destination_room
    #- Fine Metodo -

    def get_reverse_exit(self, direction):
        """
        Ritorna l'uscita inversa, relativa alla stanza di destinazione, che
        riporta a questa stanza.
        """
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return None

        # ---------------------------------------------------------------------

        if direction not in self.exits:
            log.bug("direction %s non si trova tra le uscite di %s" % (direction, self.code))
            return None

        destination_room = self.get_destination_room(direction)
        if not destination_room:
            return None

        for reverse_dir in destination_room.exits:
            reverse_destination_room = destination_room.get_destination_room(reverse_dir)
            if reverse_destination_room == self:
                return destination_room.exits[reverse_dir]

        return None
    #- Fine Metodo -

    # (OO) Se fosse possibile bisognerebbe cercare in alcuni punti di passare
    # il parametro opzionale destination_room invece di ricavarlo
    def get_door(self, direction, direct_search=True, reverse_search=True):
        """
        Ritorna l'entità relativa alla porta che si trova in quella direzione.
        Potebbero esservi potenzialmente due porte in una stessa direzione,
        quindi se non trova la prima, relativa all'uscita della propria stanza
        controlla se esiste quella nella stanza di destinazione.
        """
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return

        # direct_search e reverse_search hanno valore di verità

        # ---------------------------------------------------------------------

        if direction == DIR.NONE:
            log.bug("direzione passata errata: %r" % direction)
            return None

        if direct_search:
            if direction in self.exits:
                door = self.exits[direction].door
                if isinstance(door, basestring):
                    log.bug("codice di porta %s inserito errato o senza che la relativa proto entity sia stata creata effettivamente" % door)
                    return None
                if door and door.door_type:
                    return door

        if reverse_search:
            destination_room = self.get_destination_room(direction)
            if not destination_room:
                return None

            if direction.reverse_dir in destination_room.exits:
                reverse_door = destination_room.exits[direction.reverse_dir].door
                if isinstance(reverse_door, basestring):
                    log.bug("codice di porta %s inserito errato o senza che la relativa proto entity sia stata creata effettivamente" % reverse_door)
                    return None
                if reverse_door and reverse_door.door_type:
                    return reverse_door

        return None
    #- Fine Metodo -

    def iter_viable_directions(self, closed_doors=False):
        # Qui non ci sono problemi di reversed perchè si lavora tramite la
        # iteritems e non con una lista direttamente
        for direction, exit in self.exits.iteritems():
            if EXIT.NO_LOOK_LIST in exit.flags or EXIT.DIGGABLE in exit.flags:
                continue

            if not exit.door or not exit.door.door_type or DOOR.CLOSED not in exit.door.door_type.flags:
                yield direction
                continue

            door_type = exit.door.door_type
            if not door_type:
                log.bug("Porta inattesa %s senza struttura per le informazioni di door_type alla stanza %s" % (exit.door.code, self.code))
                continue

            if DOOR.SECRET in door_type.flags:
                continue

            if closed_doors and DOOR.CLOSED in door_type.flags:
                yield direction
                continue
    #- Fine Metodo -

    def act(self, message):
        """
        Non è un vero e propria act, è più una echo, ma per far funzionare la
        room come una entità ha lo stesso nome.
        """
        if not message:
            log.bug("message non è un parametro valido: %r" % message)
            return

        # ---------------------------------------------------------------------

        for other in self.iter_contains():
            other.send_output(message)
            other.send_prompt()
    #- Fine Metodo -

    # (TD) questo metodo è uguale a quello in Entity, accorpare?
    def echo(self, message):
        if not message:
            log.bug("message non è un parametro valido: %r" % message)
            return

        # ---------------------------------------------------------------------

        for en in self.iter_contains():
            if en.position > POSITION.SLEEP:
                en.send_output("\n%s" % put_final_dot(message))
                en.send_prompt()
    #- Fine Metodo -


class Destination(object):
    """
    Classe che serve a salvare le coordinate spaziali per una stanza.
    Difatti non basta poter identificare la posizione della stanza con il
    suo riferimento in memoria poiché tramite i reset una stanza può essere
    inserita al posto di un'altra.
    Allo stesso tempo non è possibile identificare una posizione dal codice
    di una stanza perché ci possono essere più istanze della stessa.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {"area" : ["areas"]}
    WEAKREFS    = {}

    def __init__(self, x=0, y=0, z=0, area=None):
        if x < -10000 or x > 10000:
            log.bug("x non è un parametro valido: %s" % x)
            return

        if y < -10000 or y > 10000:
            log.bug("y non è un parametro valido: %s" % y)
            return

        if z < -10000 or z > 10000:
            log.bug("z non è un parametro valido: %s" % z)
            return

        if not area and area is not None:
            log.bug("area non è un parametro valido: %s" % area)
            return

        # ---------------------------------------------------------------------

        if isinstance(area, basestring):
            try:
                area = database["areas"][area]
            except KeyError:
                log.bug("area %s non è un codice di area valido" % area)
                area = None

        self.x    = x
        self.y    = y
        self.z    = z
        self.area = area
    #- Fine Inizializzazione -

    def __repr__(self):
        if not self.area:
            log.bug("self.area non è valido: %r" % self.area)
            return "%d %d %d None" % (self.x, self.y, self.z)

        return "%d %d %d %s" % (self.x, self.y, self.z, self.area.code)
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Destination()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, destination2):
        if not destination2:
            return False

        if self.x != destination2.x:
            return False
        if self.y != destination2.y:
            return False
        if self.z != destination2.z:
            return False
        if self.area != destination2.area:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_room(self):
        if not self.area:
            log.bug("self.area non è valido: %r (per la stanza alle coordinate %s)" % (self.area, coords))
            return None

        coords = "%d %d %d" % (self.x, self.y, self.z)
        try:
            return self.area.rooms[coords]
        except KeyError:
            # Può essere normale se per caso è stato ricavato in precedenza una
            # destination e solo poi utilizzata per ricavare la room, room che
            # magari nell'intanto è stata rimossa dal gioco
            return None
    #- Fine Metodo -

    def get_error_message(self):
        """
        Se trova un errore nell'istanza della destinazione ritorna il
        relativo messaggio.
        """
        if not self.area:
            msg = "l'area non è valida: %r" % self.area
        elif self.area.code not in database["areas"]:
            msg = "il codice dell'area non è valido: %r" % self.area.code
        else:
            return ""

        return "(destination): %s" % msg
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        """
        Ricava dalla linea passata i valori di destinazione.
        """
        if not file and file is not None:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro  valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro  valido: %r" % attr)
            return

        # -------------------------------------------------------------------------

        values = line.split(None)

        # Qui non si può utilizzare il metodo get_error_message perché self.area
        # è ancora una stringa relativa al codice di un'area e non un
        # riferimento ad un'area, quindi vengono eseguiti dei controlli ad uopo
        if len(values) != 4:
            log.bug("la linea relativa alla destinazione deve avere 4 argomenti e non %d. File <%s> linea <%s> attributo <%s>" % (
                len(values), file.name if file else "None", line, attr))
            return

        try:
            values[0] = int(values[0])
        except:
            log.bug("Coordinata x errata %s per la destinazione nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                values[0], file.name if file else "None", line, attr))
            return

        try:
            values[1] = int(values[1])
        except:
            log.bug("Coordinata x errata %s per la destinazione nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                values[1], file.name if file else "None", line, attr))
            return

        try:
            values[2] = int(values[2])
        except:
            log.bug("Coordinata x errata %s per la destinazione nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                values[2], file.name if file else "None", line, attr))
            return

        if values[3] not in database["areas"] and values[3] not in database.reading_data_code:
            log.bug("Codice di area destinazione ricavato errato %s nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                values[3], file.name if file else "None", line, attr))
            return

        self.x, self.y, self.z, self.area = values[0], values[1], values[2], values[3]
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        """
        Scrive su file le coordinate identificative per una destinazione alle
        coordinate di una certa area.
        """
        if not file:
            log.bug("file non è valido: %s" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        file.write(indentation + label)
        file.write("%d %d %d %s" % (self.x, self.y, self.z, self.area.code))
        file.write("\n")
    # - Fine della Metodo -


#= FUNZIONI ====================================================================

def create_random_room(sector=SECTOR.NONE, name="", width=0, depth=0, height=0):
    """
    Crea una stanza con valori casuali e la ritorna.
    """
    if not sector:
        log.bug("sector non è un parametro valido: %r" % sector)
        return None

    # name può essere una stringa vuota

    # Le distanze sono di default in centimetri
    if width < 0 or width > 10000:
        log.bug("width non è un parametro valido: %d" % width)
        return None

    if depth < 0 or depth > 10000:
        log.bug("depth non è un parametro valido: %d" % depth)
        return None

    if height < 0 or height > 10000:
        log.bug("height non è un parametro valido: %d" % height)
        return None

    # -------------------------------------------------------------------------

    # (bb) codice prototype errato perchè la stanza non esiste, bisogna creare
    # on memory delle istanza di ati prototype da utilizzare nei testing
    room = Room(code="limbo_room_random#1234567890")

    # Il settore viene utilizzato per creare il nome della stanza, se questo
    # non è stato passato
    if room.sector == SECTOR.NONE:
        room.sector.randomize()

    # Prepara il nome della stanza
    if not room.name:
        if is_masculine(room.sector.short):
            room.name = add_article(room.sector.short, GRAMMAR.MASCULINE)
        else:
            room.name = add_article(room.sector.short, GRAMMAR.FEMININE)

    # Prepara la descrizione della stanza
    if is_masculine(room.sector.short):
        room.descr = add_article(room.sector.short.lower(), GRAMMAR.MASCULINE, GRAMMAR.INDETERMINATE)
    else:
        room.descr = add_article(room.sector.short.lower(), GRAMMAR.FEMININE, GRAMMAR.INDETERMINATE)

    # Rende casuali le flags
    room.flags.randomize()

    # Rende casuali le dimensioni della stanza
    room.width = width
    if room.width == 0:
        room.width = random.randint(0, 1000)
        if room.width == 0:
            room.width = random.randint(1000, 2000)
    room.depth = depth
    if room.depth == 0:
        room.depth = random.randint(0, 1000)
        if room.depth == 0:
            room.depth = random.randint(1000, 2000)
    room.height = height
    if room.height == 0:
        room.height = random.randint(0, 700)
        if room.height == 0:
            room.height = random.randint(800, 1500)

    # Gestiste i modificatori ambientali
    room.mod_temperature = random.randint(-5, 5)
    if room.mod_temperature == 0:
        room.mod_temperature = random.randint(-20, 20)
    room.mod_light = random.randint(-5, 5)
    if room.mod_light == 0:
        room.mod_light = random.randint(-20, 20)
    room.mod_noise = random.randint(-5, 5)
    if room.mod_noise == 0:
        room.mod_noise = random.randint(-20, 20)

    # 10% di possibilità di inserire un materiale nella stanza
    if random.randint(1, 10) == 1:
        room.filling_type.randomize()
        room.fillingh_depth = random.randint(0, 40)
        if room.filling_depth == 0:
            room.filling_depth = random.randint(26, 80)

    # 25% di probabilità di creare un'uscita nella direzione
    for direction in DIR.elements:
        if random.randint(1, 4) == 1:
            exit = Exit(direction)
            room.exits[direction] = exit

    # 20% di probabilità di creare un muro nella direzione
    for direction in DIR.elements:
        if random.randint(1, 5) == 1:
            wall = Wall(direction)
            wall.material.randomize()
            wall.depth = random.randint(5, 40)
            # C'è un terzo di possibilità di creare mura più forti
            if random.randint(1, 4) == 1:
                wall.depth = random.randint(41, 80)
            room.walls[direction] = wall

    # (TD) gli affect per ora li salto che non li ho ancora fatti
    pass

    return room
#- Fine Funzione -


#= FINALIZE ====================================================================

ProtoRoom.CONSTRUCTOR = Room
Room.CONSTRUCTOR = Room
