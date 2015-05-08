# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle descrizioni extra.
"""

#= IMPORT ======================================================================

from src.calendar import calendar
from src.color    import color_first_upper
from src.config   import config
from src.element  import Flags
from src.enums    import EXTRA
from src.log      import log
from src.miml     import MIMLParserSuperclass, MIML_SEPARATOR
from src.utility  import (is_same, is_prefix, multiple_arguments, put_final_dot,
                          copy_existing_attributes)


#= CLASSI ======================================================================

class Extras(list):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    # In teoria copy e equals non vengono utilizza
    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Extras()

        for value in self:
            try:
                copied_value = value.copy()
            except:
                copied_value = copy.copy(value)
            to_obj.append(copied_value)

        return to_obj
    #- Fine Metodo -

    def equals(self, extras2):
        if not self and extras2:
            return False
        if self and not extras2:
            return False

        if len(self) != len(extras2):
            return False
        for value in self:
            for value2 in extras2:
                if value.equals(value2):
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    def get_error_message(self):
        """
        Controlla tutte le descrizioni extra passate e se trova un errore ne
        ritorna il relativo messaggio.
        """
        for extra in self:
            msg = extra.get_error_message()
            if msg:
                return "(extra: %s) %s" % (extra.keywords, msg)
        return ""
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_extra(self, argument, exact=False):
        """
        Cerca un'extra particolare tramite l'argomento passato, esegue la ricerca
        in maniera esatta oppure anche in maniera prefissa.
        Questa funzione è da chiamare dai metodi get_extra delle stanze e delle
        entità.
        """
        if not argument:
            log.bug("argument non è un parametro valido: %s" % argument)
            return None

        # -------------------------------------------------------------------------

        for extra in self:
            if is_same(multiple_arguments(extra.keywords), argument):
                return extra

        # Se viene passato un argomento lungo un solo carattere allora non viene
        # eseguita la ricerca prefissa, questo per evitare che i player eseguano
        # un brute force per trovare eventuali extra nascoste (look a, look b,
        # look c, look d...)
        if not exact and len(argument) >= config.min_secret_arg_len:
            for extra in self:
                if is_prefix(argument, multiple_arguments(extra.keywords)):
                    return extra

        return None
    #- Fine Metodo -


class ExtraDescription(MIMLParserSuperclass):
    """
    Gestisce una descrizione extra.
    """
    PRIMARY_KEY = "keywords"
    VOLATILES   = []
    MULTILINES  = ["comment", "descr", "descr_night", "descr_hearing", "descr_hearing_night",
                   "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night",
                   "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night"]
    SCHEMA      = {}
    REFERENCES  = {"author" : ["players", "proto_mobs", "proto_items"]}
    WEAKREFS    = {}

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = False
    IS_EXIT   = False
    IS_WALL   = False
    IS_ACTOR  = False
    IS_MOB    = False
    IS_ITEM   = False
    IS_PLAYER = False
    IS_EXTRA  = True
    IS_PROTO  = False

    def __init__(self, keywords=""):
        if not keywords and keywords != "":
            log.bug("keywords passato non è una stringa valida: %s" % keywords)
            return

        # ---------------------------------------------------------------------

        self.comment             = ""  # Eventuale commento alle extra
        self.keywords            = keywords  # Parole chiave con cui accedere all'extra
        self.descr               = ""  # Descrizione diurna
        self.descr_night         = ""  # Descrizione notturna
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
        self.flags               = Flags(EXTRA.NONE)  # Flag per indicare la tipologia di extra e altre proprietà particolari
        self.author              = None  # Entità che ha scritto, o disegnato, l'extra
    #- Fine Inizializzazione -

    def get_error_message(self):
        # E' possibile evitare di inserire sia la descrizione notturna che
        # quella diurna di ognuno dei 6 sensi, (TD) cmq almeno una descr ci
        # deve essere
        msg = ""
        if not self.keywords:
            msg = "keywords di extra non valida"
        # Non bisogna controllare neppure la descr perché potrebbe essere
        # EXTRA.NIGHT_ONLY (TD) fare un check migliore
        elif self.flags.get_error_message(EXTRA, "flags") != "":
            msg = self.flags.get_error_message(EXTRA, "flags")
        return msg
    #- Fine Funzione -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = ExtraDescription()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Funzione -

    def equals(self, extra2):
        if not extra2:
            return False

        items1 = self.__dict__.items()
        items2 = extra2.__dict__.items()
        if len(items1) != len(items2):
            return False
        for attr, value in items1:
            if getattr(extra2, attr) != value:
                return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_descr(self, type="", looker=None, parent=None):
        """
        Ritorna la descrizione dell'extra.
        """
        if type:
            type = "_" + type

        if calendar.is_night():
            descr_night = getattr(self, "descr%s_night" % type)
            if descr_night:
                return put_final_dot(color_first_upper(descr_night))
            elif EXTRA.DAY_ONLY in self.flags:
                return ""

        # Non c'è bisogno di implementare la EXTRA.DAY_ONLY perché
        # concettualmente già funziona così, l'ho aggiunta perché i builder
        # si trovano meglio a inserirla esplicitamente in alcuni casi

        descr = getattr(self, "descr%s" % type)

        if MIML_SEPARATOR in descr:
            if parent:
                descr = parent.parse_miml(descr, looker)
            else:
                log.bug("Anche se il parametro è opzionale è inteso come dovuto: %r" % parent)

        if descr:
            return put_final_dot(color_first_upper(descr))
        else:
            # Può accadere quando il type è una stringa indicante un senso
            # differente da quello della vista
            return ""
    #- Fine Metodo -
