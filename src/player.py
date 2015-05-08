# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei giocatori.
"""


#= IMPORT ======================================================================

from twisted.internet import error

import collections
import datetime
import math
import random

from src.account      import get_error_message_name
from src.color        import remove_colors
from src.connection   import connections
from src.config       import config
from src.database     import database
from src.engine       import engine
from src.element      import Element, Flags
from src.enums        import FLAG, LOG, OPTION, RACE, SEX, TO, TRUST, WAY
from src.gamescript   import check_trigger
from src.grammar      import grammar_gender
from src.log          import log
from src.mail         import mail
from src.mob          import ProtoMob, Mob, create_random_mob
from src.name         import create_random_name
from src.utility      import is_same, is_prefix
from src.web_resource import IFRAME_BROWSERS, OUTPUT_END_TAG, create_tooltip

if config.reload_commands:
    reload(__import__("src.commands.command_look", globals(), locals(), [""]))
    reload(__import__("src.commands.command_snoop", globals(), locals(), [""]))
from src.commands.command_look      import command_look
from src.commands.command_snoop     import remove_and_count_snooped_by


#= VARIABILI ===================================================================

# Genera la lista con tutte le quantità di esperienza che servono per passare
# l'attuale livello del personaggio al prossimo.
# Il calcolo è stato effettuato tramite uno sviluppo di Taylor della funzione
# esponenziale centrato nel punto exp(6.4)
experiences = [0]
for lvl in xrange(1, config.max_level):
    exp = int(math.exp(6.4) * (lvl + (lvl ** 2) / (2.0) + (lvl ** 3) / (6.0) + (lvl ** 4) / (5040.0)))
    experiences.append(exp)

#for lvl, exp in enumerate(experiences):
#    print lvl, exp

#= CLASSI ======================================================================

class Player(Mob):
    """
    L'entità relativa ad un personaggio.
    Player non utilizza come chiave primaria il nome perché questo può essere
    colorato, utilizza quindi una versione ripulita dai colori e la salva in
    code, considerata la vera chiave primaria.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ProtoMob.VOLATILES + Mob.VOLATILES + ["inactivity", "idle_seconds"]
    MULTILINES  = Mob.MULTILINES + []
    SCHEMA      = {"created_time"       : ("",        "datetime"),
                   "login_time"         : ("",        "datetime"),
                   "logout_time"        : ("",        "datetime"),
                   "ban"                : ("src.ban", "Ban"),
                   "visited_areas"      : ("",        "int"),
                   "visited_rooms"      : ("",        "int"),
                   "readed_books"       : ("",        "int"),
                   "digged_rooms"       : ("",        "int"),
                   "eated_entities"     : ("",        "int"),
                   "drinked_entities"   : ("",        "int"),
                   "possessed_entities" : ("",        "int"),
                   "sensed_entities"    : ("",        "int"),
                   "sensed_rooms"       : ("",        "int"),
                   "interred_entities"  : ("",        "int"),
                   "opened_entities"    : ("",        "int"),
                   "unlocked_entities"  : ("",        "int"),
                   "unbolted_entities"  : ("",        "int"),
                   "entered_entities"   : ("",        "int"),
                   "selled_entities"    : ("",        "int"),
                   "bought_entities"    : ("",        "int")}
    SCHEMA.update(ProtoMob.SCHEMA)
    SCHEMA.update(Mob.SCHEMA)
    del(SCHEMA["behaviour"])  # I giocatori non hanno comportamenti automatici
    REFERENCES  = {"account" : ["accounts"],
                   "gifts"   : ["proto_items", "proto_mobs"]}
    REFERENCES.update(ProtoMob.REFERENCES)
    REFERENCES.update(Mob.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(ProtoMob.WEAKREFS)
    WEAKREFS.update(Mob.WEAKREFS)

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = False
    IS_EXIT   = False
    IS_WALL   = False
    IS_ACTOR  = True
    IS_MOB    = False
    IS_ITEM   = False
    IS_PLAYER = True
    IS_EXTRA  = False
    IS_PROTO  = False

    ACCESS_ATTR   = "players"
    CONSTRUCTOR   = None  # Classe Player una volta che viene definita a fine modulo

    def __init__(self, name=""):
        super(Player, self).__init__(code="")

        # Il codice non bisogna passarlo come parametro nell'inizializzazione
        # degli attributi perché viene ricavato dal nome
        if name:
            self.code = remove_colors(name)
            self.name = name

        # Rimuove o deinizializza gli attributi inutili per i giocatori
        del(self.behaviour)
        del(self.keywords_name)
        del(self.keywords_short)
        del(self.keywords_short_night)
        del(self.prototype)

        self.life           = config.starting_points
        self.mana           = config.starting_points
        self.vigour         = config.starting_points
        self.max_life       = self.life
        self.max_mana       = self.mana
        self.max_vigour     = self.vigour

        self.strength       = config.starting_attrs
        self.endurance      = config.starting_attrs
        self.agility        = config.starting_attrs
        self.speed          = config.starting_attrs
        self.intelligence   = config.starting_attrs
        self.willpower      = config.starting_attrs
        self.personality    = config.starting_attrs
        self.luck           = config.starting_attrs

        # Variabile proprie di un'istanza di Player
        self.created_time        = datetime.datetime.now()  # Data di creazione del personaggio
        self.account             = None  # Account del giocatore che contiene questo personaggio
        self.permissions         = ""  # Permessi aggiunti alla normale trust
        self.surname             = ""  # Cognome o simile
        self.old_names           = ""  # Tiene traccia dei vecchi nomi in caso di restring del nome
        self.title               = ""  # Titolo con cui è conosciuto il personaggio
        self.target_descr        = ""  # Descrizione dell'obiettivo che il personaggio vuole perseguire
        self.login_time          = None
        self.logout_time         = None
        self.inactivity          = 0
        self.seconds_played      = 0
        self.login_times         = 0
        self.last_input          = "guarda"  # Ultimo input inviato al Mud
        self.reputations         = {}  # Reputazione nei confronti delle varie razze
        self.talents             = 0
        self.practices           = 0
        self.gifts               = []
        self.idle_seconds        = 0
        self.ban                 = None
        self.visited_areas       = {}  # Indica quali aree sono state visitate e quante volte
        self.visited_rooms       = {}  # Indica quali aree e quali room sono state visitate almeno una volta
        self.readed_books        = {}  # Indica quali libri sono stati letti almeno una volta
        self.digged_rooms        = {}  # Indica quali stanze sono state stavate almeno una volta
        self.eated_entities      = {}  # Indica quali entità sono state mangiate almeno una volta
        self.drinked_entities    = {}  # Indica quali entità sono state bevute almeno una volta
        self.possessed_entities  = {}  # Indica quali entità sono state possedute in inventario almeno una volta
        self.sensed_entities     = {}  # Indica quali entità sono state esaminate con un comando sensoriale che non sia il look
        self.sensed_rooms        = {}  # Indica quali stanze sono state esaminate con un comando sensoriale che non sia il look
        self.interred_entities   = {}  # Indica quali entità sono state interrate tramite il comando plant o il comando seed
        self.opened_entities     = {}  # Indica quali entità sono state aperte tramite il comando open
        self.unlocked_entities   = {}  # Indica quali entità sono state sbloccate tramite il comando unlock
        self.unbolted_entities   = {}  # Indica quali entità sono state svincolate tramite il comando unbolt
        self.entered_entities    = {}  # Indica quali entità sono state utilizzate come portali tramite il comando enter
        self.selled_entities     = {}  # Indica quali entità sono state vendute tramite il comando sell
        self.bought_entities     = {}  # Indica quali entità sono state vendute tramite il comando buy

        # Variabili volatili
        self.sended_inputs  = collections.deque([], 100)  # Lista degl input inviati dal giocatore
        self.backsteps      = collections.deque([], 100)  # Lista delle locazioni cui l'entità si è trovata precedentemente
    #- Fine Inizializzazione -

    def get_error_message(self):
        """
        Controlla l'integrità degli attributi.
        """
        msg = super(Player, self).get_error_message()
        if msg:
            pass
        elif get_error_message_name(self.name, True, "players") != "":
            msg = get_error_message_name(self.name, True, "players")
        elif self.trust.get_error_message(TRUST, "trust") != "":
            msg = self.trust.get_error_message(TRUST, "trust")
        elif not self.account:
            msg = "Questo personaggio non è legato a nessun account valido: %r" % self.account
        elif self.code not in self.account.players:
            msg = "Non esiste nessun personaggio col codice %s nell'account %s" % (self.code, self.account.name)
        elif self.seconds_played < 0:
            msg = "seconds_played essendo una quantità di ore non può essere minore di zero: %d" % self.seconds_played
        elif not self.last_input:
            msg = "last_input in teoria non deve essere mai una stringa vuota"
        elif self.get_error_message_reputations() != "":
            msg = self.get_error_message_reputations()
        # (TD) controllare anche le variabili volatili
        else:
            return ""

        log.bug("(Player: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    def get_error_message_reputations(self):
        """
        Se vi è un errore negli attributi che salvano la reputazione ritorna
        un messaggio.
        """
        for race, reputation in self.reputations.iteritems():
            if race not in RACE.elements:
                return "razza %s non è un elemento di razza valido per la reputazione delle razze" % race
            if reputation < -100 or reputation > 100:
                return "reputazione della razza %s deve essere tra -100 e 100" %  reputation
        return ""
    #- Fine Metodo -

    #---------------------------------------------------------------------------

    def enter_in_game(self):
        force_return = check_trigger(self, "before_enter_in_game", self)
        if force_return:
            return

        # Resetta il contatore di idle, è normale che conn non sia valido
        # durante il test degli inputs
        conn = self.get_conn()
        if conn:
            conn.reinit()
        elif not engine.test_inputs_mode:
            log.bug("conn non è valido: %r" % conn)
            return

        # Se il pg ha impostato l'incognito ma non è un admin allora gli
        # viene rimosso
        if self.incognito and self.trust == TRUST.PLAYER:
            log.admin("Rimozione automatica dell'incognito al giocatore %s" % self.code)
            self.incognito = False

        # Se la stanza in cui il personaggio si trova è ancora impostata
        # significa che il giocatore si sta riconnettendo (per colpa di un
        # crash oppure utilizzando un altro browser)
        if self.location:
            # Ripulisce qualsiasi precedente istanza di connessione alla pagina
            # del gioco che non sia quella attuale
            actual_session = self.game_request.getSession()
            for session, connection in connections.iteritems():
                if session == actual_session:
                    continue
                if connection.account and OPTION.COMET not in connection.account.options:
                    continue
                if ("/game_input.html" in repr(connection.request)
                or  "/game_output.html" in repr(connection.request)):
                    # (TT) in realtà qui dovrei ucciderla o unpausarla,
                    # altrimenti mi occupa spazio di memoria, magari aggiungerla
                    # come lista alle precedenti deferrenti di questa connessione
                    connection.defer_exit_from_game.pause()
                    connection.defer_exit_from_game = None
                    del(connection)
            # Se un pg si riconnette non avvisa via mail
            send_a_mail = False
            log_message = "%s si riconnette al gioco" % self.code
        # Qui dovrebbe passare per tutti i personaggi che sono entrati almeno
        # una volta in gioco e che non hanno avuto problemi di sorta
        elif self.previous_location and self.previous_location() and not self.previous_location().IS_PLAYER:
            location = self.previous_location()
            self.previous_location = None
            self.to_location(location, use_iterative_put=False)
            send_a_mail = True
            self.login_times += 1
            log_message = "%s entra nel gioco per la %d° volta" % (self.code, self.login_times)
        # Se la stanza in cui se ne era andato il personaggio non è stata
        # impostata durante il quit allora significa che il giocatore è nuovo
        # oppure c'è stato un baco che ne ha corrotto il riferimento
        else:
            destination_room = config.initial_destination.get_room()
            if not destination_room:
                log.bug("destination_room non valida: %r" % destination_room)
                return
            self.to_location(destination_room, use_iterative_put=True)
            send_a_mail = True
            self.login_times += 1
            log_message = "%s entra nel gioco per la %d° volta" % (self.code, self.login_times)

        if not engine.test_inputs_mode:
            log.always(log_message)

        # Controlla se deve donare un'entità all'evento a cui il giocatore
        # sta partecipando; il regalo può essere sia un oggetto che un mob
        if config.gift_on_enter and config.gift_on_enter not in self.gifts:
            gift = config.gift_on_enter.CONSTRUCTOR(config.gift_on_enter.code)
            if gift:
                # Si presuppone che i gift non abbiano il max_global_quantity
                gift.inject(self)
                self.gifts.append(config.gift_on_enter)
            else:
                log.bug("Impossibile creare il dono %s per %s: %r" % (
                    config.gift_on_enter.code, self.code, gift))

        # Avvisa gli admin via mail se un pg è appena entrato nel Mud
        if self.account and self.account.trust > TRUST.PLAYER:
            send_a_mail = False
        for player in self.account.players.itervalues():
            if player.trust > TRUST.PLAYER:
                send_a_mail = False
        if send_a_mail and config.mail_on_enter_in_game:
            mail.send_to_admins(log_message, "%s è un %s di livello %s dell'account %s." % (
                self.code,
                self.sex_replacer(remove_colors(self.race.name)),
                self.level,
                self.account.name if self.account else "<Errore>"))

        eyes = self.eye_colorize("occhi")
        self.act("Ti materializzi poco a poco dal nulla e poi apri gli %s.\n" % eyes, TO.ENTITY)
        self.act("$n si materializza poco a poco dal nulla e apre gli %s come se si stesse svegliando." % eyes, TO.OTHERS)
        command_look(self)

        self.inactivity = 0

        log.connections()

        force_return = check_trigger(self, "after_enter_in_game", self)
        if force_return:
            return
    #- Fine Metodo -

    def exit_from_game(self, success):
        """
        Viene chiamata quando uno esegue un logout, voluto o non voluto, dalla
        pagina di gioco.
        """
        force_return = check_trigger(self, "before_exit_from_game", self)
        if force_return:
            return

        remove_and_count_snooped_by(self)
        self.incognito = False

        # Si assicura di togliere eventuali giocatori al suo interno
        for player in self.iter_all_entities(use_reversed=True):
            if not player.IS_PLAYER:
                continue
            self.act("$n se ne va evitando di portare con sé $N che sbuca fuori.", TO.OTHERS, player)
            self.act("Sbuchi fuori da $n che se ne va evitando di portarti con te.", TO.TARGET, player)
            player = player.from_location(1, use_repop=False)
            # (TD) Questo pezzo di codice ricorda vagamente lo stesso in
            # enter_in_game, magari accorpare?
            if self.location:
                player.to_location(self.location)
            elif self.previous_location and self.previous_location():
                player.to_location(self.previous_location())
            else:
                destination_room = Destination(0, 0, 1, "novizi").get_room()
                if destination_room:
                    player.to_location(destination_room)
                else:
                    # (TD) pescare il menhir dell'area oppure quello di novizi
                    log.bug("Non è stata trovata nessuna stanza iniziale valida: %r" % destination_room)
                    return

        # Estrae le eventuali entità al suo interno con l'apposita flag,
        # solitamente sono entità relative a delle quest la cui estrazione
        # può portare al reset della relativa quest
        for en in self.iter_all_entities(use_reversed=True):
            if FLAG.EXTRACT_ON_QUIT in en.flags:
                self.send_output("%s ti si dissolve in polvere.", en.get_name(looker=self))
                en.extract(en.quantity)

        if self.location:
            #eyes = self.eye_colorize("occhi")
            #self.act("\nChiudi gli %s come se ti stessi addormentando per poi svanire poco a poco..." % eyes, TO.ENTITY)
            #self.act("$n chiude gli %s come se si stesse addormentando e poi svanisce poco a poco..." % eyes, TO.OTHERS)
            self = self.from_location(1, use_iterative_remove=False, use_repop=False)

        # Resetta la connessione reinizializzandola
        for connection in connections.itervalues():
            if connection.player and connection.player.code == self.code:
                connection.defer_exit_from_game = None
                connection.player = None

        if self.action_in_progress and self.action_in_progress.defer_later:
            self.action_in_progress.stop()
        self.action_in_progress = None

        # (TD) defer(10, request.finish) per evitare che i pg se ne
        # approfittino ad uscire dal gioco durante i combat
        self.game_request = None
 
        self.logout_time = datetime.datetime.now()

        if self.inactivity > 0:
            message = "%s esce dal gioco dopo %d secondi di inattività" % (self.code, self.inactivity)
        else:
            message = "%s esce dal gioco" % self.code
        log.always(message)

        # Salva il numero di connessioni attive in questo dato momento
        log.connections()

        force_return = check_trigger(self, "after_exit_from_game", self)
        if force_return:
            return
    # - Fine del Funzione -

    def dies(self, opponent=None, auto_loot=False, teleport_corpse=False):
        force_return = check_trigger(self, "before_die", self, opponent)
        if force_return:
            return
        if opponent:
            force_return = check_trigger(opponent, "before_dies", self, opponent)
            if force_return:
                return

        #self.send_output('''<script>$("#output").vibrate();</script>''')  # (bb)
        if not self.location:
            log.always("%s è mort%s." % (self.get_name(), grammar_gender(self)), log_stack=False)
        else:
            log.always("%s è mort%s a %s" % (self.get_name(), grammar_gender(self), self.location.get_name()), log_stack=False)
        self.life = 1
        remains, use_repop = self.make_remains(auto_loot)
        remains.corpse_type.was_player = True
        if teleport_corpse:
            self.recall(also_entities=[remains])
        else:
            self.recall()
        self.flags -= FLAG.BEATEN

        if self.action_in_progress and self.action_in_progress.defer_later:
            self.action_in_progress.stop()
        self.action_in_progress = None

        force_return = check_trigger(self, "after_die", self, opponent)
        if force_return:
            return
        if opponent:
            force_return = check_trigger(opponent, "after_dies", self, opponent)
            if force_return:
                return
    #- Fine Metodo -

    def recall(self, message=True, also_entities=None):
        if not also_entities:
            also_entities = []

        if message:
            self.send_output("Verrai teletrasportat%s al [white]Menhir della Vita[close] più vicino." % grammar_gender(self))
            self.send_prompt(show_opponent=False)

        destination_room = config.initial_destination.get_room()
        if not destination_room:
            log.bug("destination_room non valida: %r" % destination_room)
            return

        self = self.from_location(1, use_repop=False)
        self.to_location(destination_room, use_look=True)
        self.send_prompt()

        for entity in also_entities:
            entity = entity.from_location(entity.quantity, use_repop=False)
            entity.to_location(destination_room, use_look=True)
            entity.send_prompt()
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_conn(self):
        """
        Ricava l'attuale connessione del giocatore dalla game_request.
        """
        if self.game_request:
            # Prima cerca di ricavare la connessione ciclando sulle connessioni
            for connection in connections.values():
                if connection.player == self:
                    return connection

            # Nell'eventualità remota che non ve la faccia prova nell'altro modo
            try:
                session = self.game_request.getSession()
            except error.AlreadyCalled:
                return None
            if session in connections:
                return connections[session]

        return None
    #- Fine Metodo -

    def update(self):
        """
        Aggiorna i valori relativi ad un'istanza di personaggio.
        """
        if self.account and OPTION.COMET in self.account.options:
            if self.get_conn().get_browser() not in IFRAME_BROWSERS:
                self.game_request.write(OUTPUT_END_TAG)
        self.seconds_played += 1
        self.inactivity += 1

        if FLAG.INGESTED in self.flags:
            return

        pass
    #- Fine Metodo -

    def give_experience(self, experience, reason="", first_the_prompt=False):
        """
        Questo metodo dovrebbe essere sempre utilizzato per dare quantità
        positive di esperienza al giocatore, la chiamata al metodo deve essere
        inoltre accompagnata dalla ragione per cui eventualmente tale quantità
        faccia passare di livello (a meno che non sia ovvio come nel caso di
        una vittoria in combattimento).
        """
        if experience <= 0:
            log.bug("experience non è un parametro valido: %d" % experience)
            return

        # ---------------------------------------------------------------------

        if config.exp_modifier != 100:
            experience = (experience * config.exp_modifier) / 100

        if experience > 0:
            self.experience += max(1, experience)
            if self.level < config.max_level and self.experience >= experiences[self.level]:
                self.raise_level(reason, first_the_prompt=first_the_prompt)
    #- Fine Metodo -

    def raise_level(self, reason="", first_the_prompt=False):
        while self.level < config.max_level and self.experience >= experiences[self.level]:
            self.level     += 1
            self.talents   += 200
            self.practices += 2

        if config.leveling_restore_points:
            self.life   = self.max_life
            self.mana   = self.max_mana
            self.vigour = self.max_vigour

        if reason:
            tooltip = create_tooltip(self.get_conn(), "Sei passato al livello %d %s!" % (self.level, reason), "{?}")
        else:
            tooltip = create_tooltip(self.get_conn(), "Sei passato al livello %d!" % self.level, "{?}")
        if first_the_prompt:
            self.send_prompt()
        self.act("\nTi sembra di essere cambiat$o... di essere migliore! %s" % tooltip, TO.ENTITY)
        self.act("Hai come l'impressione che $n sia cambiat$o in qualcosa..", TO.OTHERS)
        self.send_output('''<script>$("#talents_title").parent().show();</script>''', break_line=False)
        if not first_the_prompt:
            self.send_prompt()

        log.monitor("%s è passato al livello %d" % (self.name, self.level))
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def search_online_player(argument, only_exact=False):
    """
    A volte è meglio dare precedenza alla ricerca dei giocatori online al posto
    di quelli offline per comodità, poiché spesso gli admin inseriscono
    l'abbreviazione di un player correntemente online.
    """
    for player in database["players"].itervalues():
        if not player.game_request:
            continue
        if is_same(argument, player.name):
            return player

    if only_exact:
        return None

    for player in database["players"].itervalues():
        if not player.game_request:
            continue
        if is_prefix(argument, player.name):
            return player

    return None
#- Fine Funzione -


def create_random_player(name="", level=0, race=RACE.NONE, sex=SEX.NONE, way=WAY.NONE):
    """
    Crea un personaggio con caratteristiche casuali, serve principalmente per
    testing, per esempio per creare due personaggi che combattano tra loro.
    """
    if not name and name != "":
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

    if not way:
        log.bug("way non è un parametro valido: %r" % way)
        return

    # -------------------------------------------------------------------------

    player = Player()
    player = create_random_mob(player, name, level, race, sex, way)

    # Ora che player possiede una razza ed un sesso può creare un nome
    # casuale se questo non è stato passato
    if not player.name:
        player.name = create_random_name(player.race, player.sex, is_player_name=True)
    player.code = remove_colors(player.name.lower())

    # Crea il giocatore con i dati di base
    # (TD) dovrei impostare casualmente tanti altri attributi
    player.flags.randomize()
    create_random_reputations(player)

    return player
#- Fine Funzione -


def create_random_reputations(player):
    player.reputations = {}

    # (TD)
#- Fine Funzione -


#= FINALIZE ====================================================================

Player.CONSTRUCTOR = Player
