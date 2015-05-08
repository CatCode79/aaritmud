# -*- coding: utf-8 -*-

"""
Modulo relativo il motore del gioco di Aarit.
"""


#= IMPORT ======================================================================

import cProfile
import datetime
import optparse
import os
import socket
import sys
import time

from twisted.internet import reactor


#= INSTALL =====================================================================

# Si assicura che il gioco sia avviato con la versione di Python corretta
if hasattr(sys, "version_info"):
    if (2, 7) > sys.version_info >= (3, 0):
        raise RuntimeError("Il gioco ha bisogno della versione di Python tra la 2.7.")

_use_epoll = False
try:
    from twisted.internet import epollreactor
    epollreactor.install()
    _use_epoll = True
    print "Verra' utilizzato l'epoll di Linux, più performante"
except AssertionError:
    print "E' gia' stato trovato installato l'epollreactor di Linux, più' performante"
    _use_epoll = True
except:
    print "Verra' utilizzata la select di default, meno performante"
    print "(normale se stai utilizzando un OS differente da Linux)\n"

try:
    from numpy import random as numpy_random
except ImportError:
    print "La libreria opzionale numpy non è installata, alcune funzioni del modulo"
    print "random risulteranno piu' lente\n"
else:
    print "Verranno utilizzate alcune funzioni random della libreria numpy,"
    print "piu' performanti, al posto di quelle standard\n"
    import random
    random.randint   = numpy_random.random_integers
    random.randrange = numpy_random.randint


#= CLASSI ======================================================================

class OptionParser(object):
    def __init__(self):
        # Legge le opzioni di riga di comando
        self.options = self.parse_options()
        if not self.options:
            print "opzioni parsate da riga di comando errate: %r" % self.options
            sys.exit(1)
    #- Fine Inizializzazione -

    def parse_options(self):
        """
        Processa eventuali opzioni di riga di comandi passate.
        """
        parser = optparse.OptionParser()
        # Attenzione che qui negli help non bisogna inserire caratteri accentati
        parser.add_option("-b", "--boot", action="store_true", dest="boot_only", default=False, help=u"Permette di eseguire un finto boot del gioco per verificare che tutto verra' caricato")
        parser.add_option("-c", "--config", dest="config_filename", default="config.ini", help="Nome di un file di configurazione differente rispetto a quello standard")
        parser.add_option("-i", "--ignore", action="store_true", dest="ignore", default=False, help="Ignora alcuni errori che altrimenti bloccherebbero il caricamento del gioco")
        parser.add_option("-m", "--mode", dest="mode", default="", help="Aiuta a scegliere le opzioni di config per le due modalita' principali di avvio del server: testing o official. Passare all'opzione una di queste due parole per essere guidato nella scelta delle configurazioni se la modalita' si trova in discrepanza con il file config.ini")
        parser.add_option("-s", "--spelling", action="store_true", dest="spelling", default=False, help="Esegue un controllo ortografico basato su dizionario su molte delle stringe dei dati")
        parser.add_option("-p", "--prototype", action="store_true", dest="restart_from_proto", default=False, help="Evita di caricare, se esistenti, i dati di persistenza e ricrea room, mob e oggetti partendo nuovamente dai prototipi")
        parser.add_option("-u", "--umask", dest="umask", default="0", help="Imposta un umask specifico nei sistemi *nix")
        (options, args) = parser.parse_args()

        # Imposta l'eventuale umask passato
        try:
            umask = int(options.umask)
        except ValueError:
            print "Il valore della riga di comando umask e' errato: %s" % options.umask
            sys.exit(1)
        if umask < 0 or umask > 7777:
            print "Il valore della riga di comando umask non e' tra 0 e 7777"
            sys.exit(1)
        if umask != 0:
            os.umask(umask)
            print "umask dei permessi impostata a %s" % umask

        return options
    #- Fine Metodo -

    def check_the_mode(self):
        from src.config import config

        if self.options.mode == "":
            return

        if self.options.mode == "official":
            if config.reload_web_pages:
                self.wait_for_the_answer("reload_web_pages", "Ricaricando le pagine da zero ad ogni richiesta rallenterai il gioco.")
            if not config.allow_web_robots:
                self.wait_for_the_answer("allow_web_robots", "I robot dei motori di ricerca NON indicizzeranno le pagine!")
            if not config.google_analytics_ua:
                self.wait_for_the_answer("google_analytics_ua", "Google Analytics non potrà analizzare l'accesso alle pagine!")
            if config.use_profiler:
                self.wait_for_the_answer("use_profiler", "Utilizzare il profiler rallenta di molto l'esecuzione del gioco.")
            if config.reload_gamescripts:
                self.wait_for_the_answer("reload_gamescripts", "Ricaricare ad ogni esecuzione i gamescript rallenta il gioco.")
            if config.reload_commands:
                self.wait_for_the_answer("reload_commands", "Ricaricare ad ogni esecuzione i comandi rallenta il gioco.")
            if config.time_warp:
                self.wait_for_the_answer("time_warp", "Le deferred scatteranno senza attendere il loro naturale decorso.")
            if not config.use_gamescripts:
                self.wait_for_the_answer("use_gamescripts", "I gamescript non si attiveranno.")
            if not config.use_behaviours:
                self.wait_for_the_answer("use_behaviours", "I behaviour non si attiveranno.")
            if not config.use_subsequent_resets:
                self.wait_for_the_answer("use_subsequent_resets", "I reset temporali non si attiveranno.")
            if config.check_references:
                self.wait_for_the_answer("check_references", "Controllare i riferimenti ad ogni invio di comando rallenta il gioco, è comunque un'opzione da mantenere se non si è sicuri che il codice sia corretto.")
            if config.max_square_messages == 0:
                self.wait_for_the_answer("max_square_messages", "Non verrà mostrata la piazzetta a destra nelle pagine del sito.")
            if config.log_player_output:
                self.wait_for_the_answer("log_player_output", "Verranno loggato tutto l'output dei giocatori su file, ciò rallenterà il gioco.")
            if not config.mail_on_enter_in_game:
                self.wait_for_the_answer("mail_on_enter_in_game", "Non verrà inviata una mail per i personaggi che entreranno nel gioco.")
        elif self.options.mode == "testing":
            if not config.reload_web_pages:
                self.wait_for_the_answer("reload_web_pages", "Non verranno ricarite le pagine web evitando di mostrare eventuali nuove modifiche.")
            if config.allow_web_robots:
                self.wait_for_the_answer("allow_web_robots", "I robot dei motori di ricerca INDICIZZERANNO le pagine! Di solito non è voluto perché potrebbero per errore essere indicizzato il sito di testing.")
            if config.google_analytics_ua:
                self.wait_for_the_answer("google_analytics_ua", "Google Analytics analizzerà l'accesso alle pagine del server di testing aggiungendole a quelle del server officiale. Sicuramente non vuoi ciò.")
            if not config.reload_gamescripts:
                self.wait_for_the_answer("reload_gamescripts", "Non verranno ricaricati ad ogni esecuzione i gamescript, in questa maniera eventuali modifiche agli script richiederanno il riavvio del gioco.")
            if not config.reload_commands:
                self.wait_for_the_answer("reload_commands", "Non verranno ricaricati i comandi ad ogni esecuzione, in questa maniera eventuali modifiche agli script richiederanno il riavvio del gioco..")
            if not config.check_references:
                self.wait_for_the_answer("check_references", "Non verranno controllati i riferimenti, non conviene mantenere tale opzione disattiva, a meno che il server su cui gira il gioco non sia particolarmente lento.")
            if config.mail_on_enter_in_game:
                self.wait_for_the_answer("log_player_output", "Verrà inviata una mail per i personaggi che entreranno nel gioco nonostante questo sia un server di testing.")
        else:
            print "Opzione di avvio mode non valida: %s" % self.options.mode
    #- Fine Metodo -

    def wait_for_the_answer(self, config_option, message):
        from src.config import config

        while 1:
            config_option_value = getattr(config, config_option)
            response = raw_input("%s a %s. %s Vuoi mantenere il valore? S/N > " % (
                config_option, config_option_value, message))
            if response.lower() in ("n", "no"):
                setattr(config, config_option, not config_option_value)
                break
            elif response.lower() in ("s", "sì", "si"):
                break
            else:
                print "Risposta non valida, Sì o No? >"
    #- Fine Metodo -


class Engine(OptionParser):
    """
    Gestisce un'istanza di gioco.
    """
    epoll = _use_epoll

    def __init__(self):
        super(Engine, self).__init__()

        self.booting             = False
        self.shutdown            = False
        self.booting_time        = time.ctime()
        self.shutdown_time       = time.ctime()
        self.boot_seconds        = 0      # Indica quanti secondi sono stati necessari all'avvio del gioco
        self.critical_errors     = 0      # Indica il numero di errori che comprometterebbero il funzionamento del gioco
        self.seconds_to_shutdown = -1     # Indica quanti secondi mancano allo shutdown
        self.automatic_reboot    = False  # Indica se riprovare ad rieseguire un boot alla chiusura causa crash

        self.test_inputs_mode    = False
        self.last_input_sender   = None
        self.last_input_sended   = ""
    #- Fine Inizializzazione -

    def start(self):
        from src.calendar import calendar
        from src.config   import config
        from src.database import database
        from src.log      import log

        starting_time = time.time()
        self.booting = True

        log.platform_infos()

        print "Cancella tutti i file compilati per forzarne la ricompilazione"
        remove_compiled_files()

        try:
            # Dona maggiori informazioni sotto gli OS Linux e simili
            log.booting("Avvio del gioco sul server %s per l'utente %s al gruppo %s" % (socket.gethostname(), os.geteuid(), os.getgid()))
        except:
            log.booting("Avvio del gioco sul server %s" % socket.gethostname())

        log.booting("===========================================================================")
        log.booting("Carica il file di configurazione %s" % self.options.config_filename)
        config.load(self.options.config_filename)
        self.check_the_mode()

        log.booting("Carica la data del calendario gdr")
        calendar.load()

        from src.entity import load_little_words
        log.booting("Carica da file le little words da utilizzare per filtrare le keywords")
        load_little_words()

        from src.account import load_forbidden_names
        log.booting("Carica da file la lista dei nomi proibiti per nuovi account e giocatori")
        load_forbidden_names()

        log.booting("Carica tutti gli input nelle differenti lingue")
        from src.database import fread_list
        from src.input import Input
        import src.interpret as interpret_module
        interpret_module.inputs_command_it = fread_list("data/inputs_command_it.list", Input, "inputs_command_it[%d]")
        interpret_module.inputs_command_en = fread_list("data/inputs_command_en.list", Input, "inputs_command_en[%d]")
        interpret_module.inputs_skill_it   = fread_list("data/inputs_skill_it.list",   Input, "inputs_skill_it[%d]")
        interpret_module.inputs_skill_en   = fread_list("data/inputs_skill_en.list",   Input, "inputs_skill_en[%d]")
        interpret_module.inputs_social_it  = fread_list("data/inputs_social_it.list",  Input, "inputs_social_it[%d]")
        interpret_module.inputs_social_en  = fread_list("data/inputs_social_en.list",  Input, "inputs_social_en[%d]")

        # (TD) per ora inutilizzato
        #from grammar import vocabulary, EntryWord
        #log.booting("Caricamento del vocabolario grammaticale")
        #vocabulary = fread_list("data/vocabulary.list", EntryWord, "vocabulary[%d]")

        from src.database import database
        log.booting("Carica il Database:")
        database.load(use_spelling=self.options.spelling)

        from src.gamescript import create_init_files
        log.booting("Si assicura dell'esistenza dei file __init__ per importare i gamescript")
        create_init_files("data", ("proto_rooms", "proto_mobs", "proto_items"))
        create_init_files("persistence", ("rooms", "mobs", "items", "players"))

        from src.gamescript import import_all_proto_gamescripts
        log.booting("Aggiunge i riferimenti ai gamescript dei dati prototipo")
        import_all_proto_gamescripts("data", ("proto_rooms", "proto_mobs", "proto_items"))

        from src.gamescript import import_all_instance_gamescripts
        log.booting("Aggiunge i riferimenti ai gamescript dei dati delle istanze")
        import_all_instance_gamescripts("persistence", ("rooms", "mobs", "items"))
        import_all_instance_gamescripts("data", ("players", ))

        from src.gamescript import import_all_area_gamescripts
        log.booting("Aggiunge i riferimenti ai gamescript delle aree")
        import_all_area_gamescripts()

        from src.games.wumpus import import_all_wumpus_gamescripts
        log.booting("Aggiunge i riferimenti ai gamescript delle aree wumpus")
        import_all_wumpus_gamescripts()

        from src.site import site
        log.booting("Prepara il web server del gioco")
        reactor.listenTCP(config.http_port, site)

        from src.forum_db import forum_db
        log.booting("Carica il Forum")
        forum_db.load()

        # (TD) molto in futuro saranno più di una
        from src.wild import load_wild
        log.booting("Carica le informazioni sulla Wild")
        #load_wild()

        from src.element import create_elements_list_page
        log.booting("Crea dinamicamente la pagina web della lista degli elementi")
        create_elements_list_page()

        from src.fight import create_damages_page
        log.booting("Crea dinamicamente la pagina web della lista dei danni")
        create_damages_page()

        from src.reset import finalize_room_resets
        log.booting("Inizializza eventuali valori impliciti nella date dei reset.")
        finalize_room_resets()

        from src.reset import start_repop_laters
        log.booting("Prepara le informazioni di repop per tutti i dati caricati dalla persistenza")
        start_repop_laters()

        from src.reset import defer_all_reset_events
        log.booting("Prepara le aree in gioco eseguendo i primi reset.")
        defer_all_reset_events()

        from src.entitypes.plant import restart_all_planting
        log.booting("Rinizia da capo eventuali stadi di crescita lasciati a metà dal precedente shutdown.")
        restart_all_planting()

        from src.loops.aggressiveness import aggressiveness_loop
        from src.loops.blob           import blob_loop
        from src.entitypes.corpse     import decomposer_loop
        from src.loops.digestion      import digestion_loop
        from src.fight                import fight_loop
        from src.game                 import game_loop
        from src.maintenance          import maintenance_loop
        from src.behaviour            import room_behaviour_loop
        log.booting("Avvia tutti i loop")
        aggressiveness_loop.start()
        blob_loop.start()
        decomposer_loop.start()
        digestion_loop.start()
        fight_loop.start()
        game_loop.start()
        maintenance_loop.start()
        room_behaviour_loop.start()

        from src.gamescript import triggering_on_booting
        log.booting("Attivazione dei trigger on_booting")
        triggering_on_booting()

        log.booting("Finalizza e controlla la configurazione caricata precedentemente.")
        config.finalize()
        config.get_error_message()

        log.booting("Esegue un controllo al nome dei metodi della singleton log.")
        log.check_log_methods()

        # Se sono stati trovati degli errori sui riferimenti, controllati dal
        # metodo _search_the_reference o altri tipo di errori pesanti o
        # bloccanti, allora blocca il boot del gioco, a meno che non sia stato
        # avviato ignorando esplicitamente tale cosa
        if self.critical_errors > 0:
            if self.critical_errors > 1:
                message = "Sono stati riscontrati %d errori critici" % self.critical_errors
            elif self.critical_errors == 1:
                message = "E' stato riscontrato 1 errore critico"
            log.booting("===>> %s al caricamento del Gioco (ignora l'eventuale blocco dell'avvio con l'opzione d'avvio -i) <<===" % message)
            if self.options.mode == "official" and not self.options.ignore:
                sys.exit(1)

        log.booting("allow_web_robots=%s: le pagine %sverranno indicizzate dai motori di ricerca" % (
            config.allow_web_robots, "NON " if not config.allow_web_robots else ""))

        self.boot_seconds = time.time() - starting_time
        log.booting("Esecuzione del boot in %d secondi" % self.boot_seconds)

        from src.color import remove_colors
        log.booting("Il gioco %s è pronto alla porta http %d" % (remove_colors(config.game_name), config.http_port))

        if self.options.boot_only:
            print "Esecuzione del solo boot terminata."
            sys.exit(0)

        log.booting("===========================================================================")
        self.booting = False

        try:
            if config.use_profiler:
                log.booting("%s è stato avviato in modalità di profiling" % remove_colors(config.game_name))
                now = datetime.datetime.now()
                cProfile.run("from twisted.internet import reactor; reactor.run()", "profile_%dy_%dm_%dd_%dh_%dm_%ds.results" % (
                    now.year, now.month, now.day, now.hour, now.minute, now.second))
            else:
                reactor.run()
        except (KeyboardInterrupt, SystemExit):
            # Sono eccezioni accettabili e non comportano il reboot automatico
            pass
        except:
            self.automatic_reboot = True
        finally:
            self.stop()
            # Nel qual caso vi sia stato un'eccezione sconosciuta e che il
            # gioco sia quello ufficiale (e quindi è sottinteso che debba
            # sempre rimanere up and running) allora tenta di riavviarlo
            # con le stesse opzioni utilizzate per questa istanza morente
            if self.automatic_reboot and self.options.mode == "official":
                os.system("%s %s" % (sys.executable, " ".join(sys.argv)))
   #- Fine Metodo -

    def stop(self):
        """
        Esegue lo shutdown del gioco.
        """
        from src.log import log

        self.shutdown_time = time.time()
        self.shutdown = True

        from src.config import config
        log.shutdown("Salva tutte le opzioni di configurazione del file %s." % config.filename)
        config.save()

        from src.calendar import calendar
        log.shutdown("Salva la data gdr del gioco.")
        calendar.save()

        log.shutdown("Chiude le connessioni e scollega dal gioco tutti i giocatori.")
        from src.connection import close_all_connections
        close_all_connections()

        from src.game             import game_loop
        from src.maintenance      import maintenance_loop
        from src.behaviour        import room_behaviour_loop
        from src.fight            import fight_loop
        from src.entitypes.corpse import decomposer_loop
        from src.loops.aggressiveness import aggressiveness_loop
        from src.loops.blob           import blob_loop
        from src.loops.digestion      import digestion_loop
        log.shutdown("Ferma tutti i loop.")
        game_loop.stop()
        maintenance_loop.stop()
        room_behaviour_loop.stop()
        fight_loop.stop()
        aggressiveness_loop.stop()
        blob_loop.stop()
        digestion_loop.stop()
        decomposer_loop.stop()

        from src.reset import stop_all_reset_events
        log.shutdown("Mette in pausa i reset di tutte le aree.")
        stop_all_reset_events()

        from src.gamescript import triggering_on_shutdown
        log.shutdown("Attivazione dei trigger on_shutdown")
        triggering_on_shutdown()

        from src.reset import stop_all_repops
        log.shutdown("Ferma tutti i repop in corso")
        stop_all_repops()

        if not self.test_inputs_mode:
            from src.database import database
            log.shutdown("Esegue il backup del contenuto della cartella dei dati")
            database.backup("shutdown_before_save")

            if config.save_persistence:
                log.shutdown("Salva il Database:")
                database.save()

        from src.forum_db import forum_db
        log.shutdown("Salva il Forum")
        forum_db.save()

        if config.track_behaviours:
            from src.behaviour import write_behaviour_tracker
            log.shutdown("Salva le esecuzioni dei behaviour su un file di log")
            write_behaviour_tracker()

        if config.track_triggers:
            from src.gamescript import write_trigger_tracker
            log.shutdown("Salva le esecuzioni dei gamescript su un file di log")
            write_trigger_tracker()

        log.shutdown("Cancella tutti i file compilati per una maggiore pulizia")
        remove_compiled_files()

        log.shutdown("Esecuzione dello shutdown in %d secondi" % (time.time() - self.shutdown_time))
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def remove_compiled_files():
    for root, dirs, files in os.walk(os.getcwd()):
        for name in files:
            ext = os.path.splitext(name)[1]
            if ext in (".pyc", ".pyo"):
                path = os.path.join(root, name)
                try:
                    os.remove(path)
                except OSError:
                    print "Il tentativo di cancellazione del file è fallito: %s" % path
#- Fine Funzione -


#= SINGLETON ===================================================================

engine = Engine()
