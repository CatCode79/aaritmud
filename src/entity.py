# -*- coding: utf-8 -*-

"""
Modulo riguardante le Entità del Mud, un classe ProtoEntity è la base per
gli Item, i Mob e i Player.
"""


#= IMPORT ======================================================================

import collections
import copy
import math
import random
import weakref

from src.act            import Act
from src.affect         import get_error_message_affects, is_affected
from src.calendar       import calendar
from src.color          import convert_colors, get_first_color, color_first_upper, color_first_lower, remove_colors
from src.config         import config
from src.data           import Data
from src.database       import database
from src.defer          import defer, set_deferred_args
from src.describable    import Describable
from src.element        import Element, Flags
from src.engine         import engine
from src.enums          import (AREA, AFFECT, CHANNEL, CONTAINER, DOOR, ENTITYPE,
                                FLAG, HAND, MATERIAL, MONTH, OPTION, PART, POINTS,
                                POSITION, RACE, RESET, SEX, TO, TRUST, WEAR)
from src.exit           import get_destination_room_from_door
from src.extra          import Extras
from src.fight          import is_fighting, get_fight, get_opponent
from src.find_entity    import FindEntitySuperclass, RelativePointSuperclass, INSTANCE, ENTITIES, COUNTER
from src.gamescript     import import_instance_gamescripts, check_trigger
from src.grammar        import grammar_gender
from src.interpret      import interpret, translate_input
from src.log            import log
from src.material       import MaterialPercentages
from src.move           import EntityMoveSuperclass
from src.miml           import MIMLParserSuperclass, MIML_SEPARATOR
from src.reset          import HasResetLocationSuperclass
#from src.name           import create_random_name
from src.utility        import (get_percent, put_final_dot, copy_existing_attributes,
                                format_for_admin, clean_string, multiple_arguments,
                                pretty_list, add_to_phrase, remove_tags)
from src.web_resource   import IFRAME_BROWSERS, OUTPUT_END_TAG, send_audio, create_icon

from src.commands.command_look import look_a_room
from src.entitypes.door        import _is_secret_door
from src.loops.aggressiveness  import check_aggressiveness, can_aggress
from src.loops.digestion       import stop_digestion

from src.entitypes.container import Container
from src.entitypes.corpse    import Corpse


#= COSTANTI ====================================================================

little_words = []

EXCEPT_THESE_ATTRS = ("code", "previous_location", "location", "killed_times",
    "quantity", "persistent_act", "max_global_quantity", "current_global_quantity",
    "sended_inputs", "backsteps", "deferred_repop", "last_movement")


#= CLASSI ======================================================================

class ProtoEntity(Describable, Data, Act, MIMLParserSuperclass, FindEntitySuperclass, HasResetLocationSuperclass, RelativePointSuperclass, EntityMoveSuperclass):
    """
    Entità madre per gli oggetti, i mob e i personaggi.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ["persistent_act", "snoopers", "game_request", "retran", "regoto",
                   "waiting_inputs", "sended_inputs", "backsteps", "location",
                   "current_global_quantity", "gamescripts", "action_in_progress",
                   "incognito", "fights", "deferred_purification",
                   "affect_infos", "deferred_wait", "repop_later", "last_movement",
                   "interactions"]
    MULTILINES  = ["descr", "descr_night", "descr_hearing", "descr_hearing_night",
                   "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night",
                   "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night"]
    SCHEMA      = {"extras"               : ("src.extra",               "ExtraDescription"),
                   "dialogs"              : ("src.dialog",              "Dialog"),
                   "affects"              : ("src.affect",              "Affect"),
                   "shop"                 : ("src.shop",                "Shop"),
                   "aggressivenesses"     : ("",                        "str"),
                   "weight"               : ("",                        "weight"),
                   "size"                 : ("",                        "percent"),
                   "material_percentages" : ("src.material",            "MaterialPercentage"),
                   "skills"               : ("",                        "int"),
                   "container_type"       : ("src.entitypes.container", "Container"),
                   "corpse_type"          : ("src.entitypes.corpse",    "Corpse"),
                   "door_type"            : ("src.entitypes.door",      "Door"),
                   "drink_type"           : ("src.entitypes.drink",     "Drink"),
                   "fishing_type"         : ("src.entitypes.fishing",   "Fishing"),
                   "food_type"            : ("src.entitypes.food",      "Food"),
                   "money_type"           : ("src.entitypes.money",     "Money"),
                   "plant_type"           : ("src.entitypes.plant",     "Plant"),
                   "portal_type"          : ("src.entitypes.portal",    "Portal"),
                   "readable_type"        : ("src.entitypes.readable",  "Readable"),
                   "seed_type"            : ("src.entitypes.seed",      "Seed"),
                   "weapon_type"          : ("src.entitypes.weapon",    "Weapon"),
                   "wear_type"            : ("src.entitypes.wear",      "Wear"),
                   "walker"               : ("src.move",                "Walker"),
                   "extract_timeout"      : ("src.entity",              "ExtractTimeout")}
    REFERENCES  = {"players"              : ["players"],
                   "mobs"                 : ["mobs"],
                   "items"                : ["items"],
                   "leader"               : ["items", "mobs", "players"],
                   "guide"                : ["items", "mobs", "players"],
                   "master"               : ["items", "mobs", "players"],
                   "mount"                : ["mobs", "items", "players"],
                   "remains"              : ["proto_mobs", "proto_items"],
                   "remains_night"        : ["proto_mobs", "proto_items"]}
    WEAKREFS    = {"owner"                : ["proto_items", "proto_mobs", "items", "mobs", "players"],
                   "previous_location"    : ["rooms", "items", "mobs", "players"],
                   "under_weared"         : ["items", "mobs", "players"]}

    EXTRACTED_FLAG = FLAG.EXTRACTED

    def __init__(self):
        self.comment               = ""
        self.level                 = 1
        self.race                  = Element(RACE.NONE)  # Se l'entità è un mob è la razza normale, se è un oggetto indica la fattura dell'oggetto relativa a quella razza
        self.sex                   = Element(SEX.NONE)
        self.keywords_name         = ""
        self.keywords_short        = ""
        self.keywords_short_night  = ""
        self.name                  = ""  # Il nome dell'entità, quello che si legge quando una entità si presenta con il proprio vero nome
        self.short                 = ""  # descrizione corta
        self.short_night           = ""  # descrizione corta notturna
        self.long                  = ""  # descrizione lunga
        self.long_night            = ""  # descrizione lunga notturna
        self.descr                 = ""  # descrizioni
        self.descr_night           = ""  # descrizione notturna
        self.descr_hearing         = ""  # descrizione uditiva
        self.descr_hearing_night   = ""  # descrizione uditiva notturna
        self.descr_smell           = ""  # descrizione odorosa
        self.descr_smell_night     = ""  # descrizione odorosa notturna
        self.descr_touch           = ""  # descrizione tattile
        self.descr_touch_night     = ""  # descrizione tattile notturna
        self.descr_taste           = ""  # descrizione del sapore
        self.descr_taste_night     = ""  # descrizione del sapore notturna
        self.descr_sixth           = ""  # descrizione del sesto senso
        self.descr_sixth_night     = ""  # descrizione del sesto senso notturna
        self.extras                = Extras()  # descrizioni extra
        self.icon                  = ""  # Nome dell'immagine icona che rappresenta l'entità
        self.icon_night            = ""  # Nome dell'immagine icona che rappresenta l'entità di notte
        self.purification_message  = ""  # Messaggio inviato a tutti nella stanza quando l'entità viene purificata a estratta dal gioco
        self.weight                = 0
        self.size                  = 0
        self.material_percentages  = MaterialPercentages()  # Materiali con cui è formata l'entità e relative percentuali
        self.value                 = 0
        self.position              = Element(POSITION.STAND)
        self.wear_mode             = Flags(PART.NONE)  # Parti che l'entità copre in un'altra entità
        self.under_weared          = None  # Indica l'entità indossa che si trova sotto a quest'entità, è una weakref
        self.birth_day             = 0   # Per gli oggetti la data di nascita significa quando sono stati costruiti
        self.birth_month           = Element(MONTH.NONE)
        self.age                   = 0
        self.flags                 = Flags(FLAG.NONE)
        self.behaviour             = None
        self.dialogs               = []
        self.affects               = []
        self.aggressivenesses      = []
        self.skills                = {}  # Elenco delle skill
        self.runes                 = {}  # Elenco delle rune
        self.languages             = {}  # Elenco delle lingue
       #self.clan                  = None  # Clan di cui l'entità fa parte
        self.previous_location      = None
        self.trust                 = Element(TRUST.PLAYER)
        self.killed_times          = 0    # Numero di volte in cui un'entità è stata uccisa o distrutta  # (TD) spostarla lato area
        self.max_global_quantity   = 0    # Numero di volte massimo che l'entità può essere inserita nel Mud  # (TD) questo è un attributo solo prototype
        self.reset_path            = ""   # Path identificativa del reset che ha inserito questa entità in gioco, serve al riavvio del mud per sapere quale entity reset utilizzare per repoppare
        self.extract_timeout       = None  # Struttura con le informazioni relative al dead time
        self.quantity              = 1  # (TD) questo attributo si dovrà trovare solo nella versione non prototype di Entity
        self.remains               = None  # Indica quale cadavere o oggetto rotto, alternativo a quello standard, utilizzare
        self.remains_night         = None  # Indica quale cadavere o oggetto rotto, alternativo a quello standard, utilizzare, ma solo di notte

        # Variabili più da mob-only:
        self.life                  = 0
        self.mana                  = 0
        self.vigour                = 0
        self.max_life              = self.life
        self.max_mana              = self.mana
        self.max_vigour            = self.vigour
        self.owner                 = None  # Chi o che cosa è in possesso di questa entità, è una weakref
        self.leader                = None  # Chi o che cosa sta comandando il gruppo (TD) forse questo sarà in una struttura a parte
        self.guide                 = None  # Chi o che cosa sta seguendo questa entità
       #self.followers             = []    # Coloro che stanno seguendo questa entità
        self.master                = None  # Chi o che cosa ha reso schiava quest'entità
       #self.slaves                = []    # Lista delle entità in possesso o schiave di questa entità
        self.mount                 = None  # Indica che entità sta montando
        self.shop                  = None  # Per i mob indica un negoziante, per gli oggetti indica un distributore
        self.walker                = None  # Indica che l'entità cammina in maniera particolare

        # Sottostrutture relative alle tipologie d'entità.
        # Questi attributi di solito si riferiscono più facilmente a degli
        # oggetti (ma non è detto!)
        self.entitype              = Element(ENTITYPE.NONE)  # Tipologia principale di entità
        self.container_type        = None  # Indica che l'entità funziona come un contenitore
        self.corpse_type           = None  # Indica che l'entità funziona come un cadavere
        self.door_type             = None  # Indica che l'entità funziona come una porta
        self.drink_type            = None  # Indica che l'entità funziona come una bevanda
        self.fishing_type          = None  # Indica che l'entità funziona come un pesce
        self.food_type             = None  # Indica che l'entità funziona come un cibo
        self.money_type            = None  # Indica che l'entità funziona come una moneta
        self.plant_type            = None  # Indica che l'entità funziona come una pianta
        self.portal_type           = None  # Indica che l'entità funziona come un portale
        self.readable_type         = None  # Indica che l'entità funziona come un libro
        self.seed_type             = None  # Indica che l'entità funziona come un seme
        self.wear_type             = None  # Indica che l'entità funziona come un abbigliamento
        self.weapon_type           = None  # Indica che l'entità funziona come un'arma
       #self.key_type              = None
       #self.keyring_type          = None

        # Variabili volatili:
        self.persistent_act          = None
        self.current_global_quantity = 0  # Quantità globale d'istanze di questo prototipo aggiunte nel gioco  # (TD) variabile solo prototipo
        self.waiting_inputs          = collections.deque([], 100) # Lista degli input inviati nonostante l'entità sia in wait, codesti input verranno inviati uno per volta quando lo stato di wait sparirà
        self.sended_inputs           = collections.deque([], 25)  # Lista degli input inviati dall'entità
        self.backsteps               = collections.deque([], 25)  # Lista delle locazioni cui l'entità si è trovata precedentemente
        self.location                = None # Indica quale stanza o entità contiene questa entità
        self.fights                  = []    # Combattimenti attuali
        self.guarding                = None # Entità per cui self è a guardia
        self.guarded_by              = None # Entità che sta proteggendo o prendendo cura di self
        self.players                 = []   # Personaggi che si trovano nell'inventario
        self.mobs                    = []   # Mob che si trovano nell'inventario
        self.items                   = []   # Oggetti che si trovano nell'inventario
        self.affect_infos            = []   # Informazioni agli affect applicati
        #self.upon                    = None # Entità su cui è posta self
        #self.below                   = None # Entità sotto cui è posta self
        #self.near                    = None # Entità vicino alla quale self si è posta o è stata posta
        #self.left                    = None # Entità che si trova alla sinistra rispetto a self
        #self.right                   = None # Entità che si trova alla destra rispetto a self
        #self.behind                  = None # Entità che si trova dietro a self
        self.wait_time               = 0    # Tempo di attesa prima che l'entità possa inviare un altro comando
        self.wait_state              = ""   # Frase che indica che si è in wait_state e perché
        self.game_request            = None # Richiesta relativa alla pagina web di gioco
        self.incognito               = False  # Opzione impostata dagli amministratori per non farsi vedere
        self.snoopers                = []   # Lista degli admin che stanno snoopando quest'entità
        self.retran                  = None # Ultima stanza prima di essere trasferiti ad un'altra
        self.regoto                  = None # Ultima stanza dove ci si è trasferiti con il goto
        self.interactions            = []  # Qui vengono elencati i giocatori che interagiscono con l'entità e per cui il player si aspetta che rimanga fermo (no behaviour di wandering) in attesa del termine dell'interazione
        self.gamescripts             = {}   # Dizionario delle differenti funzioni di gamescript
        self.action_in_progress      = None # Informazioni relative alle azioni rpg che richiedono tempo per essere eseguite
        self.deferred_purification   = None # Deferred relativa alla decomposizione, per esempio di semi caduti dalle piante
        self.deferred_wait           = None # Deferred relativa all'attesa di una determinato comando interattivo
        self.deferred_repop          = None
        self.repop_later             = None # Struttura di repop che viene salvata durante il reset e che si attiva quando l'entità viene estratta dal gioco
        self.last_movement           = None # Indica il momento in cui è stato inviata una direzione, serve per vedere se si sta correndo
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s" % (super(ProtoEntity, self).__repr__(), self.code)
    #- Fine Metodo -

    def get_error_message(self):
        if self.level <= 0 or self.level > config.max_level:
            return "level errato: %d" % self.level
        elif self.sex.get_error_message(SEX, "sex") != "":
            return self.sex.get_error_message(SEX, "sex")
        elif not self.name:
            return "name non valido: %s" % self.short
        elif not self.short and not self.IS_PLAYER:
            return "short non valida: %r" % self.short
        # Se la short inizia con una lettera maiuscola non va bene, viene
        # eseguito un controllo semi-intelligente per evitare falsi positivi
        # con nomi propri nelle short
        elif self.short and remove_colors(self.short)[0].isupper() and clean_string(self.short)[0] != remove_little_words(self.short)[0]:
            #return "short non deve iniziare con la maiuscola a meno che non sia voluto: %s" % self.short
            return ""
        elif self.short_night and remove_colors(self.short_night)[0].isupper() and clean_string(self.short_night)[0] != remove_little_words(self.short_night)[0]:
            #return "short_night non deve iniziare con la maiuscola a meno che non sia voluto: %s" % self.short_night
            return ""
        # (TD) sarà bocciato il sistema nomi, quindi vincono le short o i nomi?
        #elif self.name and remove_colors(self.name)[0].isupper() and clean_string(self.name)[0] != remove_little_words(self.name)[0]:
        #    return "name non deve iniziare con la maiuscola a meno che non sia voluto: %s" % self.name
        elif self.short and self.short[-1] == ".":
            #return "short con un punto finale: %s" % self.short
            return ""
        elif self.short_night and self.short_night[-1] == ".":
            #return "short_night con un punto finale: %s" % self.short_night
            return ""
        elif self.name and self.name[-1] == ".":
            #return "name con un punto finale: %s" % self.name
            return ""
        elif self.long and "$N" not in self.long:
            return "long senza il tag $N: %s" % self.long
        elif not self.descr and not self.IS_PLAYER:
            return "descr non valida: %r" % self.descr
        elif self.extras.get_error_message() != "":
            return self.extras.get_error_message()
        elif self.purification_message and "$n" not in self.purification_message:
            return "purification_message senza il tag di act $n: %s" % self.purification_message
        elif self.weight < 0:
            return "Weight minore di 0: %d" % self.weight
        elif self.size < 0:
            return "Size minore di zero: %d" % self.size
        elif self.weight == 0 and self.size == 0:
            return "Un'entità non può avere sia Weight che Size a zero"
        elif self.material_percentages.get_error_message(self) != "":
            return self.material_percentages.get_error_message(self)
        elif self.age < 0:
            return "Age mancante per l'entità: %d" % self.age
        elif self.position.get_error_message(POSITION, "position") != "":
            msg = self.position.get_error_message(POSITION, "position")
        # (TD) il controllo alle Knowledges lo farò poi visto che è abb
        # complesso come dizionario, contiene chiavi di tipo mischiato
        elif self.flags.get_error_message(FLAG, "flags") != "":
            return self.flags.get_error_message(FLAG, "flags")
        elif get_error_message_affects(self.affects) != "":
            return get_error_message_affects(self.affects)
        elif self.guarding and self.guarding.guarded_by != self:
            return "self e guarding.guarded_by (%s) non sono uguali" % self.guarding.guarded_by.code
        #elif self.owner() and not self in self.owner().slaves:
        #    return "self, nonostante sia schiava, non si trova tra gli schiavi del proprio padrone (%s)" % self.owner().code
        elif self.container_type and self.container_type.get_error_message(self) != "":
            return self.container_type.get_error_message(self)
        elif self.corpse_type and self.corpse_type.get_error_message(self) != "":
            return self.corpse_type.get_error_message(self)
        elif self.door_type and self.door_type.get_error_message(self) != "":
            return self.door_type.get_error_message(self)
        elif self.drink_type and self.drink_type.get_error_message(self) != "":
            return self.drink_type.get_error_message(self)
        elif self.food_type and self.food_type.get_error_message(self) != "":
            return self.food_type.get_error_message(self)
        elif self.plant_type and self.plant_type.get_error_message(self) != "":
            return self.plant_type.get_error_message(self)
        elif self.portal_type and self.portal_type.get_error_message(self) != "":
            return self.portal_type.get_error_message(self)
        elif self.readable_type and self.readable_type.get_error_message(self) != "":
            return self.readable_type.get_error_message(self)
        elif self.seed_type and self.seed_type.get_error_message(self) != "":
            return self.seed_type.get_error_message(self)
        elif self.weapon_type and self.weapon_type.get_error_message(self) != "":
            return self.weapon_type.get_error_message(self)
        elif self.wear_type and self.wear_type.get_error_message(self) != "":
            return self.wear_type.get_error_message(self)
        elif self.walker and self.walker.get_error_message(self) != "":
            return self.walker.get_error_message(self)
        elif self.extract_timeout and self.extract_timeout.get_error_message(self) != "":
            return self.extract_timeout.get_error_message(self)
        elif not self.IS_PLAYER and self.shop and self.shop.get_error_message() != "":
            return self.shop.get_error_message()
        elif self.aggressivenesses and FLAG.AGGRESSIVE not in self.flags:
            return "aggressivenesses impostata ma senza la flag FLAG.AGGRESSIVE non funziona"

        return ""
    #- Fine Metodo -

    def get_pedantic_messages(self):
        messages = []

        if not self.long and "@empty_long" not in self.comment:
            messages.append("long non è stata scritta, sarebbe meglio inserirla piuttosto che avere il solito: 'è qui.' a meno di casi particolari. (@empty_long)")

        if not self.descr_night and "@empty_descr_night" not in self.comment:
            messages.append("descr_night non è stata scritta, da ignorare nel qual caso nella stanza non sussistano grossi cambiamenti di luce o altro, tra giorno e notte. (@empty_descr_night)")

        if not self.descr_hearing and not self.descr_smell and not self.descr_touch and not self.descr_taste and not self.descr_sixth and "@empty_senses" not in self.comment:
            messages.append("nessuna descrizione sensoriale oltre quella visiva, sarebbe meglio scriverne almeno una. (@empty_senses)")

        # E' lecito non avere delle extra per le entità, diversamente dalle stanze

        descrs = ("descr", "descr_night", "descr_hearing", "descr_hearing_night", "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night", "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night")
        for descr in descrs:
            length = len(remove_colors(getattr(self, descr)))
            if length > config.max_google_translate and "@%s_too_long" % descr not in self.comment:
                messages.append("%s è più lunga di %d caratteri: %d (@%s_too_long)" % (descr, config.max_google_translate, length, descr))

        return messages
    #- Fine Metodo -

    #- Metodi di inizializzazione di alcuni attributi --------------------------

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
            self.code = code
            self.prototype = database["proto_" + self.ACCESS_ATTR][code.split("#")[0]]
        else:
            self.code = "%s#%s" % (code, id(self))
            self.prototype = database["proto_" + self.ACCESS_ATTR][code]

        if old_code and old_code in database[self.ACCESS_ATTR]:
            del(database[self.ACCESS_ATTR][old_code])
            database[self.ACCESS_ATTR][self.code] = self
    #- Fine Metodo -

    def after_copy_existing_attributes(self):
        self.gamescripts = import_instance_gamescripts(self)

        # Prepara la cache per i valori di behaviour
        if self.behaviour:
            self.cache_behaviour("behaviour")
    #- Fine Metodo -

    #- Metodi getter degli attributi ------------------------------------------

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
            entity_tables = self.ENTITY_TABLES

        if use_reversed:
            for entity_table in entity_tables:
                for content in reversed(getattr(self, entity_table)):
                    yield content
        else:
            for entity_table in entity_tables:
                for content in getattr(self, entity_table):
                    yield content
    #- Fine Metodo -

    def _iter_variant_entities(self, variant, entity_tables=None, use_can_see=False):
        """
        Itera tutte le entità contenute e volute.
        Non è ricorsiva per ragioni prestazionali.
        Qui al metodo iter_contains non bisogna assolutamente utilizzare il
        parametro use_reversed per evitare di mischiare senza senso la lista
        generata e inficiare così l'eventuale utilizzo dell'use_reversed
        'superiore' che serve sostanzialmente ad evitare dei buchi se la lista
        iterata viene modificata rimuovendo elementi.
        E' importante che avvenga questa ricerca stratificata, e non ricorsiva,
        tramite la pop: questo per come viene gestita la chiamata a
        iter_only_interactable_entities nel modulo find_entity.
        """
        if variant not in ("all", "opened", "openable", "interactable"):
            log.bug("variant non è un parametro valido: %r" % variant)
            yield None

        # ---------------------------------------------------------------------

        contained_entities = []
        target = self

        while True:
            for contained_entity in target.iter_contains(entity_tables=entity_tables):
                if use_can_see and not self.can_see(contained_entity):
                    continue
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

    def iter_all_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera in tutte le entità contenute.
        """
        if use_reversed:
            return reversed(list(self._iter_variant_entities("all", entity_tables=entity_tables, use_can_see=use_can_see)))
        else:
            return self._iter_variant_entities("all", entity_tables=entity_tables, use_can_see=use_can_see)
    #- Fine Metodo -

    def iter_through_opened_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera tutte le entità contenute in tutti i contenitori trovati aperti.
        """
        if use_reversed:
            return reversed(list(self._iter_variant_entities("opened", entity_tables=entity_tables, use_can_see=use_can_see)))
        else:
            return self._iter_variant_entities("opened", entity_tables=entity_tables, use_can_see=use_can_see)
    #- Fine Metodo -

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

    def iter_only_interactable_entities(self, entity_tables=None, use_reversed=False, use_can_see=False):
        """
        Itera tutte le entità contenute in tutti i contenitori trovati aperti
        e che abbiano la FLAG.INTERACTABLE_FROM_OUTSIDE.
        """
        if use_reversed:
            interactable_entities = reversed(list(self._iter_variant_entities("interactable", entity_tables=entity_tables, use_can_see=use_can_see)))
        else:
            interactable_entities = self._iter_variant_entities("interactable", entity_tables=entity_tables, use_can_see=use_can_see)

        # Bisogna eseguire un filtraggio delle entità perché alcune di quelle
        # ricavate dalla variant sono dei contenitori
        for en in interactable_entities:
            if FLAG.INTERACTABLE_FROM_OUTSIDE in en.flags:
                yield en
    #- Fine Metodo -

    def get_area_code(self):
        # Questo metodo viene implementato sia nella classe Mob che in Item.
        raise NotImplementedError
    #- Fine Metodo -

    def get_name(self, looker=None):
        """
        Ritorna il nome dell'entità.
        Serve per il sistema di presentazione, se l'entità non è conosciuta a
        chi la incontra non visualizza il nome reale ma una mini-descrizione
        generica del soggetto.
        """
        # Quelli della stessa razza vedono il name del cadavere e non la short
        if looker and self.entitype == ENTITYPE.CORPSE and looker.race == self.race:
            return self.name

        # (TD) manca il ritorno di self.name se l'entità è conosciuta dal looker
        if self.IS_PLAYER:
            if "[" in self.name:
                name = self.name
            else:
                name = "[white]%s[close]" % self.name
        else:
            if calendar.is_day() or not self.short_night:
                name = self.short
            else:
                name = self.short_night

        if looker:
            if "$" in name:
                name = looker.replace_act_tags(name, target=self)
            if "$" in name:
                name = looker.replace_act_tags_name(name, looker=looker, target=self)

        return name
    #- Fine Metodo -

    def get_formatted_name(self, looker=None, location=None, look_translation="", use_number_argument=True, show_icon=True):
        if not look_translation:
            if looker:
                look_translation = translate_input(looker, "look", "en")
            else:
                log.bug("Impossibile ricavare automaticamente look_translation senza looker valido: %r" % looker)
                look_translation = "guarda"

        name = self.get_name(looker)
        if not name:
            log.bug("Non è stato possibile ricavare un nome valido per %s con looker %s" % (self.code, looker.code))
            return ""

        if looker and location and location.location != looker.location:
            return color_first_upper(name)

        location_first_keyword = ""
        if location and location != looker:
            location_first_keyword = location.get_first_keyword(looker=looker)
            if use_number_argument and not location.IS_ROOM:
                location_first_keyword = " " + location.get_numbered_keyword(looker=looker, first_keyword=location_first_keyword)

        first_keyword = self.get_first_keyword(looker=looker)
        if use_number_argument:
            first_keyword = self.get_numbered_keyword(looker=looker, first_keyword=first_keyword)

        javascript = "javascript:parent.sendInput('%s %s%s');" % (
            look_translation, first_keyword, location_first_keyword)

        if show_icon:
            return '''%s<a href="%s">%s</a>''' % (create_icon(self.get_icon()), javascript, color_first_upper(name))
        else:
            return '''<a href="%s">%s</a>''' % (javascript, color_first_upper(name))
    #- Fine Metodo -

    def get_numbered_keyword(self, looker=None, first_keyword=""):
        """
        Ricava l'argomento numerico se è necessario, così non c'è pericolo
        che si guardi sempre la prima entità con la stessa keyword.
        """
        if self.IS_PLAYER:
            return self.code

        if not first_keyword:
            first_keyword = self.get_first_keyword(looker=looker)

        if self.location:
            location_entities = self.location.get_list_of_entities(looker, use_number_argument=False)
        else:
            location_entities = []

        counter = 1
        for location_entity in location_entities:
            if location_entity[INSTANCE].IS_PLAYER:
                continue
            if self == location_entity[INSTANCE] or self in location_entity[ENTITIES]:
                break
            if first_keyword in multiple_arguments(location_entity[INSTANCE].get_keywords_attr(looker)):
                counter += 1 * location_entity[COUNTER]

        if counter > 1:
            return "%d.%s" % (counter, first_keyword)
        else:
            return first_keyword
    #- Fine Metodo -

    def get_keywords_attr(self, looker=None):
        """
        Ritorna la lista delle keywords in linea con il metodo get_name, cioè
        ritorna le keywords relative al name, short o short_night a seconda
        del looker, per il sistema di presentazione, e del giorno/notte.
        """
        if looker and self.entitype == ENTITYPE.CORPSE and looker.race == self.race:
            # (TD) Ci sarà bisogno di un metodo apposito, uno per la
            # ProtoEntity, l'altro per la Entity
            if self.__class__.__name__ in ("ProtoMob", "ProtoItem"):
                keywords_attr = create_keywords(self.name, self)
            else:
                keywords_attr = self.keywords_name
        # Per il player bisogna sempre ricalcolare le keywords perché la loro
        # short è dinamica
        elif self.IS_PLAYER:
            keywords_attr = create_keywords(self.get_name(looker), self)
        # (TD) manca il self.keywords_name se l'entità è conosciuta dal looker
        elif calendar.is_day() or not self.short_night:
            if self.__class__.__name__ in ("ProtoMob", "ProtoItem"):
                keywords_attr = create_keywords(self.short, self)
            else:
                keywords_attr = self.keywords_short
        else:
            if self.__class__.__name__ in ("ProtoMob", "ProtoItem"):
                keywords_attr = create_keywords(self.short_night, self)
            else:
                keywords_attr = self.keywords_short_night

        # Non c'è bisogno di eseguire il replace del tag di act "$O" perché
        # questi viene già eseguito nella funzione create_keywords
        if looker and "$o" in keywords_attr:
            keywords_attr = keywords_attr.replace("$o", grammar_gender(looker))

        return keywords_attr
    #- Fine Metodo -

    def get_first_keyword(self, looker=None):
        """
        Scorciatoia per diminuire la diffusione di codice boilerplate.
        """
        keyword_attr = self.get_keywords_attr(looker=looker)
        if not keyword_attr:    
            log.bug("keyword_attr non è valido per %r" % self)
            return ""

        return multiple_arguments(keyword_attr)[0]
    #- Fine Metodo -

    def get_keywords(self, looker=None):
        """
        Scorciatoia per diminuire la diffusione di codice boilerplate.
        """
        return multiple_arguments(self.get_keywords_attr(looker))
    #- Fine Metodo -

    def get_icon(self):
        icon = ""
        if calendar.is_night():
            icon = self.icon_night

        if not icon and self.icon:
            return self.icon
        elif self.IS_MOB and self.race.icon:
            return self.race.icon
        elif self.IS_ITEM and self.entitype.icon:
            return self.entitype.icon

        return ""
    #- Fine Metodo -

    def get_long(self, looker, look_translation, use_number_argument=True):
        """
        Ritorna lo stato attuale dell'entità, se questa non si trova in uno
        stato particolare allora ritorna l'attributo long.
        """
        if not looker:
            log.bug("looker non è un parametro valido: %r" % looker)
            return ""

        if not look_translation:
            log.bug("look_translation non è un parametro valido: %r" % look_translation)
            return ""

        # ---------------------------------------------------------------------

        if self.persistent_act:
            message = self.persistent_act.get_persistent_message(self, looker, use_number_argument)
            if message:
                return message

        first_keyword = self.get_first_keyword(looker=looker)
        if use_number_argument:
            first_keyword = self.get_numbered_keyword(looker=looker, first_keyword=first_keyword)

        name = color_first_upper(self.get_name(looker))
        if self.corpse_type:
            long = self.corpse_type.get_long()
        elif self.long and (calendar.is_day() or not self.long_night):
            long = self.long
        elif self.long_night and calendar.is_night():
            long = self.long_night
        else:
            # (TD) forse in futuro la long non sarà più opzionale quindi questa
            # parte non servirà più (da pensare se rendere però obbligatoria la long)
            if self.IS_ITEM:
                if looker.IS_ITEM:
                    long = "%s si trova per terra." % name
                else:
                    long = "%s è ai tuoi $feet." % name
            else:
                if looker.IS_ITEM:
                    long = "%s è qui." % name
                else:
                    long = "%s è qui." % name

        if "$i" not in long and "$I" not in long and (self.container_type and CONTAINER.CLOSED not in self.container_type.flags):
            interactable_entities = list(self.iter_only_interactable_entities(use_can_see=True))
            if interactable_entities:
                if len(interactable_entities) == 1:
                    long = add_to_phrase(long, " in cui v'è %s" % interactable_entities[0].get_name(looker=looker), ".")
                elif len(interactable_entities) > 1:
                    long = add_to_phrase(long, " in cui vi sono %s" % pretty_list([en.get_name(looker=looker) for en in interactable_entities]), ".")

        if self.position != POSITION.STAND:
            posture = color_first_lower(self.position.description)
            long = add_to_phrase(long, ", " + posture, ".")

        if MIML_SEPARATOR in long:
            long = self.parse_miml(long, looker)
        if "$" in long:
            long = looker.replace_act_tags(long, target=self)
        if "$" in long:
            long = looker.replace_act_tags_name(long, looker=looker, target=self)

        # Aggiunge eventuali informazioni di stato
        if self.IS_ITEM and self.life < self.max_life:
            long = add_to_phrase(long, ", " + self.get_condition(), ".")
        elif looker and self.is_fighting(with_him=looker):
            long = add_to_phrase(long, ", sta combattendo contro di te", "!")

        # Mostra i giocatori in link-dead
        if self.IS_PLAYER and not self.game_request:
            long += " [cyan](scollegato)[close]"

        long = put_final_dot(long)

        # È normale che non venga trovato il nome nella long, ciò capita quando
        # viene restringata la long senza inserirvi il tag di act $n, cosa un
        # po' erronea ma, se voluta, accettabile
        index = long.lower().find(name.lower())
        if index == -1:
            return long
        else:
            # Ritorna la long con formattato il nome per un click rapido che
            # invia il comando di look sull'entità
            return "%s%s%s%s%s" % (
                color_first_upper(long[ : index]) if long[ : index] else "",
                '''<a href="javascript:parent.sendInput('%s %s');">''' % (look_translation, first_keyword),
                long[index : index + len(name)],
                "</a>",
                long[index + len(name) : ])
    #- Fine Metodo -

    def get_descr(self, type="", looker=None):
        """
        Ritorna la descrizione dell'entità.
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
            if not type and not self.IS_PLAYER:
                log.bug("descr non valida con type a %s per entità %s: %r" % (type, self.code, descr))
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

    # (TD) Fare la condition anche per i mob
    def get_condition(self):
        percent = get_percent(self.life, self.max_life)

        if self.entitype == ENTITYPE.WEAPON:
            if   percent >= 100: return "[white]in superbe condizioni[close]"
            elif percent >= 92:  return "in condizioni eccellenti"
            elif percent >= 84:  return "in ottime condizioni"
            elif percent >= 76:  return "in buone condizioni"
            elif percent >= 68:  return "sembra lievemente incrinat%s" % grammar_gender(self)
            elif percent >= 60:  return "sembra un po' deformat%s" % grammar_gender(self)
            elif percent >= 52:  return "ha bisogno di una riparazione"
            elif percent >= 44:  return "ha urgente bisogno di riparazioni"
            elif percent >= 36:  return "è in condizioni disastrose"
            elif percent >= 28:  return "è quasi irriconoscibile"
            elif percent >= 20:  return "è ormai un oggetto senza valore"
            elif percent >= 12:  return "è praticamente inutilizzabile"
            else:                return "[darkslategray]è ormai completamente distrutt%s[close]" % grammar_gender(self)

        if   percent >= 100: return "[white]in perfetto stato[close]"
        elif percent >= 90:  return "quasi perfett%s" % grammar_gender(self)
        elif percent >= 80:  return "in ottime condizioni"
        elif percent >= 70:  return "in buone condizioni"
        elif percent >= 60:  return "un po' rovinat%s" % grammar_gender(self)
        elif percent >= 50:  return "rovinat%s" % grammar_gender(self)
        elif percent >= 40:  return "in condizioni mediocri"
        elif percent >= 30:  return "estremamente rovinat%s" % grammar_gender(self)
        elif percent >= 20:  return "pien%s di crepe" % grammar_gender(self)
        elif percent >= 10:  return "senza valore"
        else:                return "[darkslategray]completamente rott%s[close]" % grammar_gender(self)

        # Stato del cibo:
#		if		( dam >= 10 )	strcat( buf, "sembra una vera delizia." );
#		else if ( dam ==  9 )	strcat( buf, "è come un frutto appena colto." );
#		else if ( dam ==  8 )	strcat( buf, "sembra ottimo." );
#		else if ( dam ==  7 )	strcat( buf, "sembra davvero buono." );
#		else if ( dam ==  6 )	strcat( buf, "sembra buono." );
#		else if ( dam ==  5 )	strcat( buf, "sembra un po' avvizzito." );
#		else if ( dam ==  4 )	strcat( buf, "è un pò avvizzito.." );
#		else if ( dam ==  3 )	strcat( buf, "puzza un pò.." );
#		else if ( dam ==  2 )	strcat( buf, "puzza di muffa.." );
#		else if ( dam ==  1 )	strcat( buf, "ha un odore rivoltante!" );
#		else if ( dam <=  0 )	strcat( buf, "Bleah! Pieno di vermi!" );

        # Cibi cotti:
#		if		( dam >= 3 )	strcat( buf, "un ammasso bruciacchiato!" );
#		else if ( dam == 2 )	strcat( buf, "cotto alla brace."		 );
#		else if ( dam == 1 )	strcat( buf, "cotto a puntino."			 );
#		else					strcat( buf, "crudo."					 );

        # Stato dei cadaveri
#		  default:
#			send_to_char( ch, "Questo cadavere è stato ucciso di recente.\r\n" );
#			break;
#		  case 4:
#			send_to_char( ch, "Questo cadavere è stato ucciso da poco tempo.\r\n" );
#			break;
#		  case 3:
#			send_to_char( ch, "Percepisco un terribile tanfo si solleva dal cadavere che irrigidito dal rigor mortis è riverso in terra.\r\n" );
#			break;
#		  case 2:
#			send_to_char( ch, "Vermi e insetti hanno depredato d'ogni viscera questo cadavere, irriconoscibile.\r\n" );
#			break;
#		  case 1:
#		  case 0:
#			send_to_char( ch, "Di quello che era un corpo qui rimangono solo poche ossa, i vermi hanno preso il resto.\r\n" );
#			break;
    #- Fine Metodo -

    def get_race(self):
        # (TD)
        return self.race
    #- Fine Metodo -

    def get_body_parts(self):
        import bodies.human as human_body

        if self.IS_ITEM:
            return human_body.parts_left_handed

        if self.hand == HAND.LEFT:
            return human_body.parts_left_handed
        else:
            return human_body.parts_right_handed

        # (TD) Meglio di un import sarebbe una struttura nel database in
        # maniera tale da chiamarla subito
        #body_code = self.race.get_mini_code()
        #return getattr(bodies, body_code).parts
    #- Fine Metodo -

    def get_holded_entity(self):
        for contained in self.iter_contains():
            if PART.HOLD in contained.wear_mode:
                return contained
        return None
    #- Fine Metodo -

    def get_wielded_entity(self):
        for contained in self.iter_contains():
            if PART.WIELD in contained.wear_mode:
                return contained
        return None
    #- Fine Metodo -

    def get_age(self):
        # (TD)
        return self.age
    #- Fine Metodo -

    def get_weight(self):
        """
        Ritorna il peso dell'entità, esso varia a seconda di quello che ha
        mangiato.
        Il più delle volte bisogna utilizzare questo metodo al posto
        dell'attributo weight dell'entità.
        """
        weight = self.weight

        for ingested in self.iter_all_entities():
            if FLAG.INGESTED in ingested.flags:
                weight += ingested.weight * ingested.quantity

        return weight
    #- Fine Metodo -

    def get_carried_weight(self):
        """
        Ritorna il peso totale che l'entità sta trasportando.
        """
        carried_weight = 0

        for carried in self.iter_all_entities():
            if FLAG.INGESTED not in carried.flags:
                carried_weight += carried.weight * carried.quantity

        return carried_weight
    #- Fine Metodo -

    def get_equipped_weight(self):
        """
        Ritorna il peso totale che l'entità sta equipaggiando.
        """
        equipped_weight = 0

        for equipped in self.iter_all_entities():
            if equipped.wear_mode and FLAG.INGESTED not in equipped.flags:
                equipped_weight += equipped.weight * equipped.quantity

        return equipped_weight
    #- Fine Metodo -

    def get_total_weight(self):
        """
        Ritorna il peso totale dell'entità.
        """
        return (self.get_weight() * self.quantity) + (self.get_carried_weight() * self.quantity)
    #- Fine Metodo -

    def can_carry_weight(self):
        """
        Ritorna il valore in grammi totale trasportabile dall'entità.
        """
        if self.container_type:
            return self.container_type.max_weight
        elif self.IS_ITEM:
            # (TD) è giusto per farlo andare
            return self.weight * 10
        else:
            # (TD) Il moltiplicatore di base cambiarlo a seconda della classe
            # per guerrieri 10, per maghi 8
            return int(9000 * math.log(self.max_vigour))
    #- Fine Metodo -

    def can_carry_target(self, target, quantity=0):
        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return False

        if quantity < 0:
            log.bug("quantity è un valore negativo: %d" % quantity)
            return False

        # ---------------------------------------------------------------------

        if quantity == 0:
            quantity = target.quantity

        if (target.weight * quantity) + self.get_carried_weight() <= self.can_carry_weight():
            return True
        else:
            return False
    #- Fine Metodo -

    def have_circle_follow(self, target):
        if not target:
            log.bug("target non è un parametro valido: %r" % target)
            return False

        # ---------------------------------------------------------------------

        while target.guide:
            if target.guide == self:
                return True
            target = target.guide

        return False
    #- Fine Metodo -

    def get_current_light(self):
        """
        Luce totale che irradiata dall'entità.
        """
        current_light = 0

        # (TD)

        return current_light
    #- Fine Metodo -

    def get_followers_here(self):
        followers = []

        for content in self.location.iter_contains():
            if content != self and content.guide == self:
                followers.append(content)

        return followers
    #- Fine Metodo -

    def get_voice_potence(self, channel):
        """
        Calcola la potenza della voce dell'entità.
        """
        if not channel:
            log.bug("channel non è un parametro valido: %r" % channel)
            return

        # ---------------------------------------------------------------------

        if self.IS_ITEM:
            voice_potence = 50
        else:
            voice_potence = self.voice_potence
            voice_potence += self.race.voice_potence

            # Modifica a seconda delle conoscenze delle skill legate ai canali rpg
            if channel == CHANNEL.THUNDERING and "thundering_voice" in self.skills:
                voice_potence += self.skills["thundering_voice"] / 5
            elif channel == CHANNEL.HISSING and "hissing_voice" in self.skills:
                voice_potence -= self.skills["hissing_voice"] / 5

        # Modifica la potenza a seconda del canale passato di una
        # certa percentuale
        if channel == CHANNEL.MURMUR:
            voice_potence -= voice_potence * 20 / 100
        elif channel == CHANNEL.WHISPER:
            voice_potence -= voice_potence * 10 / 100
        elif channel == CHANNEL.YELL:
            voice_potence += voice_potence * 10 / 100
        elif channel == CHANNEL.SHOUT:
            voice_potence += voice_potence * 20 / 100

        return voice_potence
    #- Fine Metodo -

    # - Metodi di update ------------------------------------------------------

    # (TD) fame e sete

    # -------------------------------------------------------------------------

    def dies(self):
        raise NotImplementedError
    #- Fine Metodo -

    def send_output(self, message, break_line=True, replace_linefeeds=True, avoid_snoop=False, avoid_log=False):
        """
        Invia dell'output alla pagina web dell'output di gioco.
        """
        if not message:
            log.bug("message non è un parametro valido: %r" % message)
            return

        # ---------------------------------------------------------------------

        if "no_send" in message.lower():
            return

        # Se un'entità non è un giocatore e non è snoopata evita tutto il resto
        # della funzione
        if not self.game_request and not self.snoopers:
            return

        # Se si vuole inviare solo un a capo disabilita il break line
        if message == "\n":
            break_line = False

        if "$" in message:
            message = self.replace_act_tags(message)
        if "$" in message:
            message = self.replace_act_tags_name(message, looker=self, aux1=self.location)

        if "[" in message:
            message = convert_colors(message)

        if replace_linefeeds and "\n" in message:
            message = message.replace("\n", "<br>")

        if break_line:
            message += "<br>"

        if message != "\n" and message != "<br>":
            for snooper in self.snoopers:
                snooper.send_output('''<table class="mud" border="1"><tr><td>%s:</td><td>%s</td></tr>''' % (
                    self.get_name(snooper), message))

        # Solo chi ha una connessione al gioco può ricevere il messaggio
        if self.game_request:
            comet_option = "None"
            if self.account:
                comet_option = "Comet" if OPTION.COMET in self.account.options else "Ajax"

            conn = self.get_conn()
            if conn:
                if self.account and OPTION.COMET in self.account.options:
                    if conn.get_browser() in IFRAME_BROWSERS:
                        self.game_request.write(message)
                    else:
                        try:
                            self.game_request.write(message + OUTPUT_END_TAG)
                        except RuntimeError:
                            # È normale visto il redirect poco pulito della
                            # seconda pagina di creazione del personaggio
                            # verso la pagina di gioco
                            pass
                else:
                    # Se il pg ha quittato allora evita di riempire
                    # ulteriormente il buffer
                    if conn.stop_buffering:
                        return
                    conn.buffer += message
                    # Gestisce il caso in cui il buffer sia troppo grande
                    if len(conn.buffer) > config.max_output_buffer:
                        message = "Connessione %s con secondi di idle %d che ha un buffer troppo grande: %d (buffer stampato nel file overbuffer.log)" % (
                            conn.get_id(), conn.player.idle_seconds if conn.player else -1, len(conn.buffer))
                        log.write_overbuffer(conn.buffer)
                        if avoid_log:
                            print message
                        else:
                            log.conn(message)
                        conn.buffer = ""
                        if conn.player:
                            conn.player.exit_from_game(True)
                        else:
                            log.bug("Inatteso player non valido per la connessione: %s (%s)" % (conn.get_id(), comet_option))
                        return
            else:
                # Non invia il messaggio ai giocatori nel mud altrimenti crea ricorsione
                log.bug("conn non valido con game_request valida per il player %s (%s)" % (
                    self.code, comet_option), send_output=False)

            if config.log_player_output:
                log.html_output(message, self)
    #- Fine Metodo -

    def send_prompt(self, break_line=False, show_opponent=True):
        """
        Invia il prompt all'entità che ha la possibilità di connettersi
        con la pagina di gioco del sito.
        """
        if not self.game_request:
            return

        if self.account and OPTION.COMPACT in self.account.options:
            prompt = []
        else:
            prompt = ["\n"]

        # Se il nome del giocatore non è colorato lo evidenzia in bianco
        if "[" not in self.name:
            prompt.append("&lt;[white]%s[close]:" % self.name)
        else:
            prompt.append("&lt;%s:" % self.name)

        for points in POINTS.elements:
            if hasattr(self, "account") and self.account and OPTION.LESS_COLORS in self.account.options:
                points_name = remove_colors(str(points))
            else:
                points_name = str(points)
            prompt.append(" %s %s" % (self.get_actual_and_max_points(points), points_name))

        if show_opponent:
            opponent = self.get_opponent()
            if opponent:
                prompt.append(" %s: [white]%d[close]%%" % (
                    color_first_upper(opponent.get_name(self)),
                    get_percent(opponent.life, opponent.max_life)))

        prompt.append("&gt;")

        self.send_output("".join(prompt), break_line)
    #- Fine Metodo -

    def get_actual_and_max_points(self, points):
        if not points:
            log.bug("points non è un parametro valido: %s" % points)
            return ""

        # ---------------------------------------------------------------------

        percent = get_percent(getattr(self, points.attr_name), getattr(self, "max_" + points.attr_name))
        basic_color = get_first_color(str(points))
        color = basic_color
        if percent < 25:
            color = points.color_25
        elif percent < 50:
            color = points.color_50

        return "%s%d%s/%s%s[close]" % (
            color, getattr(self, points.attr_name), "[close]" if color else "",
            basic_color, getattr(self, "max_" + points.attr_name))
    #- Fine Metodo -

    def send_to_admin(self, message, break_line=True):
        """
        È una combinazione delle chiamate a format_for_admin e a send_output.
        """
        if not message:
            log.bug("message non è un parametro valido: %r" % message)
            return ""

        # ---------------------------------------------------------------------

        # I messaggi vengono comunque inviati a tutti i mob in maniera tale da
        # poter essere letti dagli admin tramite lo snoop
        if self.IS_PLAYER and self.trust <= TRUST.PLAYER:
            log.bug("Non bisogna inviare messaggi di admin ai giocatori senza trust: %s" % self.name)
            return ""

        formatted_message = format_for_admin(message)
        if not formatted_message:
            log.bug("formatted_message non è un messaggio valido: %r" % formatted_message)
            return

        self.send_output(formatted_message, break_line=break_line)
    #- Fine Metodo -

    # (TD) da inserire in Location
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

    # -------------------------------------------------------------------------

    def skin_colorize(self, argument):
        raise NotImplementedError
    #- Fine Metodo -

    def eye_colorize(self, argument):
        raise NotImplementedError
    #- Fine Metodo -

    def hair_colorize(self, argument):
        raise NotImplementedError
    #- Fine Metodo -

    #- Metodi relativi al combattimento ----------------------------------------

    is_fighting = is_fighting
    get_fight = get_fight
    get_opponent = get_opponent
    check_aggressiveness = check_aggressiveness
    can_aggress = can_aggress

    # (TD) è un metodo opinabile.. che conflitta concettualmente con alcuni
    # del fight, da rivedere; viene utilizzato per il danno da fame e da sete
    def damage(self, offender, value, type):
        """
        Infligge un tot di danno a l'entità dell'instanza.
        Ritorna True se l'entità è ancora viva dopo il danno.
        """
        if not offender:
            log.bug("offender non è un parametro valido: %r" % offender)
            return True

        if not value and value != 0:
            log.bug("value non è un parametro valido: %r" % value)
            return True

        if not type:
            log.bug("type non è un parametro valido: %r" % type)
            return True

        # ---------------------------------------------------------------------

        if value == 0:
            return

        self.life = max(0, self.life - value)
        if self.life > 0:
            return True
        else:
            return False
    #- Fine Metodo -

    def make_remains(self, auto_loot=False):
        # Nel qual caso l'entità abbia la flag che eviti la creazione del
        # cadavere allora passa subito all'inserimento del contenuto nella
        # propria locazione
        if FLAG.NO_REMAINS in self.flags:
            for something in self.iter_contains(use_reversed=True):
                if self.IS_PLAYER and FLAG.STAY_ON_DEATH in something.flags:
                    continue
                something = something.from_location(something.quantity, use_repop=False)
                something.to_location(self.location)
                if FLAG.INGESTED in something.flags:
                    something.stop_digestion(remove_flag=False)
            return None, True

        # Sceglie il codice adatto alla creazione dell'entità ormai cadavere
        if calendar.is_night() and self.remains_night:
            substitute = False
            use_repop = False
            code = self.remains_night.code
        elif self.remains:
            substitute = False
            use_repop = False
            code = self.remains.code
        else:
            substitute = True
            use_repop = True
            if self.IS_ITEM:
                entitype = self.entitype.get_mini_code()
                code = "rip_item_broken-%s" % entitype
                if code not in database["proto_items"]:
                    code = "rip_item_broken-something"
            else:
                sex  = self.sex.get_mini_code()
                race = self.race.get_mini_code()
                code = "rip_item_corpse-%s-%s" % (race, sex)
                if code not in database["proto_items"]:
                    if sex == "female":
                        code = "rip_item_corpse-human-female"
                    else:
                        code = "rip_item_corpse-%s-male" % race
                        if code not in database["proto_items"]:
                            code = "rip_item_corpse-human-male"

        # Sceglie il costruttore adatto a seconda del codice dell'entità
        if code.split("_", 2)[1] == "item":
            from src.item import Item
            remains = Item(code)
        else:
            from src.mob import Mob
            remains = Mob(code)

        # E finalmente crea il cadavere o l'oggetto rotto a seconda della
        # tipologia di entità
        remains.weight                    = self.weight
        if self.IS_ITEM:
            remains.material_percentages  = self.material_percentages.copy()
        else:
            remains.corpse_type           = Corpse()
        remains.container_type            = Container()
        remains.container_type.max_weight = self.can_carry_weight()
        if substitute:
            # (TD) È un casino però qui, bisognerebbe fare bene il sistema
            # delle conoscenze per permettere di far riconoscere il cadavere
            # di uno a chi già conosceva l'entità
            if self.IS_MOB:
                remains.keywords_name            = "cadavere"
                remains.keywords_short           = "cadavere"
                if self.keywords_short_night:
                    remains.keywords_short_night = "cadavere"
                remains.short                    = "Il cadavere di " + self.short
                if self.short_night:
                    remains.short_night          = "Il cadavere di " + self.short_night
                remains.name                     = "Il cadavere di " + self.name
            elif self.IS_ITEM:
                material = self.material_percentages.get_major_material()
                material_name = material.name if material else "qualcosa"
                remains.short                    = remains.short.replace("%material", material_name)
                if self.short_night:
                    remains.short_night          = remains.short_night.replace("%material", material_name)
                remains.name                     = remains.name.replace("%material", material_name)
            else:
                remains.keywords_name            = "cadavere"
                remains.keywords_short           = "cadavere"
                remains.short                    = "Il cadavere di " + self.name  # (TD) futura create_short
                remains.name                     = "Il cadavere di " + self.name
        else:
            remains.repop_later = self.repop_later

        # Si da per scontato che i cadaveri non abbiano max_global_quantity impostato
        if self.is_extracted():
            log.bug("entità %s già estratta ancor prima che il suo cadavere potessere essere inserito in gioco." % self.code)
            return None, False
        remains.inject(self.location)

        # Sposta tutto il contenuto dall'entità morente al suo cadavere
        for something in self.iter_contains(use_reversed=True):
            # Alcuni oggetti sono talmente importanti da 'seguire' il giocatore
            # invece di finire nel suo cadavere
            if self.IS_PLAYER and FLAG.STAY_ON_DEATH in something.flags:
                continue
            something = something.from_location(something.quantity, use_repop=False)
            if auto_loot and FLAG.INGESTED not in something.flags:
                if len(something.wear_mode) > 0:
                    something.wear_mode.clear()
                    something.under_weared = None
                something.to_location(remains.location)
            else:
                something.to_location(remains)
            # Ferma la digestione sicché le cose che si erano appena mangiate
            # possano essere trovate squartando il cadavere
            if FLAG.INGESTED in something.flags:
                something.stop_digestion(remove_flag=False)

        return remains, use_repop
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def to_location(self, location, use_look=False, use_iterative_put=True):
        """
        Sposta l'entità da una stanza ad un'altra.
        Praticamente sempre prima di questo metodo bisogna utilizzare il
        metodo from_location.
        """
        if not location:
            log.bug("location non è un parametro valido: %r" % location)
            return

        # ---------------------------------------------------------------------

        if not location.IS_ROOM:
            location = location.split_entity(1)

        force_return = check_trigger(self, "before_to_location", self, location)
        if force_return:
            return

        if self in getattr(location, self.ACCESS_ATTR):
            log.bug("entità %s già esistente nella stanza %s" % (self.code, location.code))
        else:
            getattr(location, self.ACCESS_ATTR).append(self)

        self.put_in_area(location.area, use_iterative_put)

        # Controlla se il massimale storico giornaliero della popolazione di
        # giocatori avuto nell'area sia aumentato
        if self.IS_PLAYER and len(location.area.players) > location.area.max_players:
            location.area.max_players = len(location.area.players)

        # (TD) Calcolo della luce che produce l'entità da aggiungere alla stanza
        if location.IS_ROOM:
            location.mod_light += 0

        # (TD) Aggiunta degli affect della nuova stanza

        # Invia della musica quando serve e solo ai giocatori
        if self.game_request and location.IS_ROOM:
            music = ""
            if self.location:
                if location.area.music and self.location.area != location.area:
                    music = location.area.music
                if self.location.area.music_wild and self.location.area != location.area and location.area.wild:
                    music = location.area.music_wild
            if location.music:
                music = location.music
            if music:
                send_audio(self.get_conn(), music)

        # (TD) ci saranno molti giochetti a riguardo
        if not location.IS_ROOM:
            self.owner = weakref.ref(location)

        # Inserisce l'entità nella stanza voluta, viene impostato anche
        # il previous_location se questo non è valido così da avere un
        # riferimento per la persistenza, difatti mentre location è
        # volatile previous_location viene salvato nei file delle istanze
        # delle entità
        if not self.previous_location or not self.previous_location():
            self.backsteps.append(location.code)
            self.previous_location = weakref.ref(location)
        self.location = location

        # Ferma la decomposizione per gli oggetti che sono spostati e che quindi
        # ora hanno un potenziale interesse per il gioco
        if self.deferred_purification:
            self.stop_purification()

        # Se vi sono delle entità aggressive nella locazione di destinazione
        # allora attiva la loro "aggressività"
        for en in self.location.iter_contains(use_reversed=True):
            if FLAG.AGGRESSIVE in en.flags:
                en.check_aggressiveness(victim=self)

        # Se nella locazione precedente c'era un'entità con delle interazioni
        # relative a self allora le rimuove
        for en in self.previous_location().iter_contains():
            if en.interactions and self in en.interactions:
                en.interactions.remove(self)

        # Controlla se deve aumentare il contatore delle visite nell'area
        # o nella stanza
        if self.IS_PLAYER:
            if location.area.code not in self.visited_areas:
                self.visited_areas[location.area.code]  = 1
                reason = "per aver scoperto l'area %s" % location.area.get_name(looker=self)
                self.give_experience(location.area.level*100, reason=reason)
            elif self.previous_location().area != location.area:
                self.visited_areas[location.area.code] += 1

            if location.IS_ROOM:
                if location.prototype.code in self.visited_rooms:
                    self.visited_rooms[location.prototype.code] += 1
                else:
                    self.visited_rooms[location.prototype.code]  = 1
                    reason = "per aver scoperto %s" % location.get_name(looker=self)
                    self.give_experience(max(1, location.area.level/2), reason=reason)

        # Controlla se l'entità self è stata posseduta per la prima volta da
        # parte del giocatore
        if self.location.IS_PLAYER:
            if self.prototype.code in self.location.possessed_entities:
                self.location.possessed_entities[self.prototype.code] += 1
            else:
                self.location.possessed_entities[self.prototype.code] = 1
                reason = "per essere entrato in possesso di %s per la prima volta" % self.get_name(looker=self.location)
                self.location.give_experience(self.level, reason=reason, first_the_prompt=True)

        # Se si vuole ciò si fa vedere la stanza d'arrivo al giocatore
        if use_look:
            look_a_room(self, self.location)

        force_return = check_trigger(self, "after_to_location", self, location)
        if force_return:
            return

        # Raggruppa le entità nella locazione
        self.location.group_entities()
        if not location.IS_ROOM and location.location:
            location.location.group_entities()
    #- Fine Metodo -

    def from_location(self, quantity, use_iterative_remove=True, use_repop=True, extractig=False):
        """
        Rimuove l'entità da una stanza, o da un'altra entità.
        Rimuove altresì eventuali riferimenti di area.
        """
        splitted = self.split_entity(quantity)

        if not splitted.location:
            log.bug("L'entità %s non ha un location valido: %r" % (splitted.get_name(), splitted.location))
            return None

        force_return = check_trigger(self, "before_from_location", splitted, quantity)
        if force_return:
            return splitted

        # Prepara il repop da eseguire più in là nel tempo, vengono eseguiti
        # i repop delle sole entità che vengono rimosse dalla locazione
        # di reset originale.
        # Questa parte di codice deve rimanere in questa posizione, ovvero prima
        # dell'effettiva rimozione dell'entità dalla locazione per ottenere
        # un responso dal metodo has_reset_on_location valido.
        # Da notare che alcune entità inserite in gioco tramite i gamescript e
        # non i reset non hanno l'istanza repop_later a meno di non inserirla
        # a mano nel gamescript stesso
        # Una volta impostata la deferred relativa al repop cancella l'istanza
        # di repop_later in maniera tale non venga più repoppata e non venga
        # più cambiato lo stato di open/close o wear/remove
        if use_repop and not splitted.IS_PLAYER and splitted.repop_later:
            if FLAG.REPOP_ONLY_ON_EXTRACT in splitted.flags:
                if extractig:
                    splitted.deferred_repop = splitted.repop_later.defer_repop()
                    splitted.repop_later = None
            else:
                if splitted.has_reset_on_location(area=self.area, entity_with_location=self):
                    splitted.deferred_repop = splitted.repop_later.defer_repop()
                    splitted.repop_later = None

        if splitted in getattr(splitted.location, splitted.ACCESS_ATTR):
            getattr(splitted.location, splitted.ACCESS_ATTR).remove(splitted)
        else:
            log.bug("Anche se location è impostata a %s l'entità %s non si trova nell'apposita lista della stanza %s" % (
                splitted.location.code, splitted.code, splitted.location.code))

        # Può capitare che l'entità non abbia un'area valida se per esempio
        # il pg che la conteneva ha quittato e se una deferred ha estratto
        # solo poi l'entità
        if splitted.area:
            splitted.remove_from_area(splitted.area, use_iterative_remove)
        elif not splitted.IS_PLAYER:
            log.bug("entità %s senza area valida: %r" % (splitted.code, splitted.area))

        # (TD) rimozione della luce che produceva l'entità
        if self.location.IS_ROOM:
            self.location.mod_light -= 0

        # (TD) Rimozione degli affect della vecchia stanza, sempre che
        # vengano inseriti e non gettati da una funzione di getter
        pass

        # Se l'entità è una porta sui cardini bisogna rimuoverne i riferimenti
        if splitted.door_type and splitted.is_hinged():
            for direction in self.location.exits:
                if self.location.exits[direction].door == splitted:
                    self.location.exits[direction].door = None
                    break

        # Memorizza il vecchio riferimento
        splitted.backsteps.append(self.location.code)
        splitted.previous_location = weakref.ref(self.location)
        splitted.location = None

        force_return = check_trigger(self, "after_from_location", splitted, quantity)
        if force_return:
            return splitted

        return splitted
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def inject(self, location, avoid_triggers=False, avoid_recursion=False):
        """
        Inserisce un'entità nel gioco e nel database, è una funzioncina utile
        ad evitare codice boilerplate.
        """
        if not location:
            log.bug("location non è un parametro valido iniettando l'entità %s: %r" % (location, self.code))
            return

        # ---------------------------------------------------------------------

        if not avoid_triggers:
            force_return = check_trigger(self, "before_inject", self, location)
            if force_return:
                return

        if not self.prototype:
            log.bug("%s non ha il prototype valido: %r" % (self.code, self.prototype))
            return

        self.prototype.current_global_quantity += self.quantity
        if self.prototype.max_global_quantity > 0 and self.prototype.current_global_quantity > self.prototype.max_global_quantity:
            log.bug("È stato superato il numero massimo (%d) di entità %s inseribili nel Mud: %d" % (
                self.prototype.max_global_quantity,
                self.prototype.code,
                self.prototype.current_global_quantity))

        database[self.ACCESS_ATTR][self.code] = self
        self.to_location(location)

        # Se c'è un tempo di morte allora lo attiva qui, e solo qui, nell'inject
        if self.extract_timeout:
            minutes = random.randint(self.extract_timeout.minutes - (self.extract_timeout.minutes / 10),
                                     self.extract_timeout.minutes + (self.extract_timeout.minutes / 10))
            self.extract_timeout.deferred = defer(minutes * config.seconds_in_minute, self.extract_timeout.execute, self)

        if not avoid_triggers:
            force_return = check_trigger(self, "after_inject", self, location)
            if force_return:
                return
    #- Fine Metodo -

    def extract(self, quantity, originally_extracted=None, use_repop=True, avoid_triggers=False):
        """
        Rimuove un'entità dal gioco e dal database per sempre.
        """
        if quantity <= 0:
            log.bug("quantity non è un parametro valido, deve essere superiore a zero: %d" % quantity)
            return None

        # ---------------------------------------------------------------------

        entity = self

        if entity.is_extracted():
            # Può capitare, con tutte le deferred in giro, lasciamo perdere
            # il messaggio d'errore altrimenti ci ritroviamo con un codice
            # boilerplate tra tutti i check da inserire...
            #log.bug("L'entità %s è già stata estratta!" % entity.code)
            return entity

        # Questo è meglio che rimanga prima del trigger
        if not originally_extracted:
            originally_extracted = entity

        if not avoid_triggers:
            force_return = check_trigger(entity, "before_extract", entity)
            if force_return:
                return entity

        # Se l'entità aveva un conto alla rovescia extract_timeout allora lo disattiva
        if entity.extract_timeout and entity.extract_timeout.deferred:
            entity.extract_timeout.deferred.pause()
            entity.extract_timeout.deferred = None

        # Se l'entità da estrarre è un giocatore allora si comporta in maniera
        # tale che se era il giocatore stesso ad essere estratto lo uccide,
        # altrimenti se il giocatore era solo il contenuto di qualcosa estratto
        # allora lo piazza nella locazione dell'entità originalmente estratta
        if entity.IS_PLAYER:
            if entity == originally_extracted or not originally_extracted.location:
                # (TD) ucciderlo invece di teletrasportarlo, attenzione
                # all'inventario che è da preservare
                entity = entity.from_location(quantity, use_repop=False, extractig=True)
                if not entity:
                    entity = self
                entity.to_location(config.initial_destination.get_room())
                #entity.act("$N viene distrutt$O e tu muori.", TO.ENTITY, originally_extracted)
                #entity.act("$n muore dentro $N quando questo viene distrutt$O.", TO.OTHERS, originally_extracted)
                #entity.act("$n muore assieme a te mentre vieni distrutt$O.", TO.TARGET, originally_extracted)
            else:
                entity = entity.from_location(quantity, use_repop=False, extractig=True)
                if not entity:
                    entity = self
                entity.to_location(originally_extracted.location)
                entity.act("$N viene distrutt$O e tu ti ritrovi al suo esterno.", TO.ENTITY, originally_extracted)
                entity.act("$n esce da $N mentre questo viene distrutt$O.", TO.OTHERS, originally_extracted)
                entity.act("$n esce da te mentre vieni distrutt$O.", TO.TARGET, originally_extracted)
            return entity

        # Prima rimuove il contenuto dell'entità
        for list_to_scan in entity.ENTITY_TABLES:
            for content in reversed(getattr(entity, list_to_scan)):
                content.extract(content.quantity, originally_extracted=originally_extracted, use_repop=False)

        entity = entity.from_location(quantity, use_iterative_remove=False, use_repop=use_repop, extractig=True)
        if not entity:
            entity = self
        if entity.code in database[entity.ACCESS_ATTR]:
            del database[entity.ACCESS_ATTR][entity.code]
        else:
            log.bug("Non è stato trovato nessun %s in database[%s]" % (entity.code, entity.ACCESS_ATTR))

        entity.prototype.current_global_quantity -= entity.quantity
        if entity.prototype.current_global_quantity < 0:
            log.bug("Per qualche strano motivo current_global_quantity di %s è minore di zero: %d" % (
                entity.prototype.code, entity.prototype.current_global_quantity))

        # A volte è utile conoscere se un'entità è già stata estratta o meno
        # poiché l'entità nonostante sia stata rimossa dal gioco potrebbe
        # ancora venire utilizzata, erroneamente, da una deferLater
        entity.flags += FLAG.EXTRACTED

        if not avoid_triggers:
            force_return = check_trigger(entity, "after_extract", entity)
            if force_return:
                return entity

        return entity
    #- Fine Metodo -

    def weak_extract(self):
        """
        E' un metodo formato da pezzi di extract, from_location e da
        remove_from_area e serve a spalla del metodo get_similar_here:
        sostanzialmente a rimuovere un'entità dalla memoria senza
        eseguire tutte le procedure che si dovrebbero eseguire (a partire
        dall'aggiornamento del current_global_quantity), questo perché
        l'entità non viene realmente rimossa dal gioco ma viene aumentata
        la quantità di un'altra entità fortemente simile ad essa che si
        trova nella stessa locazione.
        """
        if self.is_extracted():
            return

        if not self.is_empty():
            log.bug("weak_extract eseguita su %s con contenuti: %s %s %s" % (self.code, self.items, self.mobs, self.players))
            return

        if self in getattr(self.area, self.ACCESS_ATTR):
            getattr(self.area, self.ACCESS_ATTR).remove(self)
        else:
            log.bug("%s non si trova nell'area %s" % (self.code, self.area.code))
        self.area = None

        if self in getattr(self.location, self.ACCESS_ATTR):
            getattr(self.location, self.ACCESS_ATTR).remove(self)
        else:
            log.bug("Anche se location è impostata a %s l'entità %s non si trova nell'apposita lista della stanza %s" % (
                self.location.code, self.code, self.location.code))

        if self.code in database[self.ACCESS_ATTR]:
            del database[self.ACCESS_ATTR][self.code]
        else:
            log.bug("Non è stato trovato nessun %s in database[%s]" % (self.code, self.ACCESS_ATTR))

        self.flags += FLAG.WEAKLY_EXTRACTED
    #- Fine Metodo -

    def is_extracted(self):
        """
        Indica se l'entità è già stata estratta dal gioco.
        Serve soprattutto negli script contenenti delle deferLater per
        capire se l'entità è ancora in gioco dopo che la deferLater è scattata.
        """
        if FLAG.EXTRACTED in self.flags:
            return True

        if FLAG.WEAKLY_EXTRACTED in self.flags:
            return True

        return False
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def remove_from_area(self, area, use_iterative_remove):
        """
        Rimuove ricorsivamente tutti i riferimenti di area delle entità
        contenute in self.
        """
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return

        # ---------------------------------------------------------------------

        if use_iterative_remove:
            contained_entities = [self] + list(self.iter_all_entities())
        else:
            contained_entities = [self]

        for contained_entity in contained_entities:
            if not contained_entity:
                log.bug("contained_entity %r in %s" % (contained_entity, contained_entities))
                continue
            contained_entity.area = None
            if contained_entity in getattr(area, contained_entity.ACCESS_ATTR):
                getattr(area, contained_entity.ACCESS_ATTR).remove(contained_entity)
            else:
                log.bug("L'entità %s non si trova nell'area %s" % (contained_entity.code, area.code))
    #- Fine Metodo -

    def put_in_area(self, area, use_iterative_put):
        """
        Modifica ricorsivamente tutti i riferimenti di area delle entità
        contenute in self.
        """
        if not area:
            log.bug("area non è un parametro valido: %r (per %s in %r)" % (area, self.code, self.location))
            return

        # use_iterative_put ha valore di verità

        # ---------------------------------------------------------------------

        if use_iterative_put:
            contained_entities = [self] + list(self.iter_all_entities())
        else:
            contained_entities = [self]

        for contained_entity in contained_entities:
            if not contained_entity:
                log.bug("contained_entity %r in %s" % (contained_entity, contained_entities))
                continue
            contained_entity.area = area
            if contained_entity not in getattr(area, contained_entity.ACCESS_ATTR):
                getattr(area, contained_entity.ACCESS_ATTR).append(contained_entity)
            # Poiché le porte possono essere inserite nell'altro lato di
            # un'uscita on the fly esse si trovano cmq ancora nell'area ed
            # eventuali errori a riguardo vengono quindi ignorati
            elif not contained_entity.door_type:
                log.bug("L'entità %s si trova già nell'area %s" % (contained_entity.code, area.code))
                import sys
                sys.exit(0)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def group_entity(self, except_these_attrs=None):
        if except_these_attrs is None:
            except_these_attrs = EXCEPT_THESE_ATTRS

        if self.IS_PLAYER:
            return
        if self.is_hinged():
            return
        if not self.is_empty():
            return

        # Controlla se vi sono altre entità nella locazione di self che sono
        # equivalenti a self stesso
        for target in self.location.iter_contains(entity_tables=["items", "mobs"], use_reversed=True):
            if self.prototype.code != target.prototype.code:
                continue
            if target == self:
                continue
            if target.IS_PLAYER:
                continue
            if target.is_hinged():
                continue
            if not target.is_empty():
                continue
            for attr_name, value in self.__dict__.iteritems():
                if attr_name in except_these_attrs:
                    continue
                target_value = getattr(target, attr_name)
                if hasattr(value, "equals"):
                    if not value.equals(target_value):
                        # (TD) Ogni tanto attivare questi commenti per controllare
                        # la situazione
                        #if self.prototype.code == "limbo_item_random":
                        #    print "+", attr_name, self.code, target.code, getattr(target, attr_name), value
                        break
                else:
                    if value != target_value:
                        #if self.prototype.code == "limbo_item_random":
                        #    print "-", attr_name, self.code, target.code, getattr(target, attr_name), value
                        break
            else:
                # Se sono equivalenti allora provvede ad accorparli tra loro.
                set_deferred_args(target, self)
                self.quantity += target.quantity
                if "deferred_repop" in except_these_attrs:
                    if target.deferred_repop:
                        if self.deferred_repop:
                            target.stop_repop()
                        else:
                            self.deferred_repop = target.deferred_repop
                # Poiché si presuppone che self serva ancora nel successivo
                # flusso di codice alla chiamata di questo metodo viene estratto
                # target, tuttavia poiché è necessario mantenere l'ordine
                # precedente tra le varie entità self viene inserito al posto
                # di target
                location_entities = getattr(self.location, self.ACCESS_ATTR)
                location_entities.remove(self)
                target_index = location_entities.index(target)
                location_entities.insert(target_index, self)
                target.weak_extract()
    #- Fine Metodo -

    def group_entities(self):
        """
        Controlla se c'è bisogno di accorpare dell'entità in mucchietti uguali.
        C'è da notare che questo metodo non viene chiamato nel metodo to_location,
        che complicherebbe di molto poi l'utilizzo nei gamescripts, ma solo quando:
        - viene resettato qualche cosa
        - viene repoppato qualche cosa
        - tramite il comando look
        - tramite il comando inventory
        Ovvero viene chiamato il meno possibile e solo in punti strategici, questo
        per diminuire eventuali problemi con gamescripts o deferred. Difatti
        vi potrebbero essere dei problemi se un gamescripter scrivesse un codice
        in cui:
        - viene eseguito il to_location di una entità
        - viene guardata, tramite gamescripts, la locazione in cui vi è l'entità
        - si cerca di manipolare l'entità dopo che questa sia stata ammucchiata
          e quindi non più esistente come entità a se stante ma in un mucchio
        Portanto quindi a bachi molto subdoli, attenzione!
        Il fatto che il raggruppamento venga chiamato solo durante il look e
        l'inventory può portare a picchi computazionali nell'esecuzione di tali
        comandi, tuttavia è una cosa una tantum, di contro se non avvengono dei
        look in una locazione vi potrebbero essere consumo di RAM più o meno
        sprecosi. Per ora la situazione non sembra essere preoccupante, anche
        perché vi sono dei mob che tramite i behaviour di wandering eseguono
        dei look, però è comunque meglio tenerla a mente.
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

    def split_entity(self, quantity):
        """
        Attenzione che la risultante, splitted, una volta chiamato questo metodo
        è da inserire in una locazione.
        """
        if self.IS_PLAYER or quantity is None or self.quantity <= 1 or quantity >= self.quantity:
            return self

        if self.door_type and self.is_hinged() and self.quantity > 1:
            log.bug("Porta %s resettata sugli stipiti in quantità di %d e non di 1" % (self.code, self.quantity))
            return self

        if quantity >= self.quantity:
            return self

        splitted = self.CONSTRUCTOR(self.prototype.code)
        copy_existing_attributes(self, splitted, except_these_attrs=["code", "prototype"])

        self.quantity -= quantity
        splitted.quantity = quantity

        splitted.area = self.area
        getattr(splitted.area, splitted.ACCESS_ATTR).append(splitted)
        splitted.location = self.location
        # È meglio inserire l'entità splittata prima dell'entità self poiché
        # solitamente le entità manipolate singolarmente (e quindi splittate)
        # sarebbero concettualmente quelle in cima al mucchio e quindi le prime
        # raggiungibili in eventuali manipolazione successive
        # Attenzione che ciò comporta che anche entità manipolate per esempio
        # così: give calza 3.contenitore, il contenitore venga inserite in testa
        # a tutti gli altri uguali, è un limite voluto
        location_entities = getattr(splitted.location, splitted.ACCESS_ATTR)
        self_index = location_entities.index(self)
        location_entities.insert(self_index, splitted)
        splitted.previous_location = weakref.ref(self.location)
        splitted.backsteps.append(self.location.code)
        database[splitted.ACCESS_ATTR][splitted.code] = splitted

        # Non deve mai capitare che entità splittate abbiano del contenuto,
        # significherebbe che sta avvenendo un errore di duplicazione!
        if not splitted.is_empty():
            log.bug("Errore grave di duplicazione %s(%d) da %s(%d) con del contenuto %s %s %s, verrà eseguita una procedura di pulizia" % (
                splitted.code, splitted.quantity, self.code, self.quantity, splitted.items, splitted.mobs, splitted.players))
            for attr_name in self.ENTITY_TABLES:
                contains = getattr(splitted, attr_name)
                for value in contains:
                    value.area = None
                    value.location = None
                    contains.remove(value)

        # Dopo il tempo massimo d'esecuzione di un comando prova a riunire
        # nuovamente l'entità precedentemente divisa, è una parte di codice
        # piuttosto delicata e che porta inneluttabilmente a bachi (specie con
        # l'uso di deferred che manipolano tale entità nei gamescript attivati
        # dai comandi), ma l'inserimento di tale istruzione in questo punto
        # evita una pletora di chiamate del metodo group_entities nel codice.
        # Faccio difatti notare che la find_entity esegue di norma una
        # split_entity a quantità 1 e che quindi prima di uscire da ogni comando
        # che ha utilizzato una chiamata find_entity bisognerebbe, senza questa
        # deferred, cercare di ragruppare l'entità, ovvero prima di ogni return
        # dei comandi successivi alla chiamata della find_entity; ho preferito
        # quindi evitare tale soluzione troppo capillare per i miei gusti ed
        # entrare nel mondo dell'aletoreità asincronica.
        # Ecco come mai, nella interpret, è così importante che un comando
        # venga eseguito entro il valore definito in max_execution_time.
        defer(config.max_execution_time, splitted.location.group_entities)

        return splitted
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    # (TD) Quando si creerà la classe Entity creare il metodo uguale a questo
    # e richiamarlo tramite il suo prototype
    def has_reached_max_global_quantity(self):
        if self.max_global_quantity != 0 and self.current_global_quantity >= self.max_global_quantity:
            return True
        else:
            return False
    #- Fine Metodo -

    def can_see(self, target):
        """
        Ritorna vero se l'entità può vedere la vittima passata.
        Qui non bisogna inserire il check del NO_LOOK_LIST.
        """
        if not target:
            log.bug("target non è un parametro valido: %s" % target)
            return False

        # ---------------------------------------------------------------------

        if self.trust > TRUST.PLAYER:
            return True

        # Se il giocatore ha impostato l'incognito allora non viene visto
        if target.incognito:
            return False

        if FLAG.INGESTED in target.flags:
            return False

        if FLAG.BURIED in target.flags:
            return False

        # (TD) per ora in tutti gli altri casi si vede
        return True
    #- Fine Metodo -

    def is_outside(self):
        # (TD)
        return True
    #- Fine Metodo -

    def is_empty(self):
        if self.items or self.mobs or self.players:
            return False
        else:
            return True
    #- Fine Metodo -

    # (TD) Se si converte wear_mode in una classe apposita si può accorpare
    # questo metodo e l'attributo under_weared lì nel modulo wear.py
    def is_layerable(self):
        """
        Ritorna vero se l'entità è possibile vestirla come strato superiore
        rispetto ad un'altra.
        """
        if not self.wear_type:
            return False

        if WEAR.LAYERABLE not in self.wear_type.flags:
            return False

        # Se ha già un'entità vestita al di sotto allora non permette un
        # ulteriore strato di vestito
        if self.under_weared and self.under_weared():
            return False

        return True
    #- Fine Metodo -

    def is_sensable_inside(self, sense, looker=None, show_message=False):
        if sense not in ("sight", "hearing", "smell", "touch", "taste", "sixth"):
            log.bug("sense non è un parametro valido: %r" % sense)
            return False

        # ---------------------------------------------------------------------

        if self.container_type and CONTAINER.CLOSED not in self.container_type.flags:
            return True

        major_material = self.material_percentages.get_major_material()
        # (TD) Al posto del glass inserire una proprietà trasparency così
        # da poter gestire più materiali
        if sense in ("sight", "sixth") and major_material and major_material == MATERIAL.GLASS:
            return True

        if looker and looker.trust > TRUST.PLAYER:
            if show_message:
                # (BB) per ora con il sistema ajax questo messaggio non viene
                # inviato, ci vuole la nuova tipologia di connessione per far
                # funzionare al meglio le cose
                self.send_to_admin("Ti è possibile usare il senso di %s nell'entità anche se non è un contenitore" % sense)
            return True

        return False
    #- Fine Metodo -

     # (TD) forse non servirà più
#    def maybe_genuinely_discovered(discoverer):
#        """
#        Funzione che ritorna vero se l'oggetto potrebbe essere stato trovato
#        dall'entità discoverer senza che sia stato passato tramite un give
#        da parte di un altro giocatore oppure tramite un drop da parte di un
#        altro giocatore e get da parte del discoverer se tutti si trovano
#        nella stessa stanza.
#        """
#        if not discoverer:
#            log.bug("discoverer non è un parametro valido: %r" % discoverer)
#            return
#
#        # ---------------------------------------------------------------------
#
#        
#    #- Fine Metodo -
#
#    # -------------------------------------------------------------------------

    def is_switched(self):
        """
        Indica se il giocatore è switchato all'interno di un mob.
        """
        # (TD)
        return False
    #- Fine Metodo -

    def is_original(self):
        """
        Indica se il mob non ha nessun player switchato al suo interno.
        """
        # (TD)
        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def is_hinged(self):
        """
        Ritorna vero se l'entità è una porta che si trova sui cardini di un'uscita.
        """
        if not self.door_type:
            return False

        if not self.location:
            log.bug("%s non si trova in una locazione valida: %r" % (self.code, self.location))
            return False

        if not self.location.IS_ROOM:
            return False

        for direction in self.location.exits:
            if self.location.exits[direction].door == self:
                return True

        return False
    #- Fine Metodo -

    def get_open_close_priority(self):
        """
        Ricava la priorità della tipologia di entità da utilizzare durante il
        comando open e close: se door o container.
        """
        # Da la priorità all'apertura della tipologia dichiarata come usabile
        if self.entitype == ENTITYPE.DOOR:
            entitype_priority = "door"
        elif self.entitype == ENTITYPE.CONTAINER:
            entitype_priority = "container"
        else:
            if self.door_type:
                entitype_priority = "door"
            else:
                entitype_priority = "container"

        # Se l'entità è formata da tipologia door e container e quella con
        # priorità è già aperta controlla se deve chiudere l'altra
        if entitype_priority == "door" and self.door_type and DOOR.CLOSED not in self.door_type.flags:
            if self.container_type and CONTAINER.CLOSED in self.container_type.flags:
                entitype_priority = "container"
        elif entitype_priority == "container" and self.container_type and CONTAINER.CLOSED not in self.container_type.flags:
            if self.door_type and DOOR.CLOSED in self.door_type.flags:
                entitype_priority = "door"

        return entitype_priority
    #- Fine Metodo -

    def is_the_door_on_reverse_dir(self):
        """
        Metodo che serve a ricavare se una porta si vede anche dall'uscita
        dell'altro lato, se ciò è così allora ritorna la stanza nell'altro lato
        e la direzione che punta verso la destinazione.
        """
        if not self.door_type:
            return None, None
    
        if not self.location.IS_ROOM:
            return None, None
    
        if not self.is_hinged():
            return None, None
    
        destination_room, direction = get_destination_room_from_door(self, self)
        if not destination_room:
            log.bug("Inattesa inesistenza di una stanza di destinazione per la porta %s alla direzione %s" % (
                self.code, direction))
            return None, None
    
        reverse_door = destination_room.get_door(direction.reverse_dir, reverse_search=False)
        if reverse_door:
            return None, None
    
        return destination_room, direction
    #- Fine Metodo -

    def to_reverse_hinges(self):
        """
        Permette di inserire una porta dall'altro lato della stanza di
        destinazione. Serve per far funzionare, almeno momentaneamente,
        alcune funzionalità per la stanza di destinazione, come per esempio
        i behaviours.
        """
        if not self.door_type:
            log.bug("Si sta eseguendo un to_reverse_hinges senza che l'entità sia una porta: %s" % self.code)
            return None, None

        if self.quantity != 1:
            log.bug("Porta %s resettata sugli stipiti in quantità di %d e non in una sola unità" % (self.code, self.quantity))
            return None, None

        destination_room, direction = self.is_the_door_on_reverse_dir()
        if not destination_room:
            return None, None

        door = self.from_location(1, use_repop=False)
        door.to_location(destination_room)
        destination_room.exits[direction.reverse_dir].door = door
        return destination_room, direction
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_in_room(self):
        """
        Cerca ricorsivamente in quale stanza si trovi l'entità.
        """
        en = self
        while 1:
            if en.location:
                en = en.location
                if en.IS_ROOM:
                    return en
            # Altrimenti in teoria il pg è offline
            elif en.previous_location and en.previous_location():
                en = en.previous_location()
                if en.IS_ROOM:
                    return en
            else:
                # È normale se un giocatore non è mai entrato in gioco
                if (self.IS_PLAYER and self.login_times != 0) or not self.IS_PLAYER:
                    log.bug("location e previous_location non validi per l'entità %s" % en.code)
                break

        return None
    #- Fine Metodo -

    def get_player_carrier(self):
        """
        Ritorna il primo personaggio, in un'eventuale ricorsione di contenitori
        (modello matrioska), che sta trasportando quest'entità.
        """
        last_player = None

        loc = self.location
        while loc and not loc.IS_ROOM:
            if loc.IS_PLAYER:
                last_player = loc
            loc = loc.location

        return last_player
    #- Fine Metodo -

    def get_player_previous_carrier(self):
        """
        Ritorna il primo personaggio, in un'eventuale ricorsione di contenitori
        (modello matrioska), che stava trasportando quest'entità.
        """
        last_player = None

        loc = self
        while 1:
            if loc != self and loc.IS_PLAYER:
                last_player = loc
            if loc.location:
                loc = loc.location
                if loc.IS_ROOM:
                    break
            elif loc.previous_location and loc.previous_location():
                loc = loc.previous_location()
            else:
                log.bug("location e previous_location non validi per l'entità %s" % loc.code)
                return loc
            if loc.IS_ROOM:
                break

        return last_player
    #- Fine Metodo -

    def get_container_carrier(self):
        """
        Ritorna il primo contenitore, in un'eventuale ricorsione di contenitori
        (modello matrioska), che sta trasportando quest'entità.
        """
        last_container = None

        loc = self.location
        while loc and not loc.IS_ROOM:
            if loc.container_type:
                last_container = loc
            loc = loc.location

        return last_container
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def wait(self, seconds):
        if self.deferred_wait:
            self.deferred_wait.pause()  # (TT)
        self.deferred_wait = defer(seconds, self.stop_wait)
    #- Fine Metodo -

    def stop_wait(self):
        if self.deferred_wait:
            self.deferred_wait.pause()  # (TT)
        self.deferred_wait = None

        if self.waiting_inputs:
            input = self.waiting_inputs.popleft()
            interpret(self, input)
    #- Fine Metodo -

    stop_digestion = stop_digestion

    # -------------------------------------------------------------------------

    def start_purification(self, rpg_hours, decomposition=False):
        """
        Indica che un'entità verrà estratta se non manipolata entro tot tempo.
        La manipolazione sull'entità indica difatti che potrebbe essere
        importante o utile ad un giocatore.
        Ci sono tre punti in cui la purificazione viene fermata, nella
        to_location, nel comando wear e nel comando eat.
        """
        if rpg_hours < 1 or rpg_hours > 720:
            log.bug("rpg_hours non è un valore numerico tra 1 e 720: %d" % rpg_hours)
            return

        # ---------------------------------------------------------------------

        if self.IS_PLAYER:
            log.bug("È pericolo eseguire delle purificazioni sui personaggi")
            return

        real_seconds = rpg_hours * config.seconds_in_minute * config.minutes_in_hour
        self.deferred_purification = defer(real_seconds, self.execute_purification, decomposition)
    #- Fine Metodo -

    def stop_purification(self):
        if self.deferred_purification:
            self.deferred_purification.pause()  # (TT)
        self.deferred_purification = None
    #- Fine Metodo -

    def execute_purification(self, decomposition):
        """
        Esegue, con messaggio esplicito (per evitare che non ci si accorga e
        si pensi che sia un baco), la purificazione cioè l'estrazione dal gioco.
        """
        # decomposition ha valore di verità

        # ---------------------------------------------------------------------

        if self.is_extracted():
            return

        # Prima controlla che l'oggetto non sia di valore e quindi sarebbe
        # potenzialmente errato rimuoverlo, viene quindi reinserito nel gioco
        # buttandolo via in apposite discariche.
        # Da notare che le wild non hanno il sistema delle discariche
        to_save = None
        if not decomposition and self.area.wild:
            if value > 1000 or random.randint(0, 100) == 0:
                area_code = self.area.landfill_code.split("_room", 1)[0]
                area = database["areas"][area_code]
                for room in area.rooms.itervalues():
                    if room.prototype.code == self.area.landfill_code:
                        # Da notare che ne salva per una quantità di 1
                        to_save = self.from_location(1, use_repop=True)  # (TT) forse ci sono dei casi che richiedereanno che questa riga stia sotto un 'if location:'
                        to_save.to_location(room)
                        break
                else:
                    log.bug("Non è stata trovata nessuna stanza di landfill con codice %s" % self.area.landfill_code)

        # Se l'entità passata era in quantità di 1 allora è la medesima inviata
        # nella discarica e quindi non c'è bisogno di estrarre il resto
        if to_save == self:
            return

        if decomposition:
            self.act("Ti decomponi fino a diventare polvere.", TO.ENTITY)
            self.act("$n si decompone fino a diventare polvere.", TO.OTHERS)
        elif self.purification_message:
            # C'è un solo messaggio, per gli others, ma viene inviato anche
            # all'entity, per non esagerare con l'implementazione ho preferito
            # aggiungere solo un attributo e gestirlo così
            self.act(self.purification_message, TO.ENTITY)
            self.act(self.purification_message, TO.OTHERS)
        else:
            self.act("Ti disgreghi fino a diventare polvere.", TO.ENTITY)
            self.act("$n si disgrega fino a diventare polvere.", TO.OTHERS)
        self.stop_purification()
        self.extract(self.quantity, use_repop=True)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def stop_repop(self):
        self.repop_later = None
        if self.deferred_repop:
            self.deferred_repop.pause()
            self.deferred_repop = None
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    # (TD) da migliorare controllando gli attributi volatili, ma mi sa che
    # il sistema viene bocciato, lo tengo un po' per riferimento
    # (visto che mi son sbattuto a crearlo)
    #def merge_similar(self, location):
    #    """
    #    Unisce in un unico due oggetti identici aumentando il contatore interno.
    #    """
    #    if self.IS_PLAYER:
    #        return None
    #
    #    for contained in location.iter_contains():
    #        if contained == self:
    #            continue
    #        if equals(self, contained, except_these_attrs=["code", "persistent_act"]):
    #            contained.count += 1
    #            return contained
    #
    #    return None
    #- Fine Metodo -

    is_secret_door = _is_secret_door


#-------------------------------------------------------------------------------

class ExtractTimeout(object):
    PRIMARY_KEY = ""
    VOLATILES   = ["deferred"]
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment        = ""  # Commento relativo la struttura
        self.minutes        = 0   # Minuti rpg prima che l'entità venga rimossa dal gioco
        self.entity_message = ""  # Messaggio di act inviato all'entità da estrarre
        self.others_message = ""  # Messaggio di act inviato a tutti coloro che sono nella locazione dell'entità quando viene estratta

        # Attributi volatili
        self.deferred = None  # Deferred che scatterà quando il tempo è scaduto rimuovendo l'entità dal gioco
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if self.minutes <= 0:
            return "minutes non è un valore valido: %d" % self.minutes

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = ExtractTimeout()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, extract_timeout2):
        if not extract_timeout2:
            return False

        if self.comment != extract_timeout2.comment:
            return False
        if self.minutes != extract_timeout2.minutes:
            return False
        if self.entity_message != extract_timeout2.entity_message:
            return False
        if self.others_message != extract_timeout2.others_message:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def execute(self, entity):
        # È normale che sia a None perché potrebbe essere stato estratto in
        # precedenza e ritornato come None tramite le funzioni di defer
        if not entity:
            return

        entity.act(self.entity_message, TO.ENTITY)
        entity.act(self.others_message, TO.OTHERS)

        entity.extract(entity.quantity, use_repop=True)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def create_random_entity(entity=None, name="", level=0, race=RACE.NONE, sex=SEX.NONE):
    """
    Crea casualmente le caratteristiche generiche di un'entità.
    Il nome, altezza, peso, età e descrizioni variano a seconda del tipo di
    entità e non vengono impostate qui.
    Questa funzione teoricamente è da chiamare solamente dalle altre funzioni
    create_random_...() dei differenti tipi di entità.
    """
    if not name:
        log.bug("name non è un parametro valido: %r" % name)
        return

    if level < 0 or level > config.max_level:
        log.bug("level non è un parametro valido: %d" % level)
        return

    if not race:
        log.bug("race non è un parametro valido: %r" % race)
        return

    if not sex:
        log.bug("sex non è un parametro valido: %r" % sex)
        return

    # -------------------------------------------------------------------------

    if not entity:
        entity = ProtoEntity()

    entity.name = name

    # Se la razza è NONE ne scegli una a caso
    entity.race = Element(race)
    if entity.race == RACE.NONE:
        entity.race.randomize()

    # Se il sesso è NONE ne sceglie uno a caso
    entity.sex = Element(sex)
    if entity.sex == SEX.NONE:
        entity.sex.randomize()

    # Sceglie a caso un livello se non è stato passato
    if level == 0:
        entity.level = random.randint(1, config.max_level)
    else:
        entity.level = level

    # Imposta giorno e mese di nascita o di creazione
    entity.birth_day = random.randint(1, config.days_in_month)
    entity.birth_month.randomize()

    # (TD) manca la creazione casuale di altre variabili soprattutto in base alla razza
    pass

    # Finito!
    return entity
#- Fine Funzione -


#-------------------------------------------------------------------------------

def load_little_words():
    filepath = "data/little_words.list"
    try:
        little_words_file = open(filepath, "r")
    except IOError:
        log.bug("Impossibile aprire il file %s in lettura" % filepath)
        return

    global little_words
    for line in little_words_file:
        line = line.strip()
        if not line:
            continue
        if line[0] == "#":
            continue
        if " " in line:
            log.bug("little word non valida: %s" % line)
            continue
        little_words.append(line)
#- Fine Funzione -


def remove_little_words(argument):
    """
    Rimuove tutte le "parole piccole", come articoli, particelle pronominali
    e simili, dall'argomento passato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    argument = clean_string(argument)
    if not argument:
        log.bug("argument non è valido dopo averlo ripulito: %r" % argument)
        return ""

    args = argument.split(" ")
    if not args:
        log.bug("args non è valido dopo lo split: %r" % args)
        return argument

    result = ""
    for arg in args:
        avoid_to_add = False
        for little_word in little_words:
            # (OO) ottimizzabile spostando all'esterno la creazione di un'array
            # new_little_words in cui ci sono già gli spazi aggiunti alle
            # little_word senza un apostrofo finale
            if little_word[-1] == "'" and arg.startswith(little_word):
                arg = arg[len(little_word) : ].lstrip()
                if not arg:
                    avoid_to_add = True
                    break
            elif arg == little_word:
                avoid_to_add = True
                break
        if not avoid_to_add:
            result += "%s " % arg

    return result.rstrip()
#- Fine Funzione -


def create_keywords(argument, entity):
    """
    Ritorna le keywords partendo dall'argomento passato filtrandolo da articoli,
    particelle, parole molto corte e simili.
    Poiché simboli come virgola o punto e virgola vengono inseriti subito dopo
    una parola senza aggiungere uno spazio questi verranno a far parte della
    keywords stessa, tuttavia di problemi non dovrebbero sussisterne visto che
    la ricerca delle keywords è anche prefissa, e il simbolo rimarrebbe alla
    fine della keyword stessa.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r per l'entità %s" % (argument, entity))
        return ""

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    original_argument = argument
    if "." in argument[-1]:
        argument = argument.rstrip(".")

    global remove_colors
    if not remove_colors:
        from color import remove_colors
    argument = remove_colors(argument)
    if not argument:
        log.bug("argument dopo remove_colors non è valido: %r" % argument)
        return []

    argument = remove_tags(argument)
    if not argument:
        log.bug("argument dopo remove_tags non è valido: %r" % argument)
        return []

    if "$O" in argument:
        argument = argument.replace("$O", grammar_gender(entity))

    argument = remove_little_words(argument)
    if not argument:
        log.bug("argument dopo remove_little_words non è valido: %r" % argument)
        return []

    # Rimuove tutte le parole formate da una sola lettera
    # (TD) forse qui in futuro dovrò aggiungere un supporto per la one_argument
    keywords = []
    for key in argument.split():
        if key and len(key) > 1:
            keywords.append(key)

    #print "keywords test: '%s' -> '%s'" % (original_argument, " ".join(keywords))  # (TT)
    return " ".join(keywords)
#- Fine Funzione -
