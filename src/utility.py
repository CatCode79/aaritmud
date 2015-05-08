# -*- coding: utf-8 -*-

"""
Modulo contenente funzioni di varia utilità.
"""


#= IMPORT ======================================================================

import cgi
import copy
import datetime
import HTMLParser
import locale
import math
import random
import re
import os
import sys
import types
import weakref

from src.accent import remove_accents
from src.log    import log

# Lazy import:
remove_colors = None


#= FUNZIONI ====================================================================

def clean_string(argument):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    argument = remove_accents(argument)

    if "[" in argument:
        global remove_colors
        if not remove_colors:
            from src.color import remove_colors
        argument = remove_colors(argument)

    return argument.lower()
#- Fine Funzione -


def _compare_handler(string_list1, string_list2):
    """
    Riguardo alle funzioni di confronto tra stringhe:
    - Il confronto ignora le regole di stile css del Mud
    - Il confronto non è case-sensitive
    - Il confronto non è 'accent-sensitive', nel senso che le stringhe abilità,
      abilita' e abilita verranno considerate uguali.
    """
    if not string_list1:
        log.bug("string_list1 non è valido: %r con string_list2: %r" % (string_list1, string_list2))
        yield "", ""

    if not string_list2:
        log.bug("string_list2 non è valido: %s con string_list1: %r" % (string_list2, string_list1))
        yield "", ""

    # -------------------------------------------------------------------------

    # Se gli argomenti passati hanno il metodo zfill vengono considerati
    # come stringhe, altrimenti probabilmente sono già delle sequenze
    try:
        string_list1.zfill
        string_list1 = (string_list1, )
    except AttributeError:
        pass

    try:
        string_list2.zfill
        string_list2 = (string_list2, )
    except AttributeError:
        pass

    for arg1 in string_list1:
        arg1 = clean_string(arg1)
        for arg2 in string_list2:
            arg2 = clean_string(arg2)
            yield arg1, arg2
#- Fine Funzione -


def is_same(string_list1, string_list2):
    """
    Ritorna vero se le due stringhe sono uguali.
    """
    if not string_list1:
        log.bug("string_list1 non è un parametro valido: %r" % string_list1)
        return False

    if not string_list2:
        log.bug("string_list2 non è un parametro valido: %r" % string_list2)
        return False

    # -------------------------------------------------------------------------

    for arg1, arg2 in _compare_handler(string_list1, string_list2):
        if arg1 == arg2:
            return True
    return False
#- Fine Funzione -


def is_prefix(string_list1, string_list2):
    """
    Ritorna vero se string1 è prefisso di string2.
    """
    if not string_list1:
        log.bug("string_list non è valido: %r" % string_list1)
        return False

    if not string_list2:
        log.bug("string_list non è valido: %r" % string_list2)
        return False

    # -------------------------------------------------------------------------

    for arg1, arg2 in _compare_handler(string_list1, string_list2):
        # (TD) attivarlo solo per le stringhe del codice e non quelle
        # inserite dagli utenti, dovrebbe essere possibile tramite il
        # modulo inspect
        #if len(arg1) > len(arg2):
        #    log.bug("arg1 (%s) è maggiore di arg2 (%s)" % (arg1, arg2))
        #    return False
        if arg2.startswith(arg1):
            return True
    return False
#- Fine Funzione -


def is_infix(string_list1, string_list2):
    """
    Ritorna vero se string1 si trova dentro la string2.
    """
    if not string_list1:
        log.bug("string_list1 non è un parametro valido: %r" % string_list1)
        return False

    if not string_list2:
        log.bug("string_list2 non è un parametro valido: %r" % string_list2)
        return False

    # -------------------------------------------------------------------------

    for arg1, arg2 in _compare_handler(string_list1, string_list2):
        # (TD) anche qui come is_prefix
        #if len(arg1) > len(arg2):
        #    log.bug("arg1 (%s) è maggiore di arg2 (%s)" % (arg1, arg2))
        #    return False
        if arg1 in arg2:
            return True
    return False
#- Fine Funzione -


def is_suffix(string_list1, string_list2):
    """
    Ritorna vero se la string1 è suffissa alla string2.
    """
    if not string_list1:
        log.bug("string_list non è valido: %r" % string_list1)
        return False

    if not string_list2:
        log.bug("string_list non è valido: %r" % string_list2)
        return False

    # -------------------------------------------------------------------------

    for arg1, arg2 in _compare_handler(string_list1, string_list2):
        # (TD) anche qui come is_prefix
        #if len(arg1) > len(arg2):
        #    log.bug("arg1 (%s) è maggiore di arg2 (%s)" % (arg1, arg2))
        #    return False
        if arg2.endswith(arg1):
            return True
    return False
#- Fine Funzione -


#-------------------------------------------------------------------------------

def from_capitalized_words(argument):
    """
    Converte l'argomento, da stile CapWords in stile lower_case_with_underscores.
    """
    if not argument:
        log.bug("argument non è valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    new_argument = ""
    for i, char in enumerate(argument):
        if char.isupper() and i != 0:
            new_argument += "_"
        new_argument += char.lower()
    return new_argument
#- Fine Funzione -


def to_capitalized_words(argument):
    """
    Converte l'argomento passato da stile lower_case_with_underscores in
    stile CapWords.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    new_argument = ""
    capital = True
    for c in argument:
        if c == "_":
            capital = True
            continue
        if capital:
            c = c.upper()
            capital = False
        new_argument += c
    return new_argument
#- Fine Funzione -


#-------------------------------------------------------------------------------

def one_argument(argument, search_separator=True):
    """
    Passato l'argomento lo spezza in due parti ritornandole con una tupla di
    due valori.
    Il primo valore è la prima parola delimitata da uno spazio o all'interno
    degli apici o da delle virgolette, tutto il resto è la seconda parte.
    Utilizzare questa funzione al posto del metodo di stringa split(None, 1)
    quando c'è bisogno del supporto di ricerca di questo tipo:
    get 'spada rossa'
    """
    if not argument:
        if argument != "":
            log.bug("argument non è un parametro valido: %r" % argument)
        return "", ""

    # -------------------------------------------------------------------------

    separator = " "
    start = 0
    if search_separator and argument[0] == '"':
        separator = '"'
        start = 1
    elif search_separator and argument[0] == "'":
        separator = "'"
        start = 1
    elif argument[0] == " ":
        log.bug("argument inizia con uno spazio: %s" % argument)
        start = 1

    length = 0
    for c in argument[start : ]:
        if c == separator:
            break
        length += 1

    # Se argument era formata da una sola parola ritornerà come primo valore
    # la parola stessa e come secondo una stringa vuota
    return argument[start : length+1].strip(), argument[length+start+1 : ].strip()
#- Fine Funzione -


def reverse_one_argument(argument, search_separator=True):
    """
    Come la one_argument, ma esegue la ricerca partendo dal fondo.
    """
    if not argument:
        if argument != "":
            log.bug("argument non è un parametro valido: %r" % argument)
        return "", ""

    # -------------------------------------------------------------------------

    separator = " "
    end = len(argument)
    if search_separator and argument[-1] == '"':
        separator = '"'
        end = len(argument) - 1
    elif search_separator and argument[-1] == "'":
        separator = "'"
        end = len(argument) - 1
    elif argument[-1] == " ":
        log.bug("argument finisce con uno spazio: %s" % argument)
        end = len(argument) - 1

    length = 0
    for c in reversed(argument[ : end]):
        if c == separator:
            break
        length += 1

    return argument[ : end-length].strip(), argument[end-length : end].strip()
#- Fine Funzione -


def multiple_arguments(argument, max_split=256):
    """
    Passata una stringa ritorna una lista di stringhe spezzate dalla
    one_argument.
    Utilizzare questa funzione al posto del semplice metodo di stringa split
    quando si ha bisogno del supporto delimitatori apici-virgolette della
    one_argument.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return []

    if max_split <= 0 or max_split > 256:
        log.bug("max_split non è un parametro valido: %r" % max_split)
        return []

    # -------------------------------------------------------------------------

    if max_split == 1:
        log.bug("E' meglio utilizzare la one_argument al posto di questa funzione con max_split a 1")

    list_of_args = []
    while max_split:
        arg, argument = one_argument(argument)
        list_of_args.append(arg)
        if not argument:
            break
        max_split -= 1

    return list_of_args
#- Fine Funzione -


def number_argument(argument):
    """
    Se l'argomento passato è una stringa di questo tipo:
    2.spada
    ritorna 2 e spada.
    Non esegue controlli sul numero ricavato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return -1, ""

    # -------------------------------------------------------------------------

    number = 1
    original_argument = argument

    if "." in argument:
        number, argument = argument.split(".", 1)
        if not number or not is_number(number) or not argument:
            return 1, original_argument

        # Se il numero è minore di zero, allora non lo considera e ritorna
        # tutto l'argomento
        number = int(number)
        if number < 1:
            return 1, original_argument

    return number, argument
#- Fine Funzione -


def quantity_argument(argument):
    """
    Ritorna il numero voluto di 'argument'.
    """
    original_argument = argument

    if "." in argument:
        arg, argument = argument.split(".", 1)
        if arg.lower() in ("tutto", "tutta", "tutti", "tutte", "all"):
            return 0, argument
        argument = original_argument

    arg, argument = one_argument(argument)
    if is_number(arg) and int(arg) > 0:
        return int(arg), argument
    else:
        return 1, original_argument
#- Fine Funzione -


# (TD) controllare se sia possibile utilizzare la math.isnan al suo posto, da python 2.6
def is_number(argument):
    """
    Ritorna se è un numero decimale eseguendo dei controlli meno permissivi
    rispetto alla int.
    Non accetta spazi ad inizio e fine della stringa passato e accetta solamente
    le 10 cifre e il simbolo del più e quello del meno.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    if argument[0] not in "1234567890+-":
        return False

    for c in argument[1 : ]:
        if c not in "1234567890":
            return False

    return True
#- Fine Funzione -


def number_fuzzy(number, fuzzy_value=1):
    n = random.randint(1, 4)
    if n == 1:
        return number - fuzzy_value
    elif n == 4:
        return number + fuzzy_value
    else:
        return number
#- Fine Funzione -


def dice(argument, for_debug=None):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return 0

    # -------------------------------------------------------------------------

    argument = argument.lower()
    if "d" in argument:
        dice_qty, dice_size = argument.split("d", 1)
    else:
        log.bug("Non è stata passata un'espressione dice valida: %s (for_debug=%s)" % (argument, for_debug))
        return 0

    addend = ""
    if "+" in dice_size:
        dice_size, addend = dice_size.rsplit("+", 1)
    elif "-" in dice_size:
        dice_size, addend = dice_size.rsplit("-", 1)
        addend = "-" + addend

    dice_qty  = int(dice_qty)
    dice_size = int(dice_size)
    addend    = int(addend)

    result = 0
    while dice_qty > 0:
        result += random.randint(1, dice_size)
        dice_qty -= 1
    return result + addend
#- Fine Funzione -


#-------------------------------------------------------------------------------

def pretty_date(past=None, clock=True):
    """
    Ritorna una stringa con la data formattata.
    Accetta sia oggetti date che datetime.
    """

    if not past:
        if clock:
            past = datetime.datetime.now()
        else:
            past = datetime.date.today()

    # Ricava la data di oggi e la differenza con la data passata
    today = datetime.date.today()
    diff = today - datetime.date(past.year, past.month, past.day)

    # Riformattazione la data in maniera "carina" e maggiormente leggibile
    if diff.days == 0:
        result = "oggi"
    elif diff.days == 1:
        result = "ieri"
    elif today.year != past.year:
        result = "il %d/%d/%d" % (past.day, past.month, past.year)
    else:
        result = "il %d/%d" % (past.day, past.month)

    # Stampa anche l'ora se è voluta ed è possibile farlo
    if clock and hasattr(past, "hour"):
        result += " alle %d:%02d" % (past.hour, past.minute)

    return result
#- Fine Funzione -


def copy_existing_attributes(from_obj, to_obj, except_these_attrs=None, avoid_volatiles=False):
    """
    Copia il valore tutti gli attributi di from_obj esistenti anche in to_obj.
    Questa funzione serve ad implementare in maniera generica il prototype
    pattern per le entità in-game.
    """
    if from_obj is None:
        log.bug("from_obj non è un parametro valido: %r" % from_obj)
        return

    if to_obj is None:
        log.bug("to_obj non è un parametro valido: %r" % to_obj)
        return

    # -------------------------------------------------------------------------

    if except_these_attrs is None:
        except_these_attrs = []
    if avoid_volatiles and hasattr(from_obj, "VOLATILES"):
        for volatile in from_obj.VOLATILES:
            except_these_attrs.append(volatile)

    for attr_name, attr in from_obj.__dict__.iteritems():
        if attr_name in except_these_attrs:
            continue
        if attr_name not in to_obj.__dict__:
            continue

        if attr_name in to_obj.REFERENCES:
            if attr.__class__.__name__ == "dict":
                copied_attr = {}
                for key, value in attr.iteritems():
                    copied_attr[key] = value
            elif attr.__class__.__name__ == "list":
                copied_attr = []
                for value in attr:
                    copied_attr.append(value)
            else:
                copied_attr = attr
            setattr(to_obj, attr_name, copied_attr)
        elif attr_name in to_obj.WEAKREFS:
            if attr.__class__.__name__ == "dict":
                copied_attr = {}
                for key, value in attr.iteritems():
                    if value and value():
                        copied_attr[key] = weakref.ref(value())
                    else:
                        copied_attr[key] = None
            elif attr.__class__.__name__ == "list":
                copied_attr = []
                for value in attr:
                    if value and value:
                        copied_attr.append(weakref.ref(value))
                    else:
                        copied_attr.append(None)
            else:
                if attr and attr():
                    copied_attr = weakref.ref(attr())
                else:
                    copied_attr = None
            setattr(to_obj, attr_name, copied_attr)
        elif attr.__class__.__name__ == "dict":
            copied_attr = {}
            for key, value in attr.iteritems():
                if hasattr(value, "copy"):
                    copied_value = value.copy()
                else:
                    copied_value = copy.copy(value)
                copied_attr[key] = copied_value
            setattr(to_obj, attr_name, copied_attr)
        elif attr.__class__.__name__ == "list":
            copied_attr = []
            for value in attr:
                try:
                    copied_value = value.copy()
                except:
                    copied_value = copy.copy(value)
                copied_attr.append(copied_value)
            setattr(to_obj, attr_name, copied_attr)
        elif hasattr(attr, "copy"):
            copied_attr = attr.copy(avoid_volatiles=avoid_volatiles)
            setattr(to_obj, attr_name, copied_attr)
        else:
            copied_attr = copy.copy(attr)
            setattr(to_obj, attr_name, copied_attr)
#- Fine Funzione -


def getattr_from_path(obj, path):
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return None

    if not path:
        log.bug("path non è un parametro valido: %r" % path)
        return None

    # -------------------------------------------------------------------------

    for attr_name in path.split("."):
        obj = getattr(obj, attr_name)
        if not obj:
            return None

    return obj
#- Fine Funzione -


def import_from_anywhere(full_path):
    """
    Importa un file passandogli una path completa.
    Permette di importare da qualsiasi punto, una cosa che __import__ non fa.
    """
    if not full_path:
        log.bug("full_path non è un parametro valido: %r" % full_path)
        return None

    # -------------------------------------------------------------------------

    path, filename = os.path.split(full_path)
    filename, ext = os.path.splitext(filename)
    # Usa l'insert così da non importare il file sbagliato nel qual caso che fallisca
    sys.path.insert(0, path)
    module = __import__(filename)
    # Potrebbe non essere aggiornato quindi lo ricarica
    reload(module)
    del sys.path[0]
    return module
#- Fine Funzione -


def get_module_functions(module):
    if not module:
        log.bug("module non è un parametro valido: %r" % module)
        return {}

    # -------------------------------------------------------------------------

    functions = {}
    for key, value in module.__dict__.iteritems():
        if type(value) is types.FunctionType:
            functions[key] = value

    return functions
#- Fine Funzione -


def get_percent(value, max_value):
    """
    Ritorna un numero che rappresenta la percentuale del valore passato
    rispetto al suo potenziale massimo.
    """
    if max_value == 0:
        log.bug("max_value non è un parametro valido: 0")
        return 0

    # -------------------------------------------------------------------------

    if value > 0 and max_value < 0:
        max_value = math.mod(max_value)
        return 100 + ((value * 100) / max_value)
    elif value < 0 and max_value < 0:
        value = math.mod(value)
        max_value = math.mod(max_value)
        return -((value * 100) / max_value)
    else:
        return (value * 100) / max_value
#- Fine Funzione -


def get_index_of_shortest_string(values, avoid_zeros=True):
    """
    Passata una lista di stringhe ritorna l'indice di quella più corta.
    Se vengono trovati più valori con la stessa lunghezza ritorna il primo.
    """
    if not values:
        log.bug("values non è un parametro valido: %r" % values)
        return

    # avoid_zeros ha valore di verità

    # -------------------------------------------------------------------------

    shortest_index = 0
    shortest_length = len(values[0])
    for index, value in enumerate(values[1 : ]):
        if avoid_zeros and value[0] == "0":
            continue
        length = len(values[index])
        if shortest_length > length:
            shortest_length = length
            shortest_index = index

    return shortest_index
#- Fine Funzione -


# Credits to: http://www.djangosnippets.org/snippets/19/
URL_PATTERN = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocol>(^|\s)((www.|http://|https://|ftp://|ftps://|telnet://).*?))(\s|$)', re.S|re.M|re.I)

def convert_urls(text, tabstop=4):
    if not text:
        log.bug("text non è un parametro valido: %r" % text)
        return ""

    if tabstop < 2 or tabstop > 16:
        log.bug("tabstop non è un parametro valido: %r" % tabstop)
        return ""

    # -------------------------------------------------------------------------

    if ("www." not in text and "http://" not in text and "https://" not in text
    and "ftp://" not in text and "ftps://" not in text and "telnet://" not in text):
        return text

    def substitute(match):
        c = match.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            return '<br>'
        elif c['space']:
            t = match.group().replace('\t', '&nbsp;' * tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' ' * tabstop;
        else:
            url = match.group('protocol')
            if url.startswith(' '):
                prefix = ' '
                url = url[1 : ]
            else:
                prefix = ''
            last = match.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            if "://" not in url:
                url = "http://" + url
            return '%s<a href="%s" target="_blank">%s</a>%s' % (prefix, url, url, last)

    return URL_PATTERN.sub(substitute, text)
#- Fine Funzione -


def html_escape(text):
    """
    Funzioncina che serve a convertire i caratteri <, > e & nelle rispettive
    entità html.
    """
    if not text:
        log.bug("text non è un parametro valido: %r" % text)
        return ""

    # -------------------------------------------------------------------------

    # La & deve essere la prima ad essere sostituita
    if "&" in text:
        text = text.replace("&", "&amp;")
    if "<" in text:
        text = text.replace("<", "&lt;")
    if ">" in text:
        text = text.replace(">", "&gt;")

    if '"' in text:
        text = text.replace('"', "&quot;")
    if "'" in text:
        text = text.replace("'", "&apos;")

    #if "/" in text:
    #    text = text.replace("/", "&#47;")
    #if "+" in text:
    #    text = text.replace("+", "&#43;")
    #if ":" in text:
    #    text = text.replace(":", "&#58;")
    #if ";" in text:
    #    text = text.replace(";", "&#59;")

    return text
#- Fine Funzione -


class MLStripper(HTMLParser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def remove_tags(html):
    if "<" not in html:
        return html
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def email_encoder(email):
    if not email:
        log.bug("email non è un parametro valido: %r" % email)
        return

    # -------------------------------------------------------------------------

    email = email.lower()

    result = ""
    for c in email:
        if   c == "A":  result += "&#065;"
        elif c == "a":  result += "&#097;"
        elif c == "B":  result += "&#066;"
        elif c == "b":  result += "&#098;"
        elif c == "C":  result += "&#067;"
        elif c == "c":  result += "&#099;"
        elif c == "D":  result += "&#068;"
        elif c == "d":  result += "&#100;"
        elif c == "E":  result += "&#069;"
        elif c == "e":  result += "&#101;"
        elif c == "F":  result += "&#070;"
        elif c == "f":  result += "&#102;"
        elif c == "G":  result += "&#071;"
        elif c == "g":  result += "&#103;"
        elif c == "H":  result += "&#072;"
        elif c == "h":  result += "&#104;"
        elif c == "I":  result += "&#073;"
        elif c == "i":  result += "&#105;"
        elif c == "J":  result += "&#074;"
        elif c == "j":  result += "&#106;"
        elif c == "K":  result += "&#075;"
        elif c == "k":  result += "&#107;"
        elif c == "L":  result += "&#076;"
        elif c == "l":  result += "&#108;"
        elif c == "M":  result += "&#077;"
        elif c == "m":  result += "&#109;"
        elif c == "N":  result += "&#078;"
        elif c == "n":  result += "&#110;"
        elif c == "O":  result += "&#079;"
        elif c == "o":  result += "&#111;"
        elif c == "P":  result += "&#080;"
        elif c == "p":  result += "&#112;"
        elif c == "Q":  result += "&#081;"
        elif c == "q":  result += "&#113;"
        elif c == "R":  result += "&#082;"
        elif c == "r":  result += "&#114;"
        elif c == "S":  result += "&#083;"
        elif c == "s":  result += "&#115;"
        elif c == "T":  result += "&#084;"
        elif c == "t":  result += "&#116;"
        elif c == "U":  result += "&#085;"
        elif c == "u":  result += "&#117;"
        elif c == "V":  result += "&#086;"
        elif c == "v":  result += "&#118;"
        elif c == "W":  result += "&#087;"
        elif c == "w":  result += "&#119;"
        elif c == "X":  result += "&#088;"
        elif c == "x":  result += "&#120;"
        elif c == "Y":  result += "&#089;"
        elif c == "y":  result += "&#121;"
        elif c == "Z":  result += "&#090;"
        elif c == "z":  result += "&#122;"
        elif c == "0":  result += "&#048;"
        elif c == "1":  result += "&#049;"
        elif c == "2":  result += "&#050;"
        elif c == "3":  result += "&#051;"
        elif c == "4":  result += "&#052;"
        elif c == "5":  result += "&#053;"
        elif c == "6":  result += "&#054;"
        elif c == "7":  result += "&#055;"
        elif c == "8":  result += "&#056;"
        elif c == "9":  result += "&#057;"
        elif c == "&":  result += "&#038;"
        elif c == " ":  result += "&#032;"
        elif c == "_":  result += "&#095;"
        elif c == "-":  result += "&#045;"
        elif c == "@":  result += "&#064;"
        elif c == ".":  result += "&#046;"
        else:           result += c

    return result
#- Fine Funzione -


def square_bracket_to_html_entities(text):
    """
    Funzioncina che serve a convertire i caratteri [ e ] nelle rispettive
    entità html.
    """
    if not text:
        log.bug("text non è un parametro valido: %r" % text)
        return text

    # -------------------------------------------------------------------------

    if "[" in text:
        text = text.replace("[", "&#91;")
    if "]" in text:
        text = text.replace("]", "&#93;")

    return text
#- Fine Funzione -


def nifty_value_search(dictionary, argument):
    if not dictionary:
        log.bug("dictionary non è un parametro valido: %r" % dictionary)
        return

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    try:
        return dictionary[argument]
    except KeyError:
        # Se non ha trovato nulla allora prova a trovare in maniera
        # intelligente una chiave simile all'argomento passato
        pass

    argument = argument.lower()

    for key in dictionary:
        if is_same(argument, key):
            return dictionary[key]

    for key in dictionary:
        if is_prefix(argument, key):
            return dictionary[key]

    return None
#- Fine Funzione -


#-------------------------------------------------------------------------------

def put_final_dot(argument, char="."):
    """
    Aggiunge, se ce n'è bisogno, un punto a fine stringa.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    argument_without_css = argument
    if "[" in argument:
        global remove_colors
        if not remove_colors:
            from src.color import remove_colors
        argument_without_css = remove_colors(argument)
        if not argument_without_css:
            log.bug("argument_without_css non è valido: %r" % argument_without_css)
            return ""

    if argument_without_css[-1].isalnum():
        argument += char

    return argument
#- Fine Funzione -

# Definisce un'alias a put_final_dot:
put_final_mark = put_final_dot


def random_marks(question_qty, exclamation_qty):
    """
    Ritorna un numero casuale, anche vuoto, di punti di domanda e punti
    esclamativi voluti; serve a variare un po' l'espressività di alcune frasi
    nei gamescripts.
    """
    question_marks = ""
    if question_qty > 1:
        question_marks = random.randint(1, question_qty) * "?"
    elif question_qty == 1:
        question_marks = "?"

    exclamation_marks = ""
    if exclamation_qty > 1:
        exclamation_marks = random.randint(1, exclamation_qty) * "!"
    elif exclamation_qty == 1:
        exclamation_marks = "!"

    marks = list(question_marks) + list(exclamation_marks)
    random.shuffle(marks)
    return "".join(marks)
#- Fine Funzione -


# (TD) Magari in futuro aggiungere un parametro che indichi quale separatore
# utilizzare ricavando informazioni dal client tramite javascript, il tutto
# col pensiero di internazionalizzare Aarit
def commafy(number):
    """
    Passato un numero ne ritorna una stringa con gli apostrofi come separatori
    delle migliaia di cifre.
    """
    locale.setlocale(locale.LC_ALL, "")
    return locale.format("%d", number, True)
#- Fine Funzione -


def get_emote_argument(argument):
    """
    Ritorna argument utilizzabile come emote aggiungendo uno spazio precedente
    o meno a seconda.
    """
    if not argument:
        return ""

    if argument[0] in ("!", "?", ".") or argument[0].isspace():
        return argument

    return " " + argument
#- Fine Funzione -


def format_for_admin(message, open_symbol="{", close_symbol="}"):
    """
    Formatta i messaggi da inviare agli admin per avvisare un amministratore
    che quell'azione non la possono fare i giocatori normali.
    """
    if not message:
        log.bug("message non è un parametro valido: %r" % message)
        return ""

    # ---------------------------------------------------------------------

    return "<span class='admin'>%s%s%s</span>" % (open_symbol, message, close_symbol)
#- Fine Metodo -


def get_weight_descr(weight):
    """
    Ritorna una stringa descrivente il peso di un'entità; se questo pesa meno
    di un chilo visualizza il peso in grammi.
    """
    if weight < 0:
        log.bug("weight non è un parametro valido: %d" % weight)
        return ""

    # -------------------------------------------------------------------------

    if weight < 1000:
        return "circa [white]%d[close] gramm%s" % (weight, "o" if weight == 1 else "i")
    elif weight < 1000000:
        return "circa [white]%d[close] chil%s" % (weight / 1000, "o" if (weight / 1000) == 1 else "i")
    else:
        return "[red]veramente tanto[close]"

    log.bug("Inaspettato raggiungimento del codice")
    return ""
#- Fine Funzione -


def pretty_list(list_to_convert):
    """
    Ritorna una frase descrivendo un elenco, separato da virgole o dalla
    congiunzione 'e', partendo da una lista di stringhe.
    """
    if not list_to_convert:
        log.bug("list_to_convert non è un parametro valido: %r" % list_to_convert)
        return

    # -------------------------------------------------------------------------

    if len(list_to_convert) == 1:
        return str(list_to_convert[0])

    arguments = []
    for argument in list_to_convert:
        argument = str(argument).strip()
        if len(list_to_convert) >= 2 and argument == str(list_to_convert[-1]):
            arguments.append(" e " + argument)
        else:
            if argument == str(list_to_convert[0]):
                arguments.append(argument)
            else:
                arguments.append(", " + argument)

    return "".join(arguments)
#- Fine Funzione -


def add_to_phrase(phrase, argument, punct=""):
    if not phrase:
        log.bug("phrase non è un parametro valido: %r" % phrase)
        return

    if not argument:
        log.bug("argument non è un parametro valido: %r" % phrase)
        return

    # -------------------------------------------------------------------------

    if phrase[-1] in (".", "!", "?"):
        return phrase[ : -1] + argument + phrase[-1]
    else:
        return phrase + argument + punct
#- Fine Funzione -


def iter_filenames(path, extention="", subfolders=False):
    if not path:
        log.bug("path non è un parametro valido: %r" % path)
        return

    # -------------------------------------------------------------------------

    if extention:
        extention = extention.lower()
        if extention[0] != ".":
            extention = "." + extention

    for root, dirnames, filenames in os.walk(path):
        for filename in sorted(filenames):
            if filename[0] == "_":
                continue
            if not subfolders and root != path:
                continue
            if extention and os.path.splitext(filename)[1].lower() != extention:
                continue
            yield root, filename
#- Fine Funzione -


def iter_files(path, extention="", subfolders=False):
    if not path:
        log.bug("path non è un parametro valido: %r" % path)
        return

    # -------------------------------------------------------------------------

    extention = extention.lower()

    for root, dirnames, filenames in os.walk(path):
        for filename in sorted(filenames):
            if filename[0] == "_":
                continue
            if not subfolders and root != path:
                continue
            if extention and os.path.splitext(filename)[1].lower() != "." + extention:
                continue
            filepath = "%s/%s" % (root, filename)
            try:
                file = open(filepath, "r")
            except IOError:
                log.bug("Impossibile aprire il file %s in lettura" % filepath)
            yield file
#- Fine Funzione -


def iter_lines(file):
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    # -------------------------------------------------------------------------

    for line in file:
        line = line.strip()
        if not line:
            continue
        if line[0] == "#":
            continue
        yield line
#- Fine Funzione -


#-------------------------------------------------------------------------------

def sort_datas(datas, sorted_by="primary_key", reverse=False):
    """
    Ordina l'elenco di dati passato relativamente all'attributo ricavato
    da sorted_by.
    """
    if not sorted_by:
        log.bug("sorted_by non è un parametro valido: %r" % sorted_by)
        return []

    # -------------------------------------------------------------------------

    if not datas:
        return []

    if sorted_by == "primary_key":
        return sorted(datas.items(), reverse=reverse)
    else:
        return sorted(datas.items(), key=lambda obj:getattr(obj[1], sorted_by), reverse=reverse)
#- Fine Funzione -


def create_folders(folder):
    if not folder:
        log.bug("folder non è un parametro valido: %s" % folder)
        return False

    # -------------------------------------------------------------------------

    if os.path.exists(folder):
        return True

    try:
        os.makedirs(folder)
    except OSError:
        return False

    return True
#- Fine Metodo -


def create_file(filepath):
    if not filepath:
        log.bug("filepath non è un parametro valido: %s" % filepath)
        return False

    # -------------------------------------------------------------------------

    if os.path.exists(filepath):
        return True

    try:
        open(filepath, "w")
    except OSError:
        return False

    return True
#- Fine Metodo -


# (TD) per ora inutilizzata
#def find_function_in_stack(function_name, stack):
#    """
#    Controlla se il nome della funzione passata si trovi da qualche parte nello
#    stack passato (cerca al contrario).
#    """
#    if not function_name:
#        log.bug("function_name non è un parametro valido: %r" % function_name)
#        return False
#
#    if not stack:
#        log.bug("stack non è un parametro valido: %r" % stack)
#        return False
#
#    # -------------------------------------------------------------------------
#
#    for s in reversed(stack):
#        if s[2] == function_name:
#            return True
#
#    return False
##- Fine Funzione -
