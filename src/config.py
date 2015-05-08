# -*- coding: utf-8 -*-

"""
Modulo che gestisce le configurazioni del gioco.
Viene caricato il file di configurazione passato alla funzione start_mud nel
modulo engine.
"""

#= IMPORT ======================================================================

import ConfigParser
import sys

from src.color  import check_colors, colors
from src.log    import log


#= COSTANTI ====================================================================

class ConfigOption(object):
    def __init__(self, name, section, default, facultative, online, getter, setter, minihelp):
        self.name        = name
        self.section     = section
        self.default     = default
        self.facultative = facultative
        self.online      = online
        self.getter      = getter
        self.setter      = setter
        self.minihelp    = minihelp

        if not self.name:
            log.bug("(ConfigOption: ?) name non valido: %r" % self.name)
            return
        if not self.section:
            log.bug("(ConfigOption: %s) section non valido: %r" % (self.name, self.section))
        if not self.getter:
            log.bug("(ConfigOption: %s) getter non valido: %r" % (self.name, self.getter))
        if not self.setter:
            log.bug("(ConfigOption: %s) setter non valido: %r" % (self.name, self.setter))
        if not self.minihelp:
            log.bug("(ConfigOption: %s) minihelp non valido: %r" % (self.name, self.minihelp))
    #- Fine Inizializzazione -


CONFIG_OPTIONS = (
    #            name                          section        default    facult online, getter        setter minihelp
    ConfigOption("http_port",                  "SITE",        0,         False, False,  "getint",     "set", "Porta http con cui i client si collegano al sito. L'opzione non è modificabile online"),
    ConfigOption("site_address",               "SITE",        "http://", False, True,   "get",        "set", "Indirizzo relativo il sito"),
    ConfigOption("allow_web_robots",           "SITE",        False,     False, True,   "getboolean", "set", "Indica se lasciare indicizzare o meno le pagine di aarit da parte dei bot dei motori di ricerca"),
    ConfigOption("google_analytics_ua",        "SITE",        "",        True,  True,   "get",        "set", "User Application ID per google analytics, se viene inserito verrà creato del codice html nell'header di tutte le pagine web dinamiche, l'opzione è facoltativa"),
    ConfigOption("max_google_translate",       "SITE",        500,       False, True,   "getint",     "set", "Lunghezza massima gestita dalle api di google translate"),
    ConfigOption("max_feedback_len",           "SITE",        400,       False, True,   "getint",     "set", "Numero massimo di caratteri inseribili per il feedback riguardo alla compatibilità"),
    ConfigOption("max_square_msg_len",         "SITE",        100,       False, True,   "getint",     "set", "Lunghezza massima postabile sulla piazzetta, a 0 significa che è disattivata"),
    ConfigOption("max_square_messages",        "SITE",        100,       False, True,   "getint",     "set", "Numero massimo di messaggi visualizzabili sul sito, se impostato a 0 non mostrerà la piazzetta"),
    ConfigOption("sending_interval",           "SITE",        5,         False, True,   "getint",     "set", "Secondi di attesa tra un send di nota, messaggio, post ed un altro"),
    ConfigOption("text_color",                 "SITE",        "silver",  False, True,   "get",        "set", "Serve ad evitare di inviare codici di colore laddove non serve"),

    ConfigOption("game_name",                  "SERVER",      "Mud",     False, True,   "get",        "set", "Nome del gioco"),
    ConfigOption("server_name",                "SERVER",      "Server",  False, True,   "get",        "set", "Nome del server che ospita il gioco"),
    ConfigOption("engine_name",                "SERVER",      "Engine",  False, True,   "get",        "set", "Nome del motore del gioco"),
    ConfigOption("engine_version",             "SERVER",      "0.0",     False, True,   "get",        "set", "Versione del motore del gioco"),
    ConfigOption("staff_name",                 "SERVER",      "Staff",   False, True,   "get",        "set", "Nome dello staff del gioco"),
    ConfigOption("motto",                      "SERVER",      "Huzza!",  False, True,   "get",        "set", "Motto o frase d'effetto per il gioco"),
    ConfigOption("news_to_show",               "SERVER",      5,         False, True,   "getint",     "set", "Numero di novità da visualizzare nella homepage e quantità inviata ad ogni richiesta di visualizzazione delle novità più vecchie"),
    ConfigOption("allow_player_gaming",        "SERVER",      True,      False, True,   "getboolean", "set", "Indica se è permesso far entrare i giocatori nel gioco"),
    ConfigOption("save_persistence",           "SERVER",      True,      False, True,   "getboolean", "set", "Salva i dati che servono per mantenere la persistenza del mondo del Mud"),
    ConfigOption("compression_mode",           "SERVER",      "bz2",     False, True,   "get",        "set", "Tipologia di archiviazione dei backup creati da aarit"),
    ConfigOption("max_output_buffer",          "SERVER",      128000,    False, True,   "getint",     "set", "Indica il limite massimo in Kb di buffer di output da inviare al giocatore, una volta sforato tale limite la connessione al client viene chiusa (valori tra 64000 a 128000)"),
    ConfigOption("max_execution_time",         "SERVER",      0.04,      False, True,   "getfloat",   "set", "Indica il tempo massimo in secondi dell'esecuzione di un comando (al di là del quale le deferred automatiche di group_entities nel metodo split_entity potrebbero fare più danno di quanto non ne facciano normalmente)"),

    ConfigOption("mail_on_enter_in_game",      "MAIL",        True,      False, True,   "getboolean", "set", "Avvisa se qualche giocatore non admin entra in gioco"),
    ConfigOption("email",                      "MAIL",        "?@?.?",   False, True,   "getemail",   "set", "Indirizzo a cui vengono inviate le mail da parte dei giocatori"),
    ConfigOption("smtp_host",                  "MAIL",        "smpt.?",  False, True,   "get",        "set", "SMTP con cui inviare le mail"),
    ConfigOption("smtp_email",                 "MAIL",        "?@?.?",   False, True,   "getemail",   "set", "Email utilizzata per l'invio delle mail"),

    ConfigOption("min_len_name",               "GAME",        3,         False, True,   "getint",     "set", "Lunghezza minima per un nome di account o di personaggio"),
    ConfigOption("max_len_name",               "GAME",        14,        False, True,   "getint",     "set", "Lunghezza massima per un nome di account o di personaggio"),
    ConfigOption("min_len_password",           "GAME",        6,         False, True,   "getint",     "set", "Lunghezza minima per una password"),
    ConfigOption("max_len_password",           "GAME",        24,        False, True,   "getint",     "set", "Lunghezza massima per la password"),
    ConfigOption("max_aliases",                "GAME",        100,       False, True,   "getint",     "set", "Numero massimo di alias creati per personaggio"),
    ConfigOption("max_macros",                 "GAME",        100,       False, True,   "getint",     "set", "Numero massimo di macro creati per personaggio"),
    ConfigOption("max_account_players",        "GAME",        30,        False, True,   "getint",     "set", "Numero massimo di personaggi creabili in un account"),  # (TD) da togliere la limitazione grazie al sistema dell'immaginetta di conferma del codice
    ConfigOption("max_account_bugs",           "GAME",        1000,      False, True,   "getint",     "set", "Numero massimo di bachi segnalabili"),
    ConfigOption("max_account_comments",       "GAME",        1000,      False, True,   "getint",     "set", "Numero massimo di commenti segnalabili"),
    ConfigOption("max_account_typos",          "GAME",        1000,      False, True,   "getint",     "set", "Numero massimo di typo segnalabili"),
    ConfigOption("max_account_ideas",          "GAME",        1000,      False, True,   "getint",     "set", "Numero massimo di idee segnalabili"),
    ConfigOption("max_level",                  "GAME",        200,       False, True,   "getint",     "set", "Livello massimo consentito dal gioco"),
    ConfigOption("max_stat_value",             "GAME",        100,       False, True,   "getint",     "set", "Valore massimo per gli attributi come forza, velocità, etc"),
    ConfigOption("max_skill_value",            "GAME",        100,       False, True,   "getint",     "set", "Valore massimo imparabile per le skill"),
    ConfigOption("clumsy_value",               "GAME",        -100,      False, True,   "getint",     "set", "Valore limite prima di considerare un lancio di dadi per una skill maldestra"),
    ConfigOption("failure_value",              "GAME",        50,        False, True,   "getint",     "set", "Valore limite prima di considerare un lancio di dadi per una skill fallito"),
    ConfigOption("success_value",              "GAME",        200,       False, True,   "getint",     "set", "Valore limite prima di considerare un lancio di dadi per una skill un successo"),
    ConfigOption("masterly_value",             "GAME",        250,       False, True,   "getint",     "set", "Valore limite prima di considerare un lancio di dadi per una skill un magistrale"),
    ConfigOption("starting_points",            "GAME",        100,       False, True,   "getint",     "set", "Valore iniziale utilizzato in vari modi dei punti vita, mana e vigore"),
    ConfigOption("starting_attrs",             "GAME",        30,        False, True,   "getint",     "set", "Valore iniziale utilizzato per gli attributi"),
    ConfigOption("min_repop_time",             "GAME",        0,         False, True,   "getint",     "set", "Minuti di tempo minimo impostabili per un reset di area"),
    ConfigOption("max_repop_time",             "GAME",        1440,      False, True,   "getint",     "set", "Minuti di tempo massimo impostabili per un reset di area"),
    ConfigOption("max_idle_seconds",           "GAME",        900,       False, True,   "getint",     "set", "Secondi di inattività massima prima che il mud esegua una sconnessione forzata"),
    ConfigOption("chars_for_smile",            "GAME",        8,         False, True,   "getint",     "set", "Numero di caratteri controllati alla fine di una frase detta in cui viene cercato uno smile"),
    ConfigOption("gift_on_enter",              "GAME",        None,      True,  True,   "get",        "set", "Entità da regalare ai giocatori che non l'hanno ancora, ogni volta che entrano, l'opzione è facoltativa"),
    ConfigOption("initial_destination",        "GAME",        None,      False, True,   "get",        "set", "Destinazione per i pg che entrano nel gioco"),
    ConfigOption("min_secret_arg_len",         "GAME",        2,         False, True,   "getint",     "set", "Numero minimo da digitare"),
    ConfigOption("max_behaviour_probability",  "GAME",        300,       False, True,   "getint",     "set", "Probabilità massima impostabile nelle etichette di behaviour"),  # (TD) toglierla e farla a 100% fisso e non al 300% come ora
    ConfigOption("purification_rpg_hours",     "GAME",        24,        False, True,   "getint",     "set", "Ore rpg prima che un'entità prescelta per la purificazione venga estratta"),
    ConfigOption("leveling_restore_points",    "GAME",        False,     False, True,   "getboolean", "set", "Se impostato a vero indica che ad ogni livello nuovo guadagnato da un giocatore i punteggi di vita, mana e vigore vengono recuperati totalmente"),
    ConfigOption("use_visual_grouping",        "GAME",        True,      False, True,   "getboolean", "set", "Se impostato a vero indica che gli oggetti verranno ammucchiati visivamente a seconda che la loro long sia uguale o meno"),
    ConfigOption("use_physical_grouping",      "GAME",        True,      False, True,   "getboolean", "set", "Se impostato a vero indica che gli oggetti verranno ammucchiati fisicamente a seconda che siano tra di loro equivalenti"),
    ConfigOption("currency_jump",              "GAME",        1,         False, True,   "getint",     "set", "Indica di quante decine le 4 valute rame, argento, oro e mithril si differenziano una dall'altra: 1, 10, 100 o 1000"),
    ConfigOption("persistent_act_seconds",     "GAME",        2,         False, True,   "getint",     "set", "Indica quanti secondi durano i messaggi della persistenza dell'azione, cioè i messaggi di act utilizzati come long, valori validi tra 4 e 1"),
    ConfigOption("running_step_time",          "GAME",        1.0,       False, True,   "getfloat",   "set", "Indica i secondi o i centesimi di secondo minimi tra un comando di movimento ed un altro per considerarlo come corsa, valori validi tra 2.0 e 0.1"),
    ConfigOption("dam_plr_vs_plr",             "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra giocatori contro giocatori"),
    ConfigOption("dam_plr_vs_mob",             "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra giocatori contro mob"),
    ConfigOption("dam_plr_vs_item",            "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra giocatori contro oggetti"),
    ConfigOption("dam_mob_vs_plr",             "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra mob contro giocatori"),
    ConfigOption("dam_mob_vs_mob",             "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra mob contro mob"),
    ConfigOption("dam_mob_vs_item",            "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra mob contro item"),
    ConfigOption("dam_item_vs_plr",            "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra item contro giocatori"),
    ConfigOption("dam_item_vs_mob",            "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra item contro mob"),
    ConfigOption("dam_item_vs_item",           "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del danno inferto tra item contro item"),
    ConfigOption("exp_modifier",               "GAME",        100,       False, True,   "getint",     "set", "Indica il modificatore in percentuale del guadagno dei punti di esperienza"),
    
    ConfigOption("seconds_in_minute",          "TIME",        2,         False, True,   "getint",     "set", "Numero di secondi reali che formano un minuto rpg"),
    ConfigOption("minutes_in_hour",            "TIME",        60,        False, True,   "getint",     "set", "Numero di minuti rpg in un'ora rpg"),
    ConfigOption("hours_in_day",               "TIME",        24,        False, True,   "getint",     "set", "Numero delle ore rpg in un giorno rpg"),
    ConfigOption("days_in_month",              "TIME",        30,        False, True,   "getint",     "set", "Numero dei giorni rpg in un mese rpg"),
    ConfigOption("months_in_year",             "TIME",        10,        False, True,   "getint",     "set", "Numero dei mesi rpg in un anno rpg"),
    ConfigOption("dawn_hour",                  "TIME",        5,         False, True,   "getint",     "set", "Ora dell'aurora"),
    ConfigOption("sunrise_hour",               "TIME",        6,         False, True,   "getint",     "set", "Ora dell'alba"),
    ConfigOption("noon_hour",                  "TIME",        12,        False, True,   "getint",     "set", "Ora del mezzogiorno"),
    ConfigOption("sunset_hour",                "TIME",        18,        False, True,   "getint",     "set", "Ora del tramonto"),
    ConfigOption("dusk_hour",                  "TIME",        19,        False, True,   "getint",     "set", "Ora del crepuscolo"),
    ConfigOption("midnight_hour",              "TIME",        0,         False, True,   "getint",     "set", "Ora relativa alla mezzanotte"),
    ConfigOption("aggressiveness_loop_seconds","TIME",        1,         False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo all'invio di messaggi di minaccia (impostabile da 0.1 a 10)"),
    ConfigOption("blob_loop_seconds",          "TIME",        1,         False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo la dinamica dei fluidi (impostabile da 0.1 a 10)"),
    ConfigOption("decomposer_loop_seconds",    "TIME",        120,       False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo alla decomposizione dei cadaveri (impostabile da 12 a 1200)"),
    ConfigOption("digestion_loop_seconds",     "TIME",        60,        False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo alla digestione di cibo ingerito (impostabile da 6 a 600)"),
    ConfigOption("fight_loop_seconds",         "TIME",        0.1,       False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo al combattimento (impostabile da 0.01 a 1)"),
    ConfigOption("game_loop_seconds",          "TIME",        1,         False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo al gioco (impostabile da 0.1 a 10)"),
    ConfigOption("maintenance_loop_seconds",   "TIME",        60,        False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo alla manutenzione (impostabile da 0.1 a 10)"),
    ConfigOption("room_behaviour_loop_seconds","TIME",        1,         False, True,   "getfloat",   "set", "Tempo in secondi del ciclo relativo ai behaviour delle stanze (impostabile da 0.1 a 10)"),

    ConfigOption("log_accents",                "LOG",         True,      False, True,   "getboolean", "set", "Logga gli accenti senza convertirli nei, volgarmente chiamati, 'accenti apostrofati'"),
    ConfigOption("log_player_output",          "LOG",         False,     False, True,   "getboolean", "set", "Esegue un log, per ogni personaggio, di tutto l'output inviato relativo alla pagina del gioco"),
    ConfigOption("print_entity_inputs",        "LOG",         False,     False, True,   "getboolean", "set", "Esegue il print su console degli input inviati dagli oggetti e dai mob"),
    ConfigOption("track_behaviours",           "LOG",         True,      False, True,   "getboolean", "set", "Attiva o meno il sistema di tracking delle esecuzioni dei behaviour"),
    ConfigOption("track_triggers",             "LOG",         True,      False, True,   "getboolean", "set", "Attiva o meno il sistema di tracking delle esecuzioni dei trigger"),

    ConfigOption("reload_web_pages",           "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Ricompila i controller delle pagina web ad ogni loro richiesta, utile per modifiche on the fly senza riavviare il server"),
    ConfigOption("reload_commands",            "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Ricompila il modulo del comando ad ogni sua chiamata, utile per modifiche on the fly senza riavviare il server"),
    ConfigOption("reload_gamescripts",         "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Ricompila i gamescript, utile se si stanno modificando per test o debug"),
    ConfigOption("use_subsequent_resets",      "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Abilita i reset successivi al primo, a volte può essere utile disatibilitarli per test"),
    ConfigOption("use_behaviours",             "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Abilita o disabilita tutti i behaviour"),
    ConfigOption("use_gamescripts",            "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Abilita o disabilita tutti i mudscripts"),
    ConfigOption("use_profiler",               "DEVELOPMENT", False,     False, True,   "getboolean", "set", "Attiva il sistema di profiling per analizzare i colli di bottiglia nel codice"),
    ConfigOption("check_references",           "DEVELOPMENT", False,     False, True,   "getboolean", "set", "Attiva o meno un sistema di controllo dei riferimenti di tutte le persistenze"),
    ConfigOption("delete_pyc_files",           "DEVELOPMENT", True,      False, True,   "getboolean", "set", "Cancella tutti i file py compilati alla chiusura del gioco per maggiore pulizia, soprattutto tra i file dat"),
    ConfigOption("time_warp",                  "DEVELOPMENT", False,     False, True,   "getboolean", "set", "Se attivata tutte le deferred scatterrano dopo un secondo invece di attendere il loro naturale decorso di tempi, anche alcuni loop scattaranno il prima possibile (dipende dal loop, alcuni dopo un secondo altri dopo un minuto), questa opzione è utile per testare praticamente in real-time il normale flusso del codice senza dovre aspettare minuti e minuti"))

SUPPORTED_COMPRESSIONS = ("tar", "gz", "bz2")


#= CLASSI ======================================================================

class Config(ConfigParser.SafeConfigParser):
    """
    Classe la cui variabile singleton è inizializzata a fine modulo.
    """
    ready = False
    filename = ""

    def check_option_names(self):
        try:
            config_file = open(self.filename, "r")
        except IOError:
            log.bug("Impossibile aprire il file %s in lettura" % self.filename)
            return

        for line in config_file:
            if not line.strip():
                continue
            if line[0] == "#":
                continue
            if "=" not in line:
                continue

            name = line.split("=")[0].strip()
            for option in CONFIG_OPTIONS:
                if option.name == name:
                    break
            else:
                log.bug("Non è stata trovata nessuna opzione dal nome %s nel file di configurazione %s" % (name, self.filename))
                continue
    #- Fine Metodo -

    def load(self, filename):
        self.filename = filename
        self.check_option_names()
        ConfigParser.SafeConfigParser.read(self, filename)

        for option in CONFIG_OPTIONS:
            if hasattr(self, option.name):
                log.bug("L'opzione di config %s è già stata impostata precedentemente alla sezione %s" % (option.name, option.section))
                continue

            if not hasattr(self, option.getter):
                log.bug("L'opzione di config %s non possiede il getter %s" % (option.name, option.getter))
                setattr(self, option.name, option.default)
                continue

            getter = getattr(self, option.getter)
            try:
                value = getter(option.section, option.name)
            except ConfigParser.NoOptionError:
                if not option.facultative:
                    log.bug("Opzione %s mancante nel file %s, verrà caricata con il suo valore di default: %s" % (option.name, filename, option.default))
                setattr(self, option.name, option.default)
            else:
                setattr(self, option.name, value)

        self.ready = True
    #- Fine Metodo -

    def save(self):
        for option in reversed(CONFIG_OPTIONS):
            value = getattr(self, option.name)
            if not value and option.getter == "get" and not option.facultative:
                log.bug("valore dell'opzione di config %s non valida e non opzionale: %s" % (option.name, value))

            if not hasattr(self, option.setter):
                log.bug("L'opzione di config %s non possiede il setter %s" % (option.name, option.getter))
                continue

            setter = getattr(self, option.setter)
            setter(option.section, option.name, value)

        try:
            config_file = open(self.filename, "w")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura" % self.filename)
            return

        ConfigParser.SafeConfigParser.write(self, config_file)
        config_file.close()
    #- Fine Metodo -

    def finalize(self):
        # Converte la stringa ricavata per la prima destinazione in
        # oggetto-destinazione vero e proprio
        from room import Destination
        destination = Destination()
        destination.fread_the_line(None, self.initial_destination, "self.initial_destination")
        from src.database import database
        if destination.area in database["areas"]:
            destination.area = database["areas"][destination.area]
        else:
            log.bug("Codice d'area %s inesistente nel file %s (sarà impossibile per i pg entrare in gioco)" % (
                destination.area, self.filename))
        self.initial_destination = destination

        first_room = self.initial_destination.get_room()
        if not first_room:
            log.bug("initial_destination impostata nel file %s non punta ad una stanza valida: %r (first_room: %r)" % (
                self.filename, self.initial_destination, first_room))
            sys.exit(1)
            return

        # ---------------------------------------------------------------------

        # Recupera il riferimento dell'eventuale dono da inserire in gioco
        if self.gift_on_enter == "None":
            self.gift_on_enter = None
        elif self.gift_on_enter:
            if "_item_" in self.gift_on_enter:
                table_name = "proto_items"
            else:
                table_name = "proto_mobs"

            if self.gift_on_enter in database[table_name]:
                self.gift_on_enter = database[table_name][self.gift_on_enter]
            else:
                log.bug("Non è stata trovata nessuna entità di prototipo con codice %s nel database %s" % (
                    self.gift_on_enter, table_name))
    #- Fine Metodo -

    def iter_all_error_messages(self):
        msgs = []

        if not self.game_name:
            yield "game_name è vuoto"
        if self.game_name and not check_colors(self.game_name):
            yield "game_name contiene dei stili errati: %s" % self.game_name
        if not self.site_address:
            yield "site_address è vuoto"
        if self.site_address and not self.site_address.startswith("http://"):
            yield "site_address non inizia con 'http://'"
        if self.site_address and not self.site_address[-1].isalnum():
            yield "site_address non finisce con un numero o con una stringa, dev'essere valido per poterci eventualmente concatenare la porta: %r" % self.site_address
        if self.http_port < 1 or self.http_port > 65535:
            yield "http_port è un valore errato: %d" % self.http_port
        if not self.text_color:
            yield "text_color non è valido: %r" % self.text_color
        if self.text_color and not self.text_color.lower():
            yield "text_color non ha tutti i caratteri minuscoli: %s" % self.text_color
        if self.text_color and not self.text_color in colors:
            yield "text_color non si trova tra i nomi dei colori: %s" % self.text_color
        if not self.email:
            yield "email mancante per poter inviare mail tramite l'smtp: %r" % self.email
        if not self.smtp_email:
            yield "smtp_email mancante per poter inviare mail tramite l'smtp: %r" % self.smtp_email
        if not self.smtp_host:
            yield "smtp_host non è un valore valido: %r" % self.smtp_host
        if self.min_len_name < 2:
            yield "min_len_name è minore di 2: %d" % self.min_len_name
        if self.max_len_name < 3:
            yield "max_len_name è minore di 3: %d" % self.max_len_name
        if self.min_len_name >= self.max_len_name:
            yield "min_len_name %d supera quella di max_len_name %d" % (self.min_len_name, self.max_len_name)
        if self.min_len_password < 5:
            yield "min_len_password è minore di 5: %d" % self.min_len_password
        if self.max_len_password < 5:
            yield "max_len_password è minore di 5: %d" % self.max_len_password
        if self.min_len_password >= self.max_len_password:
            yield "min_len_password %d supera quella di max_len_password %d" % (self.min_len_password, self.max_len_password)
        if self.max_aliases < 0:
            yield "max_aliases non può essere negativo: %d" % self.max_aliases
        if self.max_macros < 0:
            yield "max_macros non può essere negativo: %d" % self.max_macros
        if self.max_account_players <= 0:
            yield "max_account_players non può essere negativo: %d" % self.max_account_players
        if self.max_account_bugs < 0:
            yield "max_account_bugs non può essere negativo: %d" % self.max_account_bugs
        if self.max_account_typos < 0:
            yield "max_account_typos non può essere negativo: %d" % self.max_account_typos
        if self.max_account_ideas < 0:
            yield "max_account_ideas non può essere negativo: %d" % self.max_account_ideas
        if self.sending_interval < 1 or self.sending_interval > 60:
            yield "sending_interval è un valore troppo basso o troppo alto: %d" % self.sending_interval
        if self.max_level < 50 or self.max_level > 1000:
            yield "max_level non è un valore valido: %d (meglio che rimanga tra 50 e 1000)" % self.max_level
        if self.max_stat_value < 50 or self.max_stat_value > 200:
            yield "max_stat_value non è un valore valido: %d (meglio che rimanga tra 50 e 200)" % self.max_stat_value
        if self.max_skill_value < 50 or self.max_skill_value > 200:
            yield "max_skill_value non è un valore valido: %d (meglio che rimanga tra 50 e 200)" % self.max_skill_value
        if self.clumsy_value < -300 or self.clumsy_value > 300:
            yield "clumsy_value non è un valore valido: %d (meglio che rimanga tra -300 e 300)" % self.clumsy_value
        if self.failure_value < -300 or self.failure_value > 300:
            yield "failure_value non è un valore valido: %d (meglio che rimanga tra -300 e 300)" % self.failure_value
        if self.success_value < -300 or self.success_value > 300:
            yield "success_value non è un valore valido: %d (meglio che rimanga tra -300 e 300)" % self.success_value
        if self.masterly_value < -300 or self.masterly_value > 300:
            yield "masterly_value non è un valore valido: %d (meglio che rimanga tra -300 e 300)" % self.masterly_value
        if self.starting_points < 10 or self.starting_points > 1000:
            yield "starting_points non è valido: %d (meglio che rimanga tra 10 e 1000)" % self.starting_points
        if self.starting_attrs < 20 or self.starting_attrs > 50:
            yield "starting_attrs non è valido: %d (meglio che rimanga tra 20 e 50)" % self.starting_attrs
        if self.min_repop_time < 0:
            yield "min_repop_time è un valore minore di zero: %d" % self.min_repop_time
        if self.max_repop_time < 0 or self.max_repop_time < self.min_repop_time:
            yield "max_repop_time è un valore minore di zero o minore di min_repop_time: %d" % self.max_repop_time
        if self.max_idle_seconds < 60 * 5 or self.max_idle_seconds > 60 * 60:
            yield "max_idle_seconds non è un valore tra 5 minuti e un'ora: %d" % self.max_idle_seconds
        if self.chars_for_smile < 0:
            yield "chars_for_smile non può essere negativo: %d" % self.chars_for_smile
        if self.initial_destination.get_error_message() != "":
            yield self.initial_destination.get_error_message()
        if not self.compression_mode in SUPPORTED_COMPRESSIONS:
            yield "compression_mode è errata: %r" % self.compression_mode
        if not self.motto:
            yield "motto è un valore non valido: %r" % self.motto
        if not self.staff_name:
            yield "staff_name è un valore non valido: %r" % self.staff_name
        if not self.engine_name:
            yield "engine_name è un valore non valido: %r" % self.engine_name
        if not self.engine_version:
            yield "engine_version è un valore non valido: %r" % self.engine_version
        if not self.server_name:
            yield "server_name è un valore non valido: %r" % self.server_name
        if self.news_to_show < 5 or self.news_to_show > 100:
            yield "news_to_show dev'essere tra 5 e 100: %d" % self.news_to_show
        if self.max_google_translate < 100:
            yield "max_google_translate non è una quantità di caratteri valida: %d" % self.max_google_translate
        if self.max_square_msg_len < 32:
            yield "max_square_msg_len non è una quantità di caratteri valida: %d" % self.max_square_msg_len
        if self.max_square_messages < 10:
            yield "max_square_messages non è una quantità di caratteri valida: %d" % self.max_square_messages
        if self.max_feedback_len < 64:
            yield "max_feedback_len non è una quantità di caratteri valida: %d" % self.max_feedback_len
        if self.min_secret_arg_len not in (1, 2, 3):
            yield "min_secret_arg_len dev'essere tra 1 e 3 compresi: %d" % self.min_secret_arg_len
        if self.max_behaviour_probability < 0 or self.max_behaviour_probability > 1000:
            yield "max_behaviour_probability dev'essere un numero tra 0 e 1000 compresi: %d" % self.max_behaviour_probability
        if self.purification_rpg_hours < 0 or self.purification_rpg_hours > 720:
            yield "purification_rpg_hours dev'essere un numero tra 0 e 720 compresi: %d" % self.purification_rpg_hours
        if self.currency_jump not in (1, 10, 100, 1000):
            yield "currency_jump dev'essere una decina tra 1 e 1000 compresi: %d" % self.currency_jump
        if self.persistent_act_seconds < 1 or self.persistent_act_seconds > 4:
            yield "persistent_act_seconds dev'essere tra 1 e 4 compresi: %d" % self.persistent_act_seconds
        if self.running_step_time < 0.1 or self.running_step_time > 2.0:
            yield "running_step_time dev'essere tra 0.1 e 2.0 compresi: %f" % self.running_step_time
        if self.dam_plr_vs_plr < 10 or self.dam_plr_vs_plr > 1000:
            yield "dam_plr_vs_plr dev'essere tra 10 e 1000 compresi: %d" % self.dam_plr_vs_plr
        if self.dam_plr_vs_mob < 10 or self.dam_plr_vs_mob > 1000:
            yield "dam_plr_vs_mob dev'essere tra 10 e 1000 compresi: %d" % self.dam_plr_vs_mob
        if self.dam_plr_vs_item < 10 or self.dam_plr_vs_item > 1000:
            yield "dam_plr_vs_item dev'essere tra 10 e 1000 compresi: %d" % self.dam_plr_vs_item
        if self.dam_mob_vs_plr < 10 or self.dam_mob_vs_plr > 1000:
            yield "dam_mob_vs_plr dev'essere tra 10 e 1000 compresi: %d" % self.dam_mob_vs_plr
        if self.dam_mob_vs_mob < 10 or self.dam_mob_vs_mob > 1000:
            yield "dam_mob_vs_mob dev'essere tra 10 e 1000 compresi: %d" % self.dam_mob_vs_mob
        if self.dam_mob_vs_item < 10 or self.dam_mob_vs_item > 1000:
            yield "dam_mob_vs_item dev'essere tra 10 e 1000 compresi: %d" % self.dam_mob_vs_item
        if self.dam_item_vs_plr < 10 or self.dam_item_vs_plr > 1000:
            yield "dam_item_vs_plr dev'essere tra 10 e 1000 compresi: %d" % self.dam_item_vs_plr
        if self.dam_item_vs_mob < 10 or self.dam_item_vs_mob > 1000:
            yield "dam_item_vs_mob dev'essere tra 10 e 1000 compresi: %d" % self.dam_item_vs_mob
        if self.dam_item_vs_item < 10 or self.dam_item_vs_item > 1000:
            yield "dam_item_vs_item dev'essere tra 10 e 1000 compresi: %d" % self.dam_item_vs_item
        if self.exp_modifier < 10 or self.exp_modifier > 1000:
            yield "exp_modifier dev'essere tra 10 e 1000 compresi: %d" % self.exp_modifier
        if self.max_output_buffer < 64000 or self.max_output_buffer > 256000:
            yield "max_output_buffer dev'essere tra 64000 e 128000: %d" % self.max_output_buffer
        if self.max_execution_time < 0.001 or self.max_execution_time > 0.5:
            yield "max_execution_time dev'essere tra 0.001 e 0.5: %d" % self.max_execution_time
        if self.seconds_in_minute < 1:
            yield "seconds_in_minute non può essere minore di 1: %d" % self.seconds_in_minute
        if self.minutes_in_hour < 1:
            yield "minutes_in_hour non può essere minore di 1: %d" % self.minutes_in_hour
        if self.hours_in_day < 1:
            yield "hours_in_day non può essere minore di 1: %d" % self.hours_in_day
        if self.days_in_month < 1:
            yield "days_in_month non può essere minore di 1: %d" % self.days_in_month
        if self.months_in_year < 1:
            yield "months_in_year non può essere minore di 1: %d" % self.months_in_year
        if self.dawn_hour < 0 or self.dawn_hour > self.hours_in_day - 1:
            yield "dawn_hour è errata: %d (dev'essere tra 0 e %d)" % (self.dawn_hour, self.hours_in_day - 1)
        if self.sunrise_hour < 0 or self.sunrise_hour > self.hours_in_day - 1:
            yield "sunrise_hour è errata: %d (dev'essere tra 0 e %d)" % (self.sunrise_hour, self.hours_in_day - 1)
        if self.noon_hour < 0 or self.noon_hour > self.hours_in_day - 1:
            yield "noon_hour è errata: %d (dev'essere tra 0 e %d)" % (self.noon_hour, self.hours_in_day - 1)
        if self.sunset_hour < 0 or self.sunset_hour > self.hours_in_day - 1:
            yield "sunset_hour è errata: %d (dev'essere tra 0 e %d)" % (self.sunset_hour, self.hours_in_day - 1)
        if self.dusk_hour < 0 or self.dusk_hour > self.hours_in_day - 1:
            yield "dusk_hour è errata: %d (dev'essere tra 0 e %d)" % (self.dusk_hour, self.hours_in_day - 1)
        if self.midnight_hour < 0 or self.midnight_hour > self.hours_in_day - 1:
            yield "midnight_hour è errata: %d (dev'essere tra 0 e %d)" % (self.midnight_hour, self.hours_in_day - 1)
        if self.aggressiveness_loop_seconds < 0.1 or self.aggressiveness_loop_seconds > 10:
            yield "aggressiveness_loop_seconds è errata: %d (dev'essere tra 0.1 e 10)" % self.aggressiveness_loop_seconds
        if self.blob_loop_seconds < 0.1 or self.blob_loop_seconds > 10:
            yield "blob_loop_seconds è errata: %d (dev'essere tra 0.1 e 10)" % self.blob_loop_seconds
        if self.decomposer_loop_seconds < 12 or self.decomposer_loop_seconds > 1200:
            yield "decomposer_loop_seconds è errata: %d (dev'essere tra 12 e 1200)" % self.decomposer_loop_seconds
        if self.digestion_loop_seconds < 6 or self.digestion_loop_seconds > 600:
            yield "digestion_loop_seconds è errata: %d (dev'essere tra 6 e 600)" % self.digestion_loop_seconds
        if self.fight_loop_seconds < 0.01 or self.fight_loop_seconds > 1:
            yield "fight_loop_seconds è errata: %d (dev'essere tra 0.01 e 1)" % self.fight_loop_seconds
        if self.game_loop_seconds < 0.1 or self.game_loop_seconds > 10:
            yield "game_loop_seconds è errata: %d (dev'essere tra 0.1 e 10)" % self.game_loop_seconds
        if self.maintenance_loop_seconds < 6 or self.maintenance_loop_seconds > 60:
            yield "maintenance_loop_seconds è errata: %d (dev'essere tra 6 e 60)" % self.maintenance_loop_seconds
        if self.room_behaviour_loop_seconds < 0.1 or self.room_behaviour_loop_seconds > 10:
            yield "room_behaviour_loop_seconds è errata: %d (dev'essere tra 0.1 e 10)" % self.room_behaviour_loop_seconds
    #- Fine Metodo -

    def get_error_message(self):
        messages = list(self.iter_all_error_messages())
        if not messages:
            return ""

        log.bug("(Config: filename %s) %s" % (self.filename, messages[0]))
        return messages[0]
    #- Fine Metodo -

    #- Metodi getter e setter --------------------------------------------------

    def getemail(self, section_name, option_name):
        return ConfigParser.SafeConfigParser.get(self, section_name, option_name)
    #- Fine Metodo -

    def set(self, section_name, option_name, value):
        # Qui anche le opzioni che hanno entità o altri oggetti (gift_on_enter)
        # funzionano senza problemi grazie al metodo __str__
        ConfigParser.SafeConfigParser.set(self, section_name, option_name, str(value))
    #- Fine Metodo -


#= SINGLETON ===================================================================

config = Config()
