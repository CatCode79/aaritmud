# -*- coding: utf-8 -*-

"""
Modulo relativo alla gestione degli account dei giocatori.
Tramite un account il giocatore può gestire più personaggi accedendo, tramite
login, ad una pagina web; in tale pagina si potranno anche modificare ed
accedere ad altre opzioni.
In minima parte l'account è anche uno strumento per tenere d'occhio il
multiplaying (dico in piccola parte poiché dopotutto qualsiasi giocatore può
creare più account inserendo indirizzi mail differenti).
"""


#= IMPORT ======================================================================

import datetime
import math
import random
import re
import string

from src.accent    import count_accents, isalpha_accent, isalnum_accent
from src.channel   import swearwords, offrpg_words
from src.color     import remove_colors
from src.config    import config
from src.data      import Data
from src.database  import database
from src.element   import Element, Flags
from src.entity    import little_words
from src.enums     import LOG, OPTION, TRUST, RACE, SEX
from src.log       import log
from src.interpret import interpret
from src.name      import create_random_name
from src.utility   import is_same


#= VARIABILI ===================================================================

# Lunghezza massima per un indirizzo email, qui abbondo, il controllo
# vero e proprio è eseguito da una regex
MAX_LEN_EMAIL    = 192

forbidden_names = []


#= CLASSI ======================================================================

class Account(Data):
    """
    Contiene tutte le informazioni e le opzioni di un Account di gioco, in
    esso c'è anche la lista dei personaggi creati e giocabili dal giocatore
    dell'account.
    """
    PRIMARY_KEY = "name"
    VOLATILES   = ["player", "players"]
    MULTILINES  = []
    SCHEMA      = {"players"                : ("src.player",  "Player"),
                   "player"                 : ("src.player",  "Player"),
                   "aliases"                : ("src.account", "Alias"),
                   "macros"                 : ("src.account", "Macro"),
                   "user_agents"            : ("",            "str"),
                   "created_time"           : ("",            "datetime"),
                   "last_bug_sended_at"     : ("",            "datetime"),
                   "last_comment_sended_at" : ("",            "datetime"),
                   "last_typo_sended_at"    : ("",            "datetime"),
                   "last_idea_sended_at"    : ("",            "datetime")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, name=""):
        self.comment                = ""
        self.created_time           = datetime.datetime.now()  # Data di creazione del'account
        self.name                   = name  # Nome di login
        self.password               = ""    # Password
        self.email                  = ""    # Indirizzo e-mail (opzionale)
        self.options                = Flags(OPTION.NONE)
        self.show_logs              = Flags(LOG.NONE)
        self.aliases                = {}  # Dizionario relativo agli alias
        self.macros                 = {}  # Dizionario relativo alle macro
        # (TD) provare a convertire questi datetime in None e caricarli tramite schema
        self.last_bug_sended_at     = None
        self.last_comment_sended_at = None
        self.last_typo_sended_at    = None
        self.last_idea_sended_at    = None
        self.sended_bugs            = 0  # Bug totali inviati
        self.sended_comments        = 0  # Typo totali inviati
        self.sended_ideas           = 0  # Idee totali inviati
        self.sended_typos           = 0  # Typo totali inviati
        self.user_agents            = [] # Informazioni relative ai client browser utilizzati dal giocatore per entrare nel Mud
        self.resolution_width       = 0  # Risoluzione in pixel del monitor del client in larghezza
        self.resolution_height      = 0  # Risoluzione in pixel del monitor del client in altezza

        # Al primo account creato in assoluto dà poteri di Implementor, dando
        # per scontato che il primo giocatore che utilizza questo Mud sia il
        # futuro amministratore, ai successivi account dona la trust di player
        if not database["accounts"]:
            self.trust = Element(TRUST.IMPLEMENTOR)
        else:
            self.trust = Element(TRUST.PLAYER)

        # Attributi volatili
        self.players = {}  # Dizionario dei giocatori creati dall'account
        self.player  = None  # Personaggio che si sta creando o utilizzando
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s" % (super(Account, self).__repr__, self.name)
    #- Fine Metodo -

    def get_error_message(self, already_in_database=True):
        """
        Ritorna una stringa vuota se l'account non ha errori, altrimenti il
        messaggio d'errore.
        Bisogna passare l'argomento already_in_database uguale a False quando
        si controlla l'integrità di un account appena creato e che non si è
        ancora aggiunto al database degli account.
        """
        msg = ""
        if already_in_database != True and already_in_database != False:
            msg = "L'argomento already_in_database non è un booleano valido: %s" % already_in_database

        # ---------------------------------------------------------------------

        # self.player è lecito che sia anche None se l'account non sta giocando

        if msg:
            pass
        elif get_error_message_name(self.name, already_in_database) != "":
            msg = "%s: %s" % (get_error_message_name(self.name, already_in_database), self.name)
        elif get_error_message_password(self.password) != "":
            msg = "%s: %s" % (get_error_message_password(self.password), self.password)
        elif get_error_message_email(self.email, already_in_database) != "":
            msg = "%s: %s" % (get_error_message_email(self.email, already_in_database), self.email)
        elif self.trust.get_error_message(TRUST, "trust") != "":
            msg = self.trust.get_error_message(TRUST, "trust")
        elif self.options.get_error_message(OPTION, "options") != "":
            msg = self.options.get_error_message(OPTION, "options")
        elif self.show_logs.get_error_message(LOG, "logs") != "":
            msg = self.show_logs.get_error_message(LOG, "logs")
        elif len(self.players) > config.max_account_players:
            msg = "Numero di personaggi superiore a %s" % config.max_account_players
        elif self._get_error_message_only_one_player() != "":
            msg = self._get_error_message_only_one_player()
        elif len(self.aliases) > config.max_aliases:
            msg = "Numero degli alias superiore al massimo (%d): %d" % (config.max_aliases, len(self.aliases))
        elif len(self.macros) > config.max_macros:
            msg = "Numero delle macro superiore al massimo (%d): %d" % (config.max_macros, len(self.macros))
        elif self.resolution_width < 0:
            msg = "Risoluzione del client in larghezza errato: %d" % self.resolution_width
        elif self.resolution_height < 0:
            msg = "Risoluzione del client in altezza errato: %d" % self.resolution_height
        else:
            return ""

        # Se ha trovato un errore invia il relativo messaggio
        log.bug("(Account: name %s) %s" % (self.name, msg))
        return msg
    #- Fine Metodo -

    def _get_error_message_only_one_player(self):
        """
        Controlla che due o più account non utilizzino lo stesso player.
        """
        for player in self.players.itervalues():
            for account in database["accounts"].itervalues():
                if account.name == self.name:
                    continue
                if player.code in account.players:
                    return "Personaggio %s già esistente nell'account %s" % (player.code, account.name)
        return ""
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_id(self):
        """
        Ritorna una o tutte tra le seguenti informazioni: il nome dell'account
        e il nome del personaggio.
        Molto utile da utilizzare nei messaggi di log.
        Questo metodo fa a coppia con quello nella classe Connection.
        """
        player_name = "None"
        if self.player:
            player_name = self.player.code

        return "%s.%s" % (self.name, player_name)
    #- Fine Metodo -

    def check_alias(self, arg, argument):
        """
        Controlla se argument sia un alias di un pg, se sì lo ritorna.
        """
        if not arg:
            log.bug("arg non è un parametro valido: %r" % arg)
            return

        # ---------------------------------------------------------------------

        if arg not in self.aliases:
            return False

        alias = self.aliases[arg]
        argument = argument or ""
        interpret(self.player, "%s %s" % (alias.action, argument), use_check_alias=False)
        return True
    #- Fine Metodo -


class Alias(object):
    """
    Gestisce un alias di un giocatore, ovvero un input personalizzato dal
    giocatore.
    """
    PRIMARY_KEY = "name"
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.name   = ""
        self.action = ""
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s" % (super(Alias, self).__repr__, self.name)
    #- Fine Metodo -

    def get_error_message(self):
        if not self.name:
            msg = "Il nome dell'alias non è valido."
        elif not self.action:
            msg = "L'azione dell'alias non è valida."
        else:
            msg = ""
    #- Fine Metodo -


#class Macro(object):
#    """
#    Gesciste una macro-bottone personalizzabile dal giocatore.
#    """
#    def __init__(self):
#        self.key = ""
#    #- Fine Inizializzazione -
#
#    def __repr__(self):
#        return "%s %s" % (super(Alias, self).__repr__, self.key)
#    #- Fine Metodo -


#= FUNZIONI ====================================================================

def load_forbidden_names():
    """
    Carica da un file la lista dei nomi proibiti per la creazione di nuovi
    account o giocatori.
    """
    global forbidden_names

    forbidden_names_path = "data/forbidden_names.list"
    try:
        forbidden_names_file = open(forbidden_names_path, "r")
    except IOError:
        log.bug("Impossibile aprire il file %s in lettura" % forbidden_names_path)
        return

    for line in forbidden_names_file:
        line = line.strip()
        if not line:
            continue
        forbidden_names.append(line)

    forbidden_names_file.close()
#- Fine Funzione -


def add_players_to_accounts():
    for player in database["players"].itervalues():
        if not player.account:
            log.bug("Account non valido per il giocatore %s: %r" % (player.name, player.account))
            continue
        database["accounts"][player.account.name].players[player.code] = player
#- Fine Funzione -


def get_error_message_name(name, already_in_database, table_name="accounts"):
    """
    Controlla che il nome passato sia valido.
    Questa funzione viene utilizzata sia per i nomi degli account sia per
    quelli dei personaggi.
    Ritorna un messaggio vuoto se tutto è a posto, altrimenti il primo
    messaggio d'errore incontrato.
    Bisogna passare l'argomento already_in_database uguale a False quando si
    controlla l'integrità di un nome di Account o di Player appena creati e
    non ancora aggiunti al relativo database, viceversa bisogna passarlo a True.
    """
    if table_name not in ("players", "accounts"):
        return "L'argomento table_name non è valido: %s" % table_name

    # -------------------------------------------------------------------------

    name = name or ""

    # Se è un nome di un personaggio rimuove gli eventuali codici css
    if table_name == "players":
        name = remove_colors(name)

    # Controlla la lunghezza del nome
    length = len(name)
    if length < config.min_len_name:
        return "Nome troppo corto, deve essere almeno di %d caratteri." % config.min_len_name
    if length > config.max_len_name:
        return "Nome troppo lungo, può essere al massimo lungo %d caratteri." % config.max_len_name

    # Controlla che i caratteri del nome siano solo alfabetici o accentati
    # (BB) c'è ancora il problema degli accenti che non vengono letti da scritte
    # inviate tramite web, commentate alcune righe in favore di un rimpiazzo
    # in attesa del python 3.0 per risolvere la faccenda
    if table_name == "accounts" and not isalnum_accent(name):
        #return "Il nome può essere formato solo da lettere (accentate o meno) e da numeri."
        return "Il nome può essere formato solo da lettere e da numeri."
    if table_name == "players" and not isalpha_accent(name):
        #return "Il nome può essere formato solo da lettere (accentate o meno)."
        return "Il nome può essere formato solo da lettere."

    # Il nome può avere in più un accento per ogni tre caratteri
    if count_accents(name) > len(name) / 3:
        return "Il nome, per essere maggiormente leggibile, può avere solo un accento ogni tre caratteri."

    # Controlla che il nome abbia una determinata varietà di caratteri inseriti
    # per evitare nomi come Aaa
    if len(set(name.lower())) < math.floor(math.log(len(name)) * 2):
        return "Nome troppo poco vario, utilizzare un maggior numero di vocali o consonanti differenti"

    # Controlla se esiste già il nome nel database passato, bisogna utilizzare
    # is_same() altrimenti nomi simili, ma uno con vocale semplice e l'altro
    # con vocale accentanta, vengono visti come differenti
    for data in database[table_name].itervalues():
        if is_same(data.name, name) or (hasattr(data, "code") and is_same(data.code, name)):
            # Se si sta controllando un nome già esistente nel database
            # quando lo trova per una volta lo salta
            if already_in_database:
                already_in_database = False
                continue
            return "Il nome è già utilizzato in un altro account."

    # Controlla che il nome non sia una parolaccia, una parola off-rpg, un
    # nome non utilizzabile o una little word, che degenererebbe la creazione
    # dinamica delle kewywords per i personaggi
    for swear_word in swearwords:
        if is_same(swear_word, name):
            return "Il nome non è valido perché è una parolaccia."
    if table_name == "players":
        for offrpg_word in offrpg_words:
            if is_same(offrpg_word, name):
                return "Il nome non è valido perché è una parola non GDR."
        for forbidden_name in forbidden_names:
            if is_same(forbidden_name, name):
                return "Il nome non è valido."
        for little_word in little_words:
            if is_same(little_word, name):
                return "Il nome non è valido."

    # Controlla che la prima lettera sia maiuscola e il resto minuscolo
    if name != name.capitalize():
        return "Il nome non inizia con la maiuscola e il resto minuscolo"

    # Se tutto è ok ritorna un messaggio vuoto
    return ""
#- Fine Funzione -


def get_error_message_password(password):
    """
    Controlla che l'argomento passato sia una password valida.
    Ritorna un messaggio vuoto se tutto è a posto, altrimenti il primo
    messaggio d'errore incontrato.
    """
    password = password or ""

    # Controlla la lunghezza della password
    if len(password) < config.min_len_password:
        return "Password troppo corta, inserisci almeno %d caratteri.\n" % config.min_len_password
    elif len(password) >= config.max_len_password:
        return "Password troppo lunga, inserisci meno di %d caratteri\n" % config.max_len_password

    # Controlla che sia formata solo da lettere e numeri
    if not password.isalnum():
        return "Per la tua password utilizza solo lettere e numeri.\n"

    # Se tutto è a posto ritorna un messaggio vuoto
    return ""
#- Fine Funzione -


# Compilazione della regex per la validazione delle mail:
PATTERN_EMAIL = re.compile(r"^[-+.\w]{1,64}@[-.\w]{1,64}\.[-.\w]{2,6}$")

def get_error_message_email(email, already_in_database=False):
    """
    Controlla la validità dell'indirzzo mail inserito.
    Ritorna un messaggio vuoto se tutto è a posto, altrimenti il primo messaggio
    d'errore incontrato.
    Bisogna passare l'argomento already_in_database uguale a False quando si
    controlla l'integrità di un indirizzo mail di un Account appena creato non
    ancora aggiunto al database degli account, nel caso contrario bisogna
    passarlo uguale a True.
    """
    # L'inserimento di un indirizzo mail è opzionale
    if not email:
        return ""

    # Controlla la sintassi dell'indirizzo
    if not PATTERN_EMAIL.match(email):
        return "Email inserita non valida."

    # Controlla che non vi sia già un account con lo stesso email
    for account in database["accounts"].itervalues():
        if account.email and is_same(account.email, email):
            # Se si sta modificando l'email questo è già in un account e quindi
            # quando la trova per la prima volta lo salta
            if already_in_database:
                already_in_database = False
                continue
            return "Email inserita già utilizzata in un altro account"

    # Se arriva fino a qui è tutto a posto
    return ""
#- Fine Funzione -


def create_random_account():
    """
    Crea un account casualmente.
    Questa funzione viene utilizzata a scopo di test.
    """
    # Crea un nome di account casuale, si assicura che non esista già nel
    # database degli account altrimenti, nel qual caso che questo account creato
    # casualmente venga inserito nel database, questi vada a sovrascrivere il
    # vecchio account
    random_name = ""
    counter = 0
    while counter < 1000:
        random_name = create_random_name(RACE.NONE.randomize(), SEX.NONE.randomize())
        if random_name not in database["accounts"]:
            break
    if not random_name:
        log.bug("non è stato possibile ricavare random_name dopo %d cicli while" % counter)
    account = Account(random_name)

    password_length = random.randint(config.min_len_password, config.max_len_password)
    account.password = random.sample("abcdefghilmnoprstuvzjywkx1234567890", password_length)

    random_email_1 = create_random_name(RACE.NONE.randomize(), SEX.NONE.randomize())
    random_email_2 = create_random_name(RACE.NONE.randomize(), SEX.NONE.randomize())
    account.email = "%s@%s.it" % (random_email_1, random_email_2)

    account.options.randomize()

    # Qui è meglio non scegliere la Trust casualmente altrimenti potrebbe
    # accedere a poteri che gli permettono di cancellare o creare oggetti a
    # caso senza controlli
    account.trust == TRUST.PLAYER

    return account
#- Fine Funzione -
