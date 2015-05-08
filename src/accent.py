# -*- coding: utf-8 -*-

"""
Modulo per la gestione degli accenti.
"""


#= COSTANTI ====================================================================

# (TD) Questo dizionario servirebbe per una futura eventuale velocizzazione della remove_accents
ACCENTS_MAP = {
    "\xC0" : "A",
    "\xC1" : "A",
    "\xC8" : "E",
    "\xC9" : "E",
    "\xCC" : "I",
    "\xCD" : "I",
    "\xD2" : "O",
    "\xD3" : "O",
    "\xD9" : "U",
    "\xDA" : "U",
    "À"    : "A",
    "Á"    : "A",
    "È"    : "E",
    "É"    : "E",
    "Ì"    : "I",
    "Í"    : "I",
    "Ò"    : "O",
    "Ó"    : "O",
    "Ù"    : "U",
    "Ú"    : "U",
    "\xE0" : "a",
    "\xE1" : "a",
    "\xE8" : "e",
    "\xE9" : "e",
    "\xEC" : "i",
    "\xED" : "i",
    "\xF2" : "o",
    "\xF3" : "o",
    "\xF9" : "u",
    "\xFA" : "u",
    "à"    : "a",
    "á"    : "a",
    "è"    : "e",
    "é"    : "e",
    "ì"    : "i",
    "í"    : "i",
    "ò"    : "o",
    "ó"    : "o",
    "ù"    : "u",
    "ú"    : "u",
    "a'"   : "a",
    "e'"   : "e",
    "i'"   : "i",
    "o'"   : "o",
    "u'"   : "u",
    "A'"   : "A",
    "E'"   : "E",
    "I'"   : "I",
    "O'"   : "O",
    "U'"   : "U"}

ACCENTS = [c for c in ACCENTS_MAP.keys() if len(c) == 1]


#= FUNZIONI ====================================================================

def count_accents(argument):
    """
    Ritorna il numero di accenti trovati nell'argomento passato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    counter = 0

    for c in argument:
        if c in ACCENTS:
            counter += 1

    return counter
#- Fine Funzione -


def isalpha_accent(argument):
    """
    Ritorna vero se la stringa passata ha solo lettere accentate o alfabetiche.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    for c in argument:
        if c.isalpha():
            continue
        if c not in ACCENTS:
            return False

    return True
#- Fine Funzione -


def dummy_isalpha_accent(argument):
    """
    Ritorna vero se la stringa passata ha solo lettere accentate o alfabetiche.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    for n, c in enumerate(argument):
        is_accent = True

        print argument, c, n, len(argument)
        if c not in ACCENTS:
            if n == len(argument)-1:
                return False
            print "A"
            is_accent = False

        if not is_accent and c + argument[n+1] not in ACCENTS:
            print "B"
            is_accent = False

        if not is_accent and not c.isalpha():
            print "C"
            return False

    print "D"
    return True
#- Fine Funzione -


def isalnum_accent(argument):
    """
    Ritorna vero se la stringa passata ha solo lettere accentato o alfabetiche
    o numeriche.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    for c in argument:
        if c.isalnum():
            continue
        if c not in ACCENTS:
            return False

    return True
#- Fine Funzione -


# (TD) Qui per velocizzare tale funzione al posto del metodo replace
# bisognerebbe utilizzare una regex
def remove_accents(argument):
    """
    Rimuove tutti gli accenti (unicode, ascii o "apostrofati") da una stringa.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    if "\xC0" in argument:  argument = argument.replace("\xC0", "A")  # À
    if "\xC1" in argument:  argument = argument.replace("\xC1", "A")  # Á
    if "\xC8" in argument:  argument = argument.replace("\xC8", "E")  # È
    if "\xC9" in argument:  argument = argument.replace("\xC9", "E")  # É
    if "\xCC" in argument:  argument = argument.replace("\xCC", "I")  # Ì
    if "\xCD" in argument:  argument = argument.replace("\xCD", "I")  # Í
    if "\xD2" in argument:  argument = argument.replace("\xD2", "O")  # Ò
    if "\xD3" in argument:  argument = argument.replace("\xD3", "O")  # Ó
    if "\xD9" in argument:  argument = argument.replace("\xD9", "U")  # Ù
    if "\xDA" in argument:  argument = argument.replace("\xDA", "U")  # Ú

    if "À" in argument:     argument = argument.replace("À", "A")
    if "Á" in argument:     argument = argument.replace("Á", "A")
    if "È" in argument:     argument = argument.replace("È", "E")
    if "É" in argument:     argument = argument.replace("É", "E")
    if "Ì" in argument:     argument = argument.replace("Ì", "I")
    if "Í" in argument:     argument = argument.replace("Í", "I")
    if "Ò" in argument:     argument = argument.replace("Ò", "O")
    if "Ó" in argument:     argument = argument.replace("Ó", "O")
    if "Ù" in argument:     argument = argument.replace("Ù", "U")
    if "Ú" in argument:     argument = argument.replace("Ú", "U")

    if "\xE0" in argument:  argument = argument.replace("\xE0", "a")  # à
    if "\xE1" in argument:  argument = argument.replace("\xE1", "a")  # á
    if "\xE8" in argument:  argument = argument.replace("\xE8", "e")  # è
    if "\xE9" in argument:  argument = argument.replace("\xE9", "e")  # é
    if "\xEC" in argument:  argument = argument.replace("\xEC", "i")  # ì
    if "\xED" in argument:  argument = argument.replace("\xED", "i")  # í
    if "\xF2" in argument:  argument = argument.replace("\xF2", "o")  # ò
    if "\xF3" in argument:  argument = argument.replace("\xF3", "o")  # ó
    if "\xF9" in argument:  argument = argument.replace("\xF9", "u")  # ù
    if "\xFA" in argument:  argument = argument.replace("\xFA", "u")  # ú

    if "à" in argument:     argument = argument.replace("à", "a")
    if "á" in argument:     argument = argument.replace("á", "a")
    if "è" in argument:     argument = argument.replace("è", "e")
    if "é" in argument:     argument = argument.replace("é", "e")
    if "ì" in argument:     argument = argument.replace("ì", "i")
    if "í" in argument:     argument = argument.replace("í", "i")
    if "ò" in argument:     argument = argument.replace("ò", "o")
    if "ó" in argument:     argument = argument.replace("ó", "o")
    if "ù" in argument:     argument = argument.replace("ù", "u")
    if "ú" in argument:     argument = argument.replace("ú", "u")

    if "A'" in argument:    argument = argument.replace("A'", "A")
    if "E'" in argument:    argument = argument.replace("E'", "E")
    if "I'" in argument:    argument = argument.replace("I'", "I")
    if "O'" in argument:    argument = argument.replace("O'", "O")
    if "U'" in argument:    argument = argument.replace("U'", "U")

    if "a'" in argument:    argument = argument.replace("a'", "a")
    if "e'" in argument:    argument = argument.replace("e'", "e")
    if "i'" in argument:    argument = argument.replace("i'", "i")
    if "o'" in argument:    argument = argument.replace("o'", "o")
    if "u'" in argument:    argument = argument.replace("u'", "u")

    return argument
#- Fine Funzione -


def accents_escape(text):
    if not text:
        log.bug("text non è un parametro valido: %r" % text)
        return ""

    # -------------------------------------------------------------------------

    if "\xC0" in text:  text = text.replace("\xC0", "&Agrave;")  # À
    if "\xC1" in text:  text = text.replace("\xC1", "&Aacute;")  # Á
    if "\xE0" in text:  text = text.replace("\xE0", "&agrave;")  # à
    if "\xE1" in text:  text = text.replace("\xE1", "&aacute;")  # á

    if "À" in text:     text = text.replace("À", "&Agrave;")
    if "Á" in text:     text = text.replace("Á", "&Aacute;")
    if "à" in text:     text = text.replace("à", "&agrave;")
    if "á" in text:     text = text.replace("á", "&aacute;")

    if "\xC8" in text:  text = text.replace("\xC8", "&Egrave;")  # È
    if "\xC9" in text:  text = text.replace("\xC9", "&Eacute;")  # É
    if "\xE8" in text:  text = text.replace("\xE8", "&egrave;")  # è
    if "\xE9" in text:  text = text.replace("\xE9", "&eacute;")  # é

    if "È" in text:     text = text.replace("È", "&Egrave;")
    if "É" in text:     text = text.replace("É", "&Eacute;")
    if "è" in text:     text = text.replace("è", "&egrave;")
    if "é" in text:     text = text.replace("é", "&eacute;")

    if "\xCC" in text:  text = text.replace("\xCC", "&Igrave;")  # Ì
    if "\xCD" in text:  text = text.replace("\xCD", "&Iacute;")  # Í
    if "\xEC" in text:  text = text.replace("\xEC", "&igrave;")  # ì
    if "\xED" in text:  text = text.replace("\xED", "&iacute;")  # í

    if "Ì" in text:     text = text.replace("Ì", "&Igrave;")
    if "Í" in text:     text = text.replace("Í", "&Iacute;")
    if "ì" in text:     text = text.replace("ì", "&igrave;")
    if "í" in text:     text = text.replace("í", "&iacute;")

    if "\xD2" in text:  text = text.replace("\xD2", "&Ograve;")  # Ò
    if "\xD3" in text:  text = text.replace("\xD3", "&Oacute;")  # Ó
    if "\xF2" in text:  text = text.replace("\xF2", "&ograve;")  # ò
    if "\xF3" in text:  text = text.replace("\xF3", "&oacute;")  # ó

    if "Ò" in text:     text = text.replace("Ò", "&Ograve;")
    if "Ó" in text:     text = text.replace("Ó", "&Oacute;")
    if "ò" in text:     text = text.replace("ò", "&ograve;")
    if "ó" in text:     text = text.replace("ó", "&oacute;")

    if "\xD9" in text:  text = text.replace("\xD9", "&Ugrave;")  # Ù
    if "\xDA" in text:  text = text.replace("\xDA", "&Uacute;")  # Ú
    if "\xF9" in text:  text = text.replace("\xF9", "&ugrave;")  # ù
    if "\xFA" in text:  text = text.replace("\xFA", "&uacute;")  # ú

    if "Ù" in text:     text = text.replace("Ù", "&Ugrave;")
    if "Ú" in text:     text = text.replace("Ú", "&Uacute;")
    if "ù" in text:     text = text.replace("ù", "&ugrave;")
    if "ú" in text:     text = text.replace("ú", "&uacute;")

    return text
#- Fine Funzione -
