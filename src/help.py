# -*- coding: utf-8 -*-

"""
Modulo per la gestione degli argomenti richiamabili con il comando help.
"""

#= IMPORT ======================================================================

from src.data     import Data
from src.database import database
from src.element  import Element
from src.enums    import HELP
from src.utility  import is_same, is_prefix, multiple_arguments


#= CLASSI ======================================================================

class Help(Data):
    """
    Classe relativa un contenuto di help.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ["syntax_function"]
    MULTILINES  = ["text", "admin_text"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment          = ""
        self.code             = ""   # Codice identificativo dell'help
        self.italian_keywords = ""   # Parole di ricerca italiane
        self.english_keywords = ""   # Parole di ricerca inglesi
        self.type             = Element(HELP.NONE)  # Tipologia dell'help
        self.text             = ""   # Testo visualizzato da tutti
        self.admin_text       = ""   # Testo visualizzato solo dagli Admin
        self.see_also         = ""   # Voci degli help simili a questo
        self.counter_use      = 0    # Contatore dell'utilizzo dell'help
        self.syntax_function  = None # Eventuale funzione che fa visualizzare la sintassi del comando
    #- Fine Inizializzazione -

    def get_error_message(self):
        if not self.code:
            return "code non è valido: %r" % self.code
        elif not self.italian_keywords:
            return "italian_keywords non è valido: %r" % self.italian_keywords
        elif not self.english_keywords:
            return "english_keywords non è valido: %r" % self.english_keywords
        elif not self.type or self.type == HELP.NONE:
            return "type non è valido: %r" % self.type
        elif not self.text and not self.admin_text and not self.see_also:
            return "nessun testo valido per l'help"
        elif self.counter_use < 0:
            return "counter_use non è una quantità valida: %d" % self.counter_use
        # (TD) controllare anche che i codici di see_also esistano

        return ""
    #- Fine Metodo -

    def bind_syntax_function(self):
        # (TD)
        pass
    #- Fine Metodo -


# (TT) c'è da controllare se ricava correttamente le parole chiave inserite tra ''
def get_help(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    # Se argument è formato da più parole erroneamente separate da più spazi
    # allora li converte in un'unico spazio
    if "  " in argument:
        argument = " ".join(argument.split())

    # Cerca prima tra gli help della propria lingua in maniera esatta
    if entity.IS_PLAYER or OPTION.ITALIAN in entity.account.options:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_same(argument, multiple_arguments(help.italian_keywords)):
                return help
    else:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_same(argument, multiple_arguments(help.english_keywords)):
                return help

    # Cerca poi tra gli help della propria lingua in maniera prefissa
    if entity.IS_PLAYER or OPTION.ITALIAN in entity.account.options:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_prefix(argument, multiple_arguments(help.italian_keywords)):
                return help
    else:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_prefix(argument, multiple_arguments(help.english_keywords)):
                return help

    # Cerca poi tra gli help della lingua secondaria in maniera esatta
    if entity.IS_PLAYER or OPTION.ITALIAN in entity.account.options:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_same(argument, multiple_arguments(help.english_keywords)):
                return help
    else:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_same(argument, multiple_arguments(help.italian_keywords)):
                return help

    # Cerca poi tra gli help della lingua secondaria in maniera prefissa
    if entity.IS_PLAYER or OPTION.ITALIAN in entity.account.options:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_prefix(argument, multiple_arguments(help.english_keywords)):
                return help
    else:
        for help in database["helps"].itervalues():
            if not help.text and help.admin_text and entity.trust == TRUST.PLAYER:
                continue
            if is_prefix(argument, multiple_arguments(help.italian_keywords)):
                return help

    return None
#- Fine Funzione -


def sort_helps_alphabetically(language):
    # (TD)
    pass
#- Fine Funzione -


def find_no_helps():
    """
    Ritorna tutti i comandi, skill, spell, razze e altro che non hanno un
    proprio help.
    """
    # (TD)
    pass
#- Fine Funzione -
