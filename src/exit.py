# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle uscite e delle mura di una stanza.
"""


#= IMPORT ======================================================================

from src.calendar    import calendar
from src.database    import database
from src.describable import Describable
from src.element     import Element, Flags
from src.extra       import Extras
from src.enums       import DOOR, DIR, EXIT
from src.log         import log
#from src.material    import MaterialPercentages
from src.utility     import is_prefix, put_final_dot, copy_existing_attributes


#= CLASSI ======================================================================

#(TD) spostare gli attributi di descr nella classe Describable, come nelle altre
# classi utili; decidere se Exit e Wall abbisognino dell'attributo keywords

class Exit(Describable):
    """
    Gestisce una singola uscita di una stanza.
    """
    PRIMARY_KEY = "direction"
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"extras"      : ("src.extra", "ExtraDescription"),
                   "height"      : ("",          "measure"),
                   "depth"       : ("",          "measure"),
                   "destination" : ("src.room",  "Destination")}
    REFERENCES  = {}
    WEAKREFS    = {}

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = False
    IS_EXIT   = True
    IS_WALL   = False
    IS_ACTOR  = False
    IS_MOB    = False
    IS_ITEM   = False
    IS_PLAYER = False
    IS_EXTRA  = False
    IS_PROTO  = False

    def __init__(self, direction=DIR.NONE):
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return

        # ---------------------------------------------------------------------

        self.comment             = ""  # Eventuale commento all'uscita
        self.direction           = Element(direction)  # Tipologia della direzione
        self.descr               = ""  # Descrizione di quello che si vede guardando la direzione
        self.descr_night         = ""  # Descrizione notturna di quello che si vede guardando la direzione
        self.descr_hearing       = ""  # Descrizione uditiva
        self.descr_hearing_night = ""  # Descrizione uditiva notturna
        self.descr_smell         = ""  # Descrizione odorosa
        self.descr_smell_night   = ""  # Descrizione odorosa notturna
        self.descr_touch         = ""  # Descrizione tattile
        self.descr_touch_night   = ""  # Descrizione tattile notturna
        self.descr_taste         = ""  # Descrizione del sapore
        self.descr_taste_night   = ""  # Descrizione del sapore notturna
        self.descr_sixth         = ""  # Descrizione del sesto senso
        self.descr_sixth_night   = ""  # Descrizione del sesto senso notturna
        self.icon                = ""  # Icona rappresentante l'uscita di giorno
        self.icon_night          = ""  # Icona rappresentante l'uscita di notte
        self.extras              = Extras()  # Descrizioni extra dell'uscita
        self.flags               = Flags(EXIT.NONE)  # Flags dell'uscita
        self.destination         = None # Stanza a cui l'uscita porta se questa differente rispetto alla direzione presa
        self.door                = None # Oggetto porta se serve aprirla (se non viene indicata questa viene caricata dal limbo una porta di default)  (TD) qui vorrei aggiungere anche una variabile finestra.. ma poi come gestire finestre e porte multiple? e il key_code nel qual caso una finestra sia chiudibile (cmq per ora continuo così.. in effetti potrei considerare il fatto di voler inserire più porte o finestre in una uscita come una eccezione e gestirla tramite gamescripts)
        self.entity_message      = ""   # Messaggio di movimento per colui che si sta spostando
        self.others_in_message   = ""   # Messaggio di movimento per gli altri della stanza di partenza
        self.others_out_message  = ""   # Messaggio di movimento per gli altri della stanza di arrivo
    #- Fine Inizializzazione -

    def get_error_message(self):
        """
        Se c'è un errore nell'uscita ne ritorna il messaggio appropriato.
        """
        if self.direction.get_error_message(DIR, "direction", allow_none=False) != "":
            msg = self.direction.get_error_message(DIR, "direction", allow_none=False)
        elif self.flags.get_error_message(EXIT, "flags") != "":
            msg = self.flags.get_error_message(EXIT, "flags")
#        elif (self.door and self.door.code not in database["items"]
#        and   self.door and self.door.code not in database["mobs"]):
#            msg = "door dell'uscita non è un oggetto valido: %s" % self.door.code
        elif self.destination and self.destination.get_error_message() != "":
            msg = self.destination.get_error_message()
        elif self.extras.get_error_message():
            msg = self.extras.get_error_message()
        else:
            return ""

        return "(exit %r): %s" % (self.direction, msg)
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Exit()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, exit2):
        # Non dovrebbe servire implementarli, ma inserisco questo "avviso" al caso
        raise NotImplementedError
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_icon(self, room=None):
        if room:
            door = room.get_door(self.direction)
        else:
            door = None

        icon = ""
        if door and door.door_type and DOOR.CLOSED in door.door_type.flags and DOOR.SECRET not in door.door_type.flags:
            # L'icone dell'entità porta è intesa come chiusa
            icon = door.get_icon()
            if not icon:
                icon = "icons/door/default-door.png"
        elif door and door.door_type and DOOR.CLOSED not in door.door_type.flags:
            # Icona della porta aperta
            icon = door.door_type.get_icon()
            if not icon:
                icon = "icons/door/default-door-open.png"
        elif not door or (door.door_type and DOOR.SECRET not in door.door_type.flags):
            if calendar.is_night() and self.icon_night:
                # icona dell'uscita di notte
                icon = self.icon_night
            elif self.icon:
                # icona dell'uscita di giorno
                icon = self.icon

        # Inserisce di default dei simboli di una rosa dei venti
        if not icon:
            icon = "icons/compass/%s.png" % repr(self.direction).split(".")[1].lower()

        return icon
    #- Fine Metodo -

    def get_descr(self, type="", looker=None):
        """
        Ritorna la descrizione dell'uscita.
        """
        if type:
            type = "_" + type

        descr = ""
        if calendar.is_night():
            descr = getattr(self, "descr%s_night" % type)
        if not descr:
            descr = getattr(self, "descr%s" % type)

        # Normale che possa accadere per qualsiasi tipologia di descrizione
        if not descr:
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


class Wall(Describable):
    """
    Classe per la gestione di un muro di stanza.
    """
    PRIMARY_KEY = "direction"
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"extras" : ("src.extra", "ExtraDescription")}
    REFERENCES  = {"maked_by"  : ["proto_items", "proto_mobs"]}
    WEAKREFS    = {}

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = False
    IS_EXIT   = False
    IS_WALL   = True
    IS_ACTOR  = False
    IS_MOB    = False
    IS_ITEM   = False
    IS_PLAYER = False
    IS_EXTRA  = False
    IS_PROTO  = False

    def __init__(self, direction=DIR.NONE):
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return

        # ---------------------------------------------------------------------

        self.comment             = ""  # Eventuale commento al muro
        self.direction           = Element(direction)  # Tipologia della direzione
        self.maked_by            = None  # Oggetto di base utilizzato nella costruzione del muro (di solito un mattone o una pietra)
        self.depth               = 0   # Profondità della parete, assieme al tipo di materiale in quella direzione ne fanno la forza, che serve nel caso si voglia romperlo, picconarlo, sfondarlo o farlo saltare in aria!
        self.height              = 0   # Altezza del muro, se differente dall'altezza della stanza
        self.descr               = ""  # Descrizione dell'uscita che viene a formarsi quando il muro viene sfondato
        self.descr_night         = ""  # Descrizione notturna dell'uscita che viene a formarsi quando il muro viene sfondato
        self.descr_hearing       = ""  # Descrizione uditiva
        self.descr_hearing_night = ""  # Descrizione uditiva notturna
        self.descr_smell         = ""  # Descrizione odorosa
        self.descr_smell_night   = ""  # Descrizione odorosa notturna
        self.descr_touch         = ""  # Descrizione tattile
        self.descr_touch_night   = ""  # Descrizione tattile notturna
        self.descr_taste         = ""  # Descrizione del sapore
        self.descr_taste_night   = ""  # Descrizione del sapore notturna
        self.descr_sixth         = ""  # Descrizione del sesto senso
        self.descr_sixth_night   = ""  # Descrizione del sesto senso notturna
        self.extras              = Extras()  # Elenco delle extra che si possono guardare o leggere sul muro
    #- Fine Inizializzazione -

    def get_error_message(self):
        """
        Se nell'instanza del muro c'è un errore ritorna il relativo messaggio.
        """
        if self.direction.get_error_message(DIR, "direction", allow_none=False) != "":
            msg = self.direction.get_error_message(DIR, "direction", allow_none=False)
        elif not self.maked_by:
            msg = "non esiste nessuna entità legata a maked_by"
        elif self.maked_by and self.maked_by.code not in database["proto_items"]:
            msg = "non esiste nessun oggetto prototipo dal codice %s" % self.maked_by.code
        elif self.depth <= 0:
            msg = "depth è una lunghezza e quindi non deve essere minore e uguale a 0: %d" % self.depth
        elif self.height <= 0:
            msg = "height è una lunghezza e quindi non deve essere minore e uguale a 0: %d" % self.height
        elif self.extras.get_error_message():
            msg = self.extras.get_error_message()
        else:
            return ""
        return "(wall %s): %s" % (self.direction, msg)
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Wall()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, wall2):
        # Non dovrebbe servire implementarli, ma inserisco questo "avviso" al caso
        raise NotImplementedError
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_descr(self, type="", looker=None):
        """
        Ritorna la descrizione del muro.
        """
        if type:
            type = "_" + type

        descr = ""
        if calendar.is_night():
            descr = getattr(self, "descr%s_night" % type)
        if not descr:
            descr = getattr(self, "descr%s" % type)

        # Normale che possa accadere per qualsiasi tipologia di descrizione
        if not descr:
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


#= FUNZIONI ====================================================================

def get_direction(arg, exact=False):
    """
    Passato un argomento ne ritorna la direzione corrispondente.
    """
    if not arg:
        log.bug("arg non è un parametro valido: %r con exact a %s" % (arg, exact))
        return DIR.NONE

    # -------------------------------------------------------------------------

    # Esegue prima una ricerca esatta
    if   arg == "north"     or arg == "nord":   return DIR.NORTH
    elif arg == "east"      or arg == "est":    return DIR.EAST
    elif arg == "south"     or arg == "sud":    return DIR.SOUTH
    elif arg == "west"      or arg == "ovest":  return DIR.WEST
    elif arg == "up"        or arg == "alto":   return DIR.UP
    elif arg == "down"      or arg == "basso":  return DIR.DOWN
    elif arg == "northeast" or arg == "nordest"   or arg == "ne":                 return DIR.NORTHEAST
    elif arg == "northwest" or arg == "nordovest" or arg == "nw" or arg == "no":  return DIR.NORTHWEST
    elif arg == "southeast" or arg == "sudest"    or arg == "se":                 return DIR.SOUTHEAST
    elif arg == "southwest" or arg == "sudovest"  or arg == "sw" or arg == "so":  return DIR.SOUTHWEST

    # Ora esegue una ricerca relativa al prefisso, se così è stato voluto
    if not exact:
        if   is_prefix(arg, "north"    ) or is_prefix(arg, "nord"     ):  return DIR.NORTH
        elif is_prefix(arg, "east"     ) or is_prefix(arg, "est"      ):  return DIR.EAST
        elif is_prefix(arg, "south"    ) or is_prefix(arg, "sud"      ):  return DIR.SOUTH
        elif is_prefix(arg, "west"     ) or is_prefix(arg, "ovest"    ):  return DIR.WEST
        elif is_prefix(arg, "up"       ) or is_prefix(arg, "alto"     ):  return DIR.UP
        elif is_prefix(arg, "down"     ) or is_prefix(arg, "basso"    ):  return DIR.DOWN
        elif is_prefix(arg, "northeast") or is_prefix(arg, "nordest"  ):  return DIR.NORTHEAST
        elif is_prefix(arg, "northwest") or is_prefix(arg, "nordovest"):  return DIR.NORTHWEST
        elif is_prefix(arg, "southeast") or is_prefix(arg, "sudest"   ):  return DIR.SOUTHEAST
        elif is_prefix(arg, "southwest") or is_prefix(arg, "sudovest" ):  return DIR.SOUTHWEST

    # Se non l'ha trovata ritorna None
    return DIR.NONE
#- Fine Funzione -


# (TD) forse utilizzarlo come metodo per la class Entity?
def get_destination_room_from_door(entity, door):
    """
    Ricava la stanza di destinazione relativa alla porta nella stanza in cui
    si trova entity.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None, None

    if not door:
        log.bug("door non è un parametro valido: %r" % door)
        return None, None

    # -------------------------------------------------------------------------

    entity_room = entity.location
    if not entity_room:
        return None, None

    if not entity_room.IS_ROOM:
        return None, None

    if not door.door_type:
        return None, None

    if not door.is_hinged():
        return None, None

    if not door.location.IS_ROOM:
        log.bug("Nonostante la porta %s non sia sui cardini non si trova in una room: %s" % (door.code, door.location.code))
        return None, None

    direction = None
    for direction in entity_room.exits:
        if entity_room.exits[direction].door == door:
            break
    else:
        # Altrimenti la porta si potrebbe trovarsi nel lato di un'altra stanza
        # e quindi la cerca come tale
        for direction in door.location.exits:
            if door.location.exits[direction].door == door:
                direction = direction.reverse_dir
                break
        else:
            return None, None

    destination = entity_room.get_destination(direction)
    if not destination:
        return None, None

    return destination.get_room(), direction
#- Fine Funzione -
