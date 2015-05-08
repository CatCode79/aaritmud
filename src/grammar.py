# -*- coding: utf-8 -*-

"""
Modulo per la gestisce delle manipolazioni grammaticali sul testo.
"""


#= IMPORT ======================================================================

from src.color       import remove_colors
from src.database    import fread_list
from src.element     import Flags
from src.enums       import GRAMMAR, SEX, LOG
from src.log         import log
from src.utility     import clean_string, is_same, is_suffix, one_argument


#= VARIABILI ===================================================================

# Vocabolario delle parole italiane o termini fantastici inventati che
# contengono delle eccezioni e che non vengono gestite correttamente dalle
# funzione sottostanti
vocabulary = []


#= CLASSI ======================================================================

class EntryWord(object):
    """
    Gestisce un termine del vocabolario.
    """
    PRIMARY_KEY = ""  # Non ha una chiave primaria perché il dato è inserito in una lista
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        super(EntryWord, self).__init__()
        self.comment            = ""
        self.masculine_singular = ""
        self.masculine_plural   = ""
        self.feminine_singular  = ""
        self.feminine_plural    = ""
    #- Fine Inizializzazione -

    def fread_the_line(self, file, line, attr):
        """
        Ricava dalla linea passata un termine di vocabolario.
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

        ms, mp, fs, fp = line.split(",")

        self.masculine_singular = ms.strip()
        self.masculine_plural   = mp.strip()
        self.feminine_singular  = fs.strip()
        self.feminine_plural    = fp.strip()

        if self.get_error_message() != "":
            log.bug("EntryWord letta dal file <%s> alla riga <%s> per l'attributo <%s> è errata" % (file.name, line, attr))
            return
    #- Fine Metodo -

    # (??) cosa serve il parametro entry_word?
    def fwrite(self, file, entry_word):
        """
        Scrive su file una parola relativa al dizionario grammaticale del Mud.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        # -------------------------------------------------------------------------

        file.write("%s, %s, %s, %s\n" % (
            self.masculine_singular,
            self.masculine_plural,
            self.feminine_singular,
            self.feminine_plural))
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def grammar_cleaner(argument):
    """
    Passato un argomento ne ritorna la prima parola in minuscolo e senza
    caratteri di colore che potrebbero interferire con le funzioni grammaticali
    qui sotto.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    first_word = argument.split()[0]
    return remove_colors(first_word).lower()
#- Fine Funzione -


#-------------------------------------------------------------------------------

def semi_consonante(argument, c):
    """
    Ritorna vero che l'argomento passato inizia con una semiconsonante uguale
    al carattere passato.
    Una semiconsonante è una vocale seguita da un'altra vocale.
    """
    if not argument:
        log.bug("argument non un parametro valido: %r" % argument)
        return ""

    if not c:
        log.bug("c passato non è un parametro valido: %r")
        return ""

    if len(c) != 1:
        log.bug("c passato non è un parametro carattere: %r" % c)
        return ""

    # -------------------------------------------------------------------------

    c = c.lower()
    word = grammar_cleaner(argument)
    if word[0] == c and is_vowel(word[1]) and word[1] != c:
        return True
    else:
        return False
#- Fine Funzione -


def esse_impura(argument):
    """
    Ritorna vero se l'argomento passato inizia con 's' impura (cioè una
    's' seguita da una consonante).
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    word = grammar_cleaner(argument)
    if word[0] == "s" and not is_vowel(word[1]):
        return True
    else:
        return False
#- Fine Funzione -


def gruppo_diagramma(argument, diagramma):
    """
    Ritorna vero se l'argomento passato inizia con il gruppo o
    diagramma passato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    if not diagramma:
        log.bug("diagramma non è un parametro valido: %r" % diagramma)
        return ""

    if len(diagramma) != 2:
        log.bug("diagramma non è una stringa formata da due caratteri: %r" % diagramma)
        return ""

    # -------------------------------------------------------------------------

    word = grammar_cleaner(argument)
    if word[2 : ] == diagramma.lower():
        return True
    else:
        return False
#- Fine Funzione -


#-------------------------------------------------------------------------------

def is_vowel(c):
    """
    Ritorna vero se il carattere passato è una vocale.
    """
    if not c:
        log.bug("c non è un parametro valido: %r" % c)
        return False

    if len(c) != 1:
        log.bug("c passato non è un carattere: %r" % c)
        return False

    # -------------------------------------------------------------------------

    if c in ("a", "e", "i", "o", "u", "A", "E", "I", "O", "U"):
        return True
    else:
        return False
#- Fine Funzione -


# (TD) da ridefinire meglio
def is_masculine(argument):
    """
    Ritorna vero se l'argomento passato è una parola maschile.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    # Bisogna avere per forza un dizionario che indichi le eccezioni non
    # ricavabili dalla funzione
    for entry_word in vocabulary:
        if is_same(argument, (entry_word.masculine_singular, entry_word.masculine_plural)):
            return True
        elif is_same(argument, (entry_word.feminine_singular, entry_word.feminine_plural)):
            return False

    word = grammar_cleaner(argument)

    # Di solito le parole con la 'a' finale non sono maschili
    if word[-1] == "a":
        # Le parole che finiscono in "essa" non sono maschili
        if is_suffix("essa", word):
            return False
        # Le tipologie di derivazione greca che finiscono in "ma" sono maschili
        if is_same(word, ("diploma", "dramma", "poema", "teorema", "problema")):
            return True
        # Altre parole maschili
        if is_same(word, ("duca", "nulla", "papa", "pigiama", "poeta", "profeta", "vaglia")):
            return True
        return False
    elif word[-1] == "e":
        # Se la parole finisce in "tore" è maschile
        if is_suffix("tore", word):
            return True
        # Se finisce in "sore" la maggior parte delle volte è maschile
        if is_suffix("sore", word):
            return True
        # Quelle che finiscono in trice sono femminili
        if is_suffix("trice", word):
            return False
        return True
    elif word[-1] == "i":
        return True
    elif word[-1] == "o":
        return True
    elif word[-1] == "u":
        return True

    return False
#- Fine Funzione -


def is_feminine(argument):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    return not is_masculine(argument)
#- Fine Funzione -


def is_singular(argument):
    """
    Ritorna vero se l'argomento passato è una parola in singolare.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    for entry_word in vocabulary:
        if is_same(argument, (entry_word.masculine_singular, entry_word.feminine_singular)):
            return True
        elif is_same(argument, (entry_word.masculine_plural, entry_word.feminine_plural)):
            return False

    # (TD) da finire, anche questa funzione come is_masculine non è pienamente
    # programmabile
    return True
#- Fine Funzione -


def is_plural(argument):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    return not is_singular(argument)
#- Fine Funzione -


def get_grammar_genre(argument):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return GRAMMAR.NONE

    # -------------------------------------------------------------------------

    if is_masculine(argument):
        return GRAMMAR.MASCULINE
    else:
        return GRAMMAR.FEMININE
#- Fine Funzione -


def get_grammar_number(argument):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return GRAMMAR.NONE

    # -------------------------------------------------------------------------

    if is_singular(argument):
        return GRAMMAR.SINGULAR
    else:
        return GRAMMAR.PLURAL
#- Fine Funzione -


#-------------------------------------------------------------------------------

def grammar_gender(entity, masculine="o", feminine="a"):
    """
    Questa semplicistica funzione ritorna la corretta alternativa tra
    le stringa maschile o femminile passate a seconda del sesso dell'entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not masculine:
        log.bug("masculine non è un parametro valido: %r" % masculine)
        return ""

    if not feminine:
        log.bug("feminine non è un parametro valido: %r" % feminine)
        return ""

    # -------------------------------------------------------------------------

    if entity.sex == SEX.FEMALE:
        return feminine
    else:
        return masculine
#- Fine Funzione -


# (TD) farla e aggiungerci il supporto al vocabolario
def grammar_declension(argument, *types):
    """
    Ritorna l'argomento passato nel genere e numero grammaticale voluto.
    types è una lista di elementi dell'enumerazione GRAMMAR.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    if not types:
        log.bug("types non è un parametro valido: %r" % types)
        return ""

    # -------------------------------------------------------------------------

#    word = grammar_cleaner(argument)
    return argument
#- Fine Funzione -


def get_article(argument, *articles):
    """
    Ritorna l'articolo voluto adeguato all'argomento.
    articles è una lista di elementi dell'enumerazione GRAMMAR
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    word = grammar_cleaner(argument)

    # Se articles non è valido oppure non ha impostato nessuna sessualità
    # allora la trova automaticamente
    if not articles:
        articles = Flags(GRAMMAR.NONE)
        articles += get_grammar_genre(argument)
        articles += get_grammar_number(argument)
    else:
        articles = Flags(*articles)

    # (TD) Aggiungerci il supporto al vocabolario

    # (TD) forse posso fare a meno di convertirle in flags

    if GRAMMAR.FEMININE in articles:
        if GRAMMAR.PLURAL in articles:
            possessive = "tue "
            if GRAMMAR.INDETERMINATE in articles:
                article = "delle "
            elif GRAMMAR.PREPOSITION_IN in articles:
              article = "nelle "  
            else:
                article = "le "  # raramente anche "l'" davanti a vocale ma solo in testi poetici.
        else:
            possessive = "tua "
            if (GRAMMAR.POSSESSIVE not in articles and is_vowel(word[0])
            and not semi_consonante(word, "i")):
                if GRAMMAR.INDETERMINATE in articles:
                    article = "un'"
                elif GRAMMAR.PREPOSITION_IN in articles:
                  article = "nell'"  
                else:
                    article = "l'"
            else:
                if GRAMMAR.INDETERMINATE in articles:
                    article = "una "
                elif GRAMMAR.PREPOSITION_IN in articles:
                  article = "nella "  
                else:
                    article = "la "  # davanti alla 'h', al contrario del maschile, non c'è la forma con l'apostrofo
    else:
        if (GRAMMAR.POSSESSIVE not in articles
        and (esse_impura(word)
        or   word[0] == "z"
        or   word[0] == "x"
        or   gruppo_diagramma(word, "pn")
        or   gruppo_diagramma(word, "ps")
        or   gruppo_diagramma(word, "gn")
        or   gruppo_diagramma(word, "sc")
        or   semi_consonante(word, "i"))):
            if GRAMMAR.PLURAL in articles:
                possessive = "tuoi "
                if GRAMMAR.INDETERMINATE in articles:
                    article = "degli "
                elif GRAMMAR.PREPOSITION_IN in articles:
                  article = "negli "  
                else:
                    article = "gli "
            else:
                possessive = "tuo "
                if GRAMMAR.INDETERMINATE in articles:
                    article = "uno "
                elif GRAMMAR.PREPOSITION_IN in articles:
                  article = "nel "  
                else:
                    article = "lo "
        else:
            if GRAMMAR.PLURAL in articles:
                if GRAMMAR.POSSESSIVE not in articles and is_vowel(word[0]):
                    possessive = ""
                    if GRAMMAR.INDETERMINATE in articles:
                        article = "degli "
                    elif GRAMMAR.PREPOSITION_IN in articles:
                      article = "negli "  
                    else:
                        article = "gli "
                else:
                    possessive = "tuoi "
                    if GRAMMAR.INDETERMINATE in articles:
                        article = "dei "
                    elif GRAMMAR.PREPOSITION_IN in articles:
                      article = "nei "  
                    else:
                        article = "i "
            else:
                if GRAMMAR.POSSESSIVE not in articles and is_vowel(word[0]):
                    possessive = ""
                    if GRAMMAR.INDETERMINATE in articles:
                        article = "un "
                    elif GRAMMAR.PREPOSITION_IN in articles:
                      article = "nell'"  
                    else:
                        article = "l'"
                else:
                    possessive = "tuo "
                    if GRAMMAR.INDETERMINATE in articles:
                        article = "un "
                    elif GRAMMAR.PREPOSITION_IN in articles:
                      article = "nel "  
                    else:
                        article = "il "  # (TD) Ci sarebbe da effettuare un controllo sulle 'h' aspirate, è un'eccezione da gestire col "dizionario italiano" implementato

    # Cancella l'articolo possessivo se non ci vuole
    if GRAMMAR.POSSESSIVE not in articles:
        possessive = ""
    return article + possessive
#- Fine Funzione -


def add_article(argument, *articles):
    """
    Ritorna l'articolo voluto adeguato all'argomento e argomento.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    return get_article(argument, *articles) + argument
#- Fine Funzione -


def clean_and_add_article(argument, type, genre=GRAMMAR.MASCULINE, number=GRAMMAR.SINGULAR):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    if not type:
        log.bug("type non è un parametro valido: %r" % type)
        return ""

    if not genre:
        log.bug("genre non è un parametro valido: %r" % genre)
        return ""

    if not number:
        log.bug("number non è un parametro valido: %r" % number)
        return ""

    # -------------------------------------------------------------------------

    colorless = remove_colors(argument)
    if not colorless:
        log.bug("la stringa %s è formata solo da colori" % argument)
        return ""

    # Ci sono casi particolari in cui non serve convertire aggiungendo un articolo
    # altrimenti vengono furoi cose come:
    # Posi un piccone nell'all'interno delle miniere.
    if type == GRAMMAR.PREPOSITION_IN and colorless[ : 4] in ("all'", "alla", "agli", "alle"):
        return argument

    if colorless[ : 6] in ("degli "):
        old_article = colorless[ : 6]
        genre = GRAMMAR.MASCULINE
        number = GRAMMAR.PLURAL
    elif colorless[ : 6] in ("delle "):
        old_article = colorless[ : 6]
        genre = GRAMMAR.FEMININE
        number = GRAMMAR.PLURAL
    elif colorless[ : 4] in ("dei "):
        old_article = colorless[ : 4]
        genre = GRAMMAR.MASCULINE
        number = GRAMMAR.PLURAL
    elif colorless[ : 4] in ("una "):
        old_article = colorless[ : 4]
        genre = GRAMMAR.FEMININE
        number = GRAMMAR.SINGULAR
    elif colorless[ : 4] in ("gli "):
        old_article = colorless[ : 4]
        genre = GRAMMAR.MASCULINE
        number = GRAMMAR.PLURAL
    elif colorless[ : 3] in ("il ", "un "):
        old_article = colorless[ : 3]
        genre = GRAMMAR.MASCULINE
        number = GRAMMAR.SINGULAR
    elif colorless[ : 3] in ("la ", "un'"):
        old_article = colorless[ : 3]
        genre = GRAMMAR.FEMININE
        number = GRAMMAR.SINGULAR
    elif colorless[ : 3] in ("le "):
        old_article = colorless[ : 3]
        genre = GRAMMAR.FEMININE
        number = GRAMMAR.PLURAL
    elif colorless[ : 2] in ("i "):
        old_article = colorless[ : 2]
        genre = GRAMMAR.MASCULINE
        number = GRAMMAR.PLURAL
    elif colorless[ : 2] in ("l'"):
        old_article = colorless[ : 2]
        genre = get_grammar_genre(colorless)  # (bb) essendo is_masculine non terminato qui potrebbe ritornare baco al momento
        number = GRAMMAR.SINGULAR
    else:
        old_article = ""

    article = get_article(colorless[len(old_article) : ], genre, number, type)

    # Eseguendo la replace tenta di mantenere la colorazione originale,
    # altrimenti ne invia una versione semplicificata senza colori
    # (bb) sì lo so, non è perfetta perché se l'articolo è formato da più
    # colori il sistema non regge, ma per ora va bene così
    if argument.find(old_article) != -1:
        return argument.replace(old_article, article, 1)
    else:
        return colorless.replace(old_article, article, 1)
#- Fine Funzione -


def depends_on_vowel(argument, with_vowel, without_vowel):
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    if not with_vowel:
        log.bug("with_vowel non è un parametro valido: %r" % with_vowel)
        return ""

    if not without_vowel:
        log.bug("without_vowel non è un parametro valido: %r" % without_vowel)
        return ""

    # -------------------------------------------------------------------------

    cleaned_argument = clean_string(argument)
    if is_vowel(cleaned_argument[0]):
        return with_vowel + argument
    else:
        return without_vowel + argument
#- Fine Funzione -
