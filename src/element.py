# -*- coding: utf-8 -*-

"""
Modulo per il supporto delle enumerazioni del gioco.
Essi si trovano tutti nella cartella src/enums.
"""


#= IMPORT ======================================================================

import os
import random
import sys

from src.accent  import accents_escape
from src.engine  import engine
from src.log     import log
from src.utility import copy_existing_attributes, is_same, to_capitalized_words


#= CLASSI ======================================================================

class EnumElement(object):
    """
    Gestisce gli elementi di un'enumerazione.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    SHOW_ATTRS_ON_HTML = []

    def __init__(self, name, description=""):
        if not name:
            log.bug("name non è un parametro valido: %r" % name)
            return

        # ---------------------------------------------------------------------

        # La variabile enum contiene l'enumerazione della classe che conterrà
        # questa'ultima.
        # Il motivo per cui viene salvato il riferimento all'enumerazione
        # su ogni Elemento di Enumerazione (come accade con le Flags è per
        # risparmiare memoria: gli Elementi sono relativamente pochi rispetto
        # a tutte le flags delle entità che possono diventare veramente molte!
        self.enum        = sys.modules[self.__module__]
        self.code        = ""  # Il codice viene inizializzato nella finalize_enumeration
        self.name        = name
        self.description = description
        self.index       = -1
        # Questo è un riferimento a se stessi che serve a far utilizzare nella
        # stessa maniera gli EnumElement e gli Elementfacendo risparmiare cicli
        # di clock preziosi evitando di utilizzare isinstance, type o hasattr.
        # Attenzione ai riferimenti circolari!
        self.enum_element = self

        # Per ogni EnumElement creato viene inserito nella lista elements del
        # modulo della enumerazione relativa, in tal modo si ha una lista
        # ordinata degli elementi in qualsiasi momento
        self.enum.elements.append(self)
    #- Fine Inizializzazione -

    def __str__(self):
        return self.name
    #- Fine Metodo -

    def __repr__(self):
        return self.code
    #- Fine Metodo -

    # -------------------------------------------------------------------------
    # Meglio non eseguire dei check sui parametri per mantenere le prestazioni

    def __lt__(self, other):
        return self.index < other.enum_element.index
    #- Fine Metodo -

    def __le__(self, other):
        return self.index <= other.enum_element.index
    #- Fine Metodo -

    def __eq__(self, other):
        return self.code == other.code
    #- Fine Metodo -

    def __ne__(self, other):
        return self.code != other.enum_element.code
    #- Fine Metodo -

    def __gt__(self, other):
        return self.index > other.enum_element.index
    #- Fine Metodo -

    def __ge__(self, other):
        return self.index >= other.enum_element.index
    #- Fine Metodo -

    def __add__(self, other):
        index = self.index + other
        # Evita di sforare la lista degli elementi
        if index > len(self.enum.elements):
            # (TD) potrebbe essere il caso di utilizzare una deque con il rotate
            # o altri costrutti del genere
            if self.enum.cycle_on_last:
                index = 1
            else:
                index = len(self.enum.elements)
        return self.enum.elements[index - 1]
    #- Fine Metodo -

    def __sub__(self, other):
        result = self.index - other
        # Evita di assegnare l'elemento di enumerazione NONE
        if result < 1:
            result = 1
        return self.enum.elements[result - 1]
    #- Fine Metodo -

    def __setattr__(self, name, value):
        if hasattr(self, "code") and hasattr(self, "index") and self.code and self.index >= 0:
            raise AttributeError, "Non puoi modificare un elemento di enumerazione una volta che è stato finalizzato"
        else:
            self.__dict__[name] = value
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_error_message(self, enum, attr):
        """
        Se, controllando l'elemento, trova un errore ne ritorna il messaggio
        adeguato.
        """
        if not enum:
            log.bug("enum non è un parametro valido: %r" % enum)
            return ""

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return ""

        # ---------------------------------------------------------------------

        if self.enum.name != enum.name:
            return "Enumerazione errata: %s (dovrebbe essere %s) per l'attributo %s" % (self.enum.name, enum.name, attr)

        if not self.code:
            return "L'enum-element non ha un codice valido per l'attributo %s" % (attr)

        if not self.name:
            return "Il nome dell'enum-element %s dell'enumerazione %s non è valido per l'attributo %s" % (self.code, self.enum.name, attr)

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        """
        La copia di un enum_element dev'essere per forza un riferimento a
        se stesso.
        """
        return self
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        """
        Scrive su file un elemento di enumerazione.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        if not self.code:
            log.bug("Il codice dell'EnumElement da scrivere sul file %s non è valido: %r" % (file.name, self.code))
            return

        file.write("%s%s%s\n" % (indentation, label, self.code))
    #- Fine Metodo -

    def get_mini_code(self):
        return self.code.split(".")[1].lower()
    #- Fine Metodo -


# Non si può utilizzare la UserDict perché non è iterabile
class EnumElementDict(dict):
    """
    Questo dizionario DEVE essere usato quando si prevede di utilizzare
    come chiavi degli EnumElement, cosicché gli Elementi-sinonimi possono
    confrontare in maniera adeguata i propri valori.
    """
    REFERENCES = {}
    WEAKREFS = {}
    
    def __init__(self, dictionary=None, **kwargs):
        self.data = {}
        if dictionary is not None:
            self.data.update(dictionary)
        if len(kwargs) > 0:
            self.data.update(kwargs)
    #- Fine Inizializzazione -

    # -------------------------------------------------------------------------

    def __len__(self):
        return len(self.data)
    #- Fine Metodo -

    def __getitem__(self, element):
        if element.enum_element in self.data:
            return self.data[element.enum_element]

        raise KeyError(element)
    #- Fine Metodo -

    def __setitem__(self, element, value):
        self.data[element.enum_element] = value
    #- Fine Metodo -

    def __delitem__(self, element):
        if element.enum_element in self.data:
            del self.data[element.enum_element]
            return

        raise KeyError(element)
    #- Fine Metodo -

    def __contains__(self, element):
        return element.enum_element in self.data
    #- Fine Metodo -

    def __iter__(self):
        return self.data.iterkeys()
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def __repr__(self):
        return repr(self.data)

    def __cmp__(self, dictionary):
        if isinstance(dictionary, (EnumElementDict, Flags)):
            return cmp(self.data, dictionary.data)
        else:
            return cmp(self.data, dictionary)

    def clear(self):
        self.data.clear()

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = EnumElementDict()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def values(self):
        return self.data.values()

    def has_key(self, key):
        return key in self.data

    def update(self, dictionary=None, **kwargs):
        if dictionary is None:
            pass
        elif isinstance(dictionary, (EnumElementDict, Flags)):
            self.data.update(dictionary.data)
        elif isinstance(dictionary, type({})) or not hasattr(dictionary, 'items'):
            self.data.update(dictionary)
        else:
            for k, v in dictionary.items():
                self[k] = v
        if len(kwargs):
            self.data.update(kwargs)

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        return self.data.pop(key, *args)

    def popitem(self):
        return self.data.popitem()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d


class Element(object):
    """
    Questa classe permette di gestire una variabile pressoché uguale
    alll'EnumElement ma con in più l'attributo synonym che contiene un nome
    alternativo all'elemento, un sinonimo appunto.
    Così al posto di semplici nomi tipo "Umano", si possono personalizzare
    tramite i synonym con "Umano di Nakilen", "Umano Alto", etc etc.. creando
    così sottorazze almeno di nome, poiché in realtà questi Element  si
    riferirebbero tutti allo stesso elemento d'enumerazione.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, enum_element, synonym=""):
        if not enum_element:
            log.bug("enum_element non è un parametro valido: %r" % enum_element)
            return

        # ---------------------------------------------------------------------

        if isinstance(enum_element, basestring):
            enum_element = get_enum_element(enum_element)

        self.enum_element = enum_element or None

        # Qui ritengo che sia meglio non utilizzare la funzione is_same
        # per il confronto, al caso che qualcuno voglia inserire dei
        # sinonimi uguale al nome dell'elemento ma con o senza colori
        # oppure con lettere maiuscole/minuscole differenti
        if synonym and synonym != self.enum_element.name:
            self.synonym = synonym
        else:
            self.synonym = ""
    #- Fine Inizializzazione -

    def __str__(self):
        if self.synonym:
            return self.synonym
        elif self.enum_element:
            return self.enum_element.name

        log.bug("enum_element errato per %r con synonym %r" % (self, self.synonym))
        return "<error>"
    #- Fine Metodo -

    def __repr__(self):
        if self.enum_element:
            if self.synonym:
                return "%s %s" % (repr(self.enum_element), self.synonym)
            else:
                return "%s" % repr(self.enum_element)
        else:
            log.bug("enum_element errato per %r con synonym %r" % (self, self.synonym))
            return "<errore!> %s" % self.synonym
    #- Fine Metodo -

    # -------------------------------------------------------------------------
    # Meglio non eseguire dei check sui parametri per mantenere le prestazioni

    def __lt__(self, other):
        return self.enum_element.index < other.enum_element.index
    #- Fine Metodo -

    def __le__(self, other):
        return self.enum_element.index <= other.enum_element.index
    #- Fine Metodo -

    def __eq__(self, other):
        return self.enum_element.code == other.enum_element.code
    #- Fine Metodo -

    def __ne__(self, other):
        return self.enum_element.code != other.enum_element.code
    #- Fine Metodo -

    def __gt__(self, other):
        return self.enum_element.index > other.enum_element.index
    #- Fine Metodo -

    def __ge__(self, other):
        return self.enum_element.index >= other.enum_element.index
    #- Fine Metodo -

    def __add__(self, other):
        index = self.enum_element.index + other
        # Evita di sforare la lista degli elementi
        if index > len(self.enum_element.enum.elements):
            if self.enum_element.enum.cycle_on_last:
                index = 1
            else:
                index = len(self.enum_element.enum.elements)
        return self.enum_element.enum.elements[index - 1]
    #- Fine Metodo -

    def __sub__(self, other):
        index = self.enum_element.index - other
        # Evita di assegnare l'elemento di enumerazione NONE
        if index < 1:
            index = 1
        return self.enum_element.enum.elements[index - 1]
    #- Fine Metodo -

    # (TT) probabilmente questa __getattr__ consuma preziose risorse cpu
    # bisognerebbe tracciare se c'è un name particolare che ricava, così da
    # referenziarlo
    def __getattr__(self, name):
        """
        Grazie a questo metodo speciale la classe Element è come se fosse
        una classe EnumElement accedendo direttamente ai suoi attributi invece
        di salvarne il riferimento in questa classe e consumando memoria per
        nulla.
        """
        return getattr(self.enum_element, name)
    #- Fine Metodo -

    # (TD) in futuro attr non dovrà essere opzionale
    def get_error_message(self, enum, attr, allow_none=True):
        """
        Il controllo degli errori è praticamente uguale a quello per le
        EnumElement visto che l'attributo synonym non ha bisogno di controlli
        particolari.
        """
        if not enum:
            log.bug("enum non è parametro valido: %r" % enum)
            return None

        if not attr:
            log.bug("attr non è un parametro valido :%r" % attr)
            return None

        # ---------------------------------------------------------------------

        if not hasattr(self, "enum_element"):
            return "%s non possiede neppure l'attributo enum_element" % attr
        if not self.enum_element:
            return "%s non ha ricavato l'element d'enumerazione" % attr
        if not allow_none and self.enum_element.code[-5 : ] == ".NONE":
            return "%s ha l'elemento di enumerazione NONE" % attr
        return self.enum_element.get_error_message(enum, attr)
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Element(self.enum_element)
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def randomize(self, from_element=None, to_element=None):
        """
        Ritorna un elemento a caso dell'enumerazione passata.
        from_element e to_element sono facoltativi e servono a scegliere
        un range ristretto dell'enumerazione.
        """
        if not from_element:
            from_element = self.enum_element.enum.elements[0]
        if not to_element:
            to_element = self.enum_element.enum.elements[-1]
        choised = random.randint(from_element.index, to_element.index)
        self.enum_element = from_element.enum_element.enum.elements[choised - 1]
        self.synonym = ""

        return self
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        """
        Ricava dalla linea passata i valori di un Element.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # ---------------------------------------------------------------------

        try:
            code, synonym_string = line.split(None, 1)
        except ValueError:
            code = line.strip()
            synonym_string = ""
        else:
            # Capita che alcuni builder scambino alcuni Element per delle Flags ed
            # inseriscano più element in una riga sola, che il sistema invece
            # leggerebbe come se fossero dei sinonimi, quindi c'è qui un controllo
            # apposito
            enum_prefix = code.split(".", 1)
            if "." in synonym_string:
                synonym_prefix = synonym_string.split(".", 1)
                if enum_prefix == synonym_prefix:
                    log.bug("linea di Element errata, attenzione a non confondersi con le Flags: %s file <%s> attr <%s>" % (
                        line, file.name, attr))
                    synonym_string = ""

        # A volte qualcuno inserisce una virgola invece di lasciare lo spazio
        # tra il codice e il sinonimo, qui gestisce questo stile
        if code[-1] == ",":
            code = code[ : -1].strip()

        error = False
        try:
            self.__init__(code, synonym_string)
        except:
            error = True

        if not self.enum_element:
            log.bug("codice passato errato <%s> nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                code, file.name, line, attr))
            return

        if error or self.get_error_message(self.enum, attr) != "":
            log.bug("codice passato errato <%s> nel file <%s> per la linea <%s> e l'attributo <%s>. Errore: %s" % (
                code, file.name, line, attr, self.get_error_message(self.enum, attr)))
            return
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        """
        Scrive su file un elemento sinonimo.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        if not hasattr(self, "code"):
            log.bug("Il codice dell'Element da scrivere sul file %s non ha neppure l'attributo code (forse un errore durante il caricamento?)" % file.name)
            return

        if not self.code:
            log.bug("Il codice dell'Element da scrivere sul file %s non è valido: %r" % (file.name, self.code))
            return

        indentation = indentation or ""

        if self.synonym:
            file.write("%s%s%s %s\n" % (indentation, label, self.code, self.synonym))
        else:
            file.write("%s%s%s\n" % (indentation, label, self.code))
    #- Fine Metodo -

    def get_mini_code(self):
        return self.code.split(".")[1].lower()
    #- Fine Metodo -


# Non si può utilizzare la UserDict perché non è iterabile
class Flags(dict):
    """
    Questa classe contiene sostanzialmente un dizionario di elementi di una
    stessa tipologia di enumerazione.
    Concettualmente bisogna vedere questa classe come un bitvector dei Mud
    classici.
    Poiché deve esistere sempre almeno un elemento nel dizionario (che serve a
    ricavare di quale enumerazione la Flags appartenga) spesso viene passato
    l'elemento NONE di un'enumerazione per inizializzarne una nuova istanza.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, *enum_elements):
        """
        (bb) Assicurarsi di inizializzarsi le Flags sempre e solo con l'elemento
        NONE, altrimenti il fread imposterà sì le flag ma non rimuoverà
        quelle già precedentemente impostate.
        """
        if not enum_elements:
            log.bug("enum_elements non è un parametro valido: %r" % enum_elements)
            return

        # ---------------------------------------------------------------------

        # Se la variabile flags passata in realtà è già un oggetto Flags allora
        # prepara la lista di elementi per ricreare l'oggetto Flags
        if type(enum_elements[0]) == Flags:
            enum_elements = enum_elements[0].values()
        # Se invece la variabile enum_elements è una stringa bisogna prepare la
        # lista di elementi splittandola
        elif isinstance(enum_elements[0], basestring):
            code_strings = enum_elements[0].split()
            enum_elements = []
            for code_string in code_strings:
                # Separare le singole flag da una virgola è facoltativo
                if code_string[-1] == ",":
                    code_string = code_string[ : -1].rstrip()
                enum_element_found = get_enum_element(code_string)
                if enum_element_found:
                    enum_elements.append(enum_element_found)
        elif isinstance(enum_elements[0], dict):
            enum_elements = enum_elements[0]

        self.enum = None
        self.data = {}
        for enum_element in enum_elements:
            if enum_element.enum:
                self.enum = enum_element.enum
            if enum_element != enum_element.enum.NONE:
                self.data[enum_element] = enum_element
    #- Fine Inizializzazione -

    # -------------------------------------------------------------------------

    def __len__(self):
        return len(self.data)
    #- Fine Metodo -

    def __getitem__(self, element):
        if element.enum_element in self.data:
            return self.data[element.enum_element]

        raise KeyError(element)
    #- Fine Metodo -

    def __setitem__(self, element, value):
        self.data[element.enum_element] = value
        return
    #- Fine Metodo -

    def __delitem__(self, element):
        if element.enum_element in self.data:
            del self.data[element.enum_element]
            return

        raise KeyError(element)
    #- Fine Metodo -

    def __contains__(self, element):
        if element.enum != self.enum:
            log.bug("enumerazione tra element %r e flags differente:  %r (enum %s)" % (
                element, self.data, self.enum.name if self.enum else None))
        return element.enum_element in self.data
    #- Fine Metodo -

    def __iter__(self):
        return self.data.iterkeys()
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def __str__(self):
        result = ""

        sorted_elements = self.sort_elements()
        if len(self) > 1:
            for enum_element in sorted_elements[0 : -1]:
                result += " %s," % enum_element
            result = "%s e %s" % (result.rstrip(","), sorted_elements[-1])
        elif len(self) == 1:
            result = str(sorted_elements[0])

        return result.lstrip()
    #- Fine Metodo -

    def __repr__(self):
        result = ""
        for enum_element in self.sort_elements(True):
            result += "%r, " % enum_element
        return result.rstrip(", ")
    #- Fine Metodo -

    # -------------------------------------------------------------------------
    # Meglio non eseguire dei check sui parametri per mantenere le prestazioni

    def __eq__(self, other):
        """
        Sia self che other devono essere due classi Flags
        """
        if not other:
            return False
        if type(other) != Flags:
            log.bug("other è di una tipologia errato: %s" % type(other))
            return False
        return self.sort_elements() == other.sort_elements()
    #- Fine Metodo -

    def __ne__(self, other):
        if type(other) != Flags:
            log.bug("other è di una tipologia errato: %s" % type(other))
            return False
        return self.sort_elements() != other.sort_elements()
    #- Fine Metodo -

    def __add__(self, other):
        """
        Aggiunge un elemento alla flag passandogli il relativo riferimento
        all'elemento d'enumerazione.
        """
        if isinstance(other, basestring):
            other = get_enum_element(other)
        else:
            other = other.enum_element

        if other.enum != self.enum:
            log.bug("enumerazione tra element %r e flags differente: %s %r" % (self, self.enum.name, self.data))

        if other and other not in self.data:
            self.data[other] = other
        return self
    #- Fine Metodo -

    def __sub__(self, other):
        """
        Rimuove il riferimento dell'elemento dalla flag relativo al codice
        passato.
        """
        if isinstance(other, basestring):
            other = get_enum_element(other)
        else:
            other = other

        if other and other in self.data:
            del self.data[other.enum_element]
        return self
    #- Fine Metodo -

    def __cmp__(self, dictionary):
        if isinstance(dictionary, (EnumElementDict, Flags)):
            return cmp(self.data, dictionary.data)
        else:
            return cmp(self.data, dictionary)

    def clear(self):
        self.data.clear()

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Flags(self.data)
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()

    def values(self):
        return self.data.values()

    def has_key(self, key):
        return key in self.data

    def update(self, dictionary=None, **kwargs):
        if dictionary is None:
            pass
        elif isinstance(dictionary, (EnumElementDict, Flags)):
            self.data.update(dictionary.data)
        elif isinstance(dictionary, type({})) or not hasattr(dictionary, 'items'):
            self.data.update(dictionary)
        else:
            for k, v in dictionary.items():
                self[k] = v
        if len(kwargs):
            self.data.update(kwargs)

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        return self.data.pop(key, *args)

    def popitem(self):
        return self.data.popitem()

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def sort_elements(self, use_none_element=False):
        """
        Ritorna gli elementi di una Flags ordinati a seconda della posizione.
        La lista di elementi è senza il primo valore NONE.
        Se viene passato il parametro use_none_element a True e la lista
        risultante è vuota allora viene aggiunto forzatamente l'elemento NONE.
        """
        sorted_elements = []

        for element in self.enum.elements:
            if element in self.data:
                sorted_elements.append(element)

        if use_none_element and not sorted_elements:
            sorted_elements.append(self.enum.NONE)

        return sorted_elements
    #- Fine Metodo -

    # (TT) serve raramente, forse posso farne a meno
    def toggle(self, enum_element):
        """
        Rimuove o aggiunge un elemento dalle flag a seconda se sia
        presente o assente.
        """
        if not enum_element:
            log.bug("enum_element non è un parametro valido: %r" % enum_element)
            return

        # ---------------------------------------------------------------------

        try:
            enum_element = enum_element.enum_element
        except AttributeError:
            enum_element = get_enum_element(enum_element)

        if enum_element:
            if enum_element in self.data:
                self.__sub__(enum_element)
            else:
                self.__add__(enum_element)
    #- Fine Metodo -

    def get_error_message(self, enum, attr):
        """
        Se vi sono degli errori nei dati della classe ne ritorna i
        relativi messaggi.
        """
        if not enum:
            log.bug("enum non è un parametro valido: %r" % enum)
            return ""

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return ""

        # ---------------------------------------------------------------------

        if not self.enum:
            return "enum non valido per la flag con attributo %s" % attr

        for element in self.data.itervalues():
            msg = element.get_error_message(enum, attr)
            if msg != "":
                return msg

        return ""
    #- Fine Metodo -

    def randomize(self, from_element=None, to_element=None):
        """
        Ritorna casualmente una serie di flag-elemento.
        from_element e to_element funzionano come nel metodo randomize della
        classe Element.
        """
        if not from_element:
            from_element = self.enum.elements[0]
        if not to_element:
            to_element = self.enum.elements[-1]

        # Sceglie gli elementi per la flag
        elements_population = self.enum.elements[from_element.index : to_element.index]
        quantity_choised = random.randint(0, to_element.index - from_element.index)
        choised_elements = random.sample(elements_population, quantity_choised)

        # Reinizializza il dizionario con i nuovi valori scelti a caso
        self.data.clear()
        for choised_element in choised_elements:
            self.data[choised_element] = choised_element

        return self
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        """
        Inizializza dalla linea passata un'instanza Flags.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # -------------------------------------------------------------------------

        self.__init__(line)

        error_message = self.get_error_message(self.enum, attr)
        if error_message != "":
            log.bug("le flag passate sono errate <%s> al file <%s> e con l'attributo <%s>" % (
                line, file.name, attr))
            return
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        """
        Scrive su file tutti i codice degli elementi he compongono la
        flag passata.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        indentation = indentation or ""

        file.write(indentation + label)
        if self.data:
            file.write(repr(self))
        else:
            if not repr(self.enum.NONE):
                log.bug("Flags %s non finalizzata." % self.enum.name)
            file.write(repr(self.enum.NONE))
        file.write("\n")
    #- Fine Metodo -


#= FUNZIONI=====================================================================

def get_enum_element(element_code, quiet=False):
    """
    Recupera l'EnumElement relativo al codice dell'elemento passato.
    """
    if not element_code:
        log.bug("element_code non è un parametro valido: %r" % element_code)
        return None

    # -------------------------------------------------------------------------

    if "." in element_code:
        enum_name, code = element_code.split(".")
    else:
        if not quiet:
            log.bug("element_code passato è errato: %s" % element_code)
        return None

    module = __import__("src.enums.%s" % enum_name, globals(), locals(), [''])
    if hasattr(module, code):
        enum_element = getattr(module, code)
    else:
        if not quiet:
            log.bug("%s inesistente per l'enumerazione %s. *ERRORE CRITICO*" % (code, enum_name))
            engine.critical_errors += 1
        return None

    return enum_element
#- Fine Funzione -


# (TD) Convertirlo in metodo fread_the_line per l'EnumElement
def fread_enum_element(file, line, attr):
    """
    Legge da file testuale il codice relativo ad un elemento di enumerazione
    e lo ritorna.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return None

    if not line:
        log.bug("line non è un parametro valido: %r" % line)
        return None

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return None

    # -------------------------------------------------------------------------

    enum_element = get_enum_element(line)
    if not enum_element:
        log.bug("L'elemento di enumerazione letto dal file <%s> alla riga <%s> per l'attributo <%s> è errato" % (
            file.name, line, attr))
        return None

    return enum_element
#- Fine Funzione -


def finalize_enumeration(enum_import_path):
    """
    Per ogni Elemento di enumerazione assegna il codice relativo e l'indice
    posizionale.
    Rimuove inoltre dalla lista degli elementi del modulo il primo elemento
    (che è sempre NONE).
    """
    if not enum_import_path:
        log.bug("enum_import_path non è un parametro valido: %r" % enum_import_path)
        return

    # -------------------------------------------------------------------------

    enum = sys.modules[enum_import_path]
    for element_code in dir(enum):
        enum_element = enum.__dict__[element_code]
        if isinstance(enum_element, EnumElement):
            enum_element.code = "%s.%s" % (enum.name, element_code)
            enum_element.index = enum.elements.index(enum_element)
    enum.elements = enum.elements[1 : ]
#- Fine Funzione -


def get_element_from_index(enum, index):
    """
    Ricava l'elemento di un'enumerazione con index uguale a quello passato.
    """
    if not enum:
        log.bug("enum non è un parametro valido: %r" % enum)
        return None

    if index < 0 or index > len(enum.elements):
        log.bug("index non è un parametro valido: %d (0 - %d)" % (index, len(enum.elements)))
        return None

    # -------------------------------------------------------------------------

    for enum_element in enum.elements:
        if enum_element.index == index:
            return enum_element

    return None
#- Fine Funzione -


def get_element_from_name(enum, name):
    """
    Ricava l'elemento di un'enumerazione con index uguale a quello passato.
    """
    if not enum:
        log.bug("enum non è un parametro valido: %r" % enum)
        return None

    if not name:
        log.bug("name non è un parametro valido: %r" % name)
        return None

    # -------------------------------------------------------------------------

    from color import remove_colors

    for enum_element in enum.elements:
        enum_element_name = remove_colors(enum_element.name)
        if "$o" in enum_element_name:
            if is_same(enum_element_name.replace("$o", "o"), name):
                return enum_element
            if is_same(enum_element_name.replace("$o", "a"), name):
                return enum_element
        else:
            if is_same(enum_element_name, name):
                return enum_element

    return None
#- Fine Funzione -


def create_elements_list_page():
    from src.color import convert_colors

    lines = []

    lines.append('''<html>''')
    lines.append('''<head>''')
    lines.append('''<link rel="Shortcut Icon" type="image/x-icon" href="favicon.ico">''')
    lines.append('''<link rel="Stylesheet" type="text/css" href="../style.css">''')
    lines.append('''<link rel="Stylesheet" type="text/css" href="../style_doc.css">''')
    lines.append('''<title>Documentazione di Aarit, il Mud in Python</title>''')
    lines.append('''<meta http-equiv="content-type" content="text/html;" charset="utf-8" />''')
    lines.append('''</head>''')
    lines.append('''<body>''')
    lines.append('''<hr>''')

    for enum_name in sorted(os.listdir("src/enums/")):
        if enum_name[0] == "_":
            continue
        if not enum_name.endswith(".py"):
            continue
        if not enum_name[ : -len(".py")].isupper():
            continue

        enum_name = enum_name[ : -len(".py")]
        enum_module =__import__("src.enums." + enum_name, globals(), locals(), [""])

        other_attrs = ""
        for attr_name in enum_module.elements[0].__dict__:
            if attr_name in enum_module.elements[0].SHOW_ATTRS_ON_HTML:
                other_attrs += "<th>%s</th>" % to_capitalized_words(attr_name)

        lines.append('''<a name='%s'><h3 style='color:white'>%s</h3></a>''' % (
            enum_module.name, enum_module.name.capitalize()))
        lines.append('''%s''' % enum_module.__doc__)
        lines.append('''<table class="mud" border='1' width="100%">''')
        lines.append('''<tr><th>Codice</th><th>Nome</th><th>Descrizione</th>%s</tr>''' % other_attrs)
        for enum_element in enum_module.elements:
            name = convert_colors(enum_element.name)
            description = ""
            if enum_element.description:
                description = convert_colors(enum_element.description)

            other_attrs = ""
            for attr_name in enum_element.__dict__:
                if attr_name in enum_element.SHOW_ATTRS_ON_HTML:
                    other_attrs += "<td>%s</td>" % str(getattr(enum_element, attr_name))

            line = '''<tr><td>%s</td><td>%s</td><td>%s</td>%s</tr>''' % (
                enum_element.code, name, description, other_attrs)
            line = accents_escape(line)
            try:
                line = line.encode("ascii")
            except UnicodeDecodeError:
                print "Impossibile encodare in ascii la linea: %s" % line
            lines.append(line)
        lines.append('''</table><br><br>''')

    lines.append('''<hr>''')
    lines.append('''<body>''')
    lines.append('''</html>''')

    html_file = open("www/builder_pages/elements_list.htm", "w")
    html_file.write("\n".join(lines))
    html_file.close()
#- Fine Funzione -
create_elements_list_page()