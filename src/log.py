# -*- coding: utf-8 -*-

"""
Modulo di gestione generica del log.
"""


#= IMPORT ======================================================================

import datetime
import platform
import os
import sys
import traceback

import Image  # PIL
from twisted._version import version as twisted_version
numpy_version = None
try:
    from numpy.version import version as numpy_version
except ImportError:
    pass


#= CLASSI ======================================================================

class Log(object):
    def __init__(self):
        self.user_agents = []
    #- Fine Inizializzazione -

    def check_log_methods(self):
        """
        Controlla che vi siano tutti i metodi relativi alla numerazione di LOG.
        """
        from src.enums import LOG

        print 
        for element in LOG.elements:
            method_name = element.code.split(".", 1)[1].lower()
            if method_name not in dir(self):
                print "Il metodo %s non esiste nella singleton log mentre invece esiste nell'enumerazione come %r." % (method_name, element)
    #- Fine Inizializzazione -

    # Per evitare ricorsioni ovviamente qui viene utilizzata la print invece
    # della log per mostrare eventuali errori
    def msg(self, message, log_type=None, log_stack=True, write_on_file=True, send_output=True, use_blink=False):
        """
        Invia un messaggio di log contenente errori o avvisi.
        """
        if not message:
            print("[log.bug] message non è un parametro valido: %r" % message)
            return

        # -------------------------------------------------------------------------

        from src.enums import LOG

        # Questa extract_stack è un collo di bottiglia prestazionale del Mud,
        # tuttavia la sua utilità è indubbia e quindi fino a che Aarit non sarà
        # maturissimo è inutile anche evitarla con qualche opzione di config.
        # Ho deciso tuttavia di saltare il print della last_function relativa
        # a tutti i messaggi di log reset, che sono quelli maggiormente inviati
        stack = None
        last_function = ""
        last_function = ""
        if not log_type or log_type.show_last_function:
            stack = traceback.extract_stack()
            last_function = str(stack[-3][2])

        # Stampa il messaggio alla console e lo scrive sul file
        if stack:
            source_name = stack[-3][0].replace(os.getcwd(), "")
            if "src" in source_name:
                position = source_name.find("src")
                source_name = source_name[position : ]
            elif "data" in source_name:
                position = source_name.find("data")
                source_name = source_name[position : ]
            source_line = stack[-3][1]
            last_function = " (%s %s %s)" % (last_function, source_name, source_line)

        # Rimuove i colori dal messaggio per una stampa a video maggiormente amica
        from src.color import remove_colors
        message = remove_colors(message)

        # Invia il messaggio di log agli Admin del Mud
        if send_output:
            from src.database import database
            if "players" in database and log_type.show_on_mud:
                from src.utility import html_escape
                for player in database["players"].itervalues():
                    if not player.game_request:
                        continue
                    if player.trust < log_type.trust and str(log_type.code) not in player.permissions:
                        continue
                    if log_type != LOG.ALWAYS and log_type not in player.account.show_logs and str(log_type.code) not in player.permissions:
                        continue
                    open_span = ""
                    close_span = ""
                    if use_blink:
                        open_span = "<span style='text-decoration: blink;'>"
                        close_span = "</span>"
                    player.send_output("<br>[magenta]%s%s %s%s[close]" % (
                        open_span, last_function.lstrip(), html_escape(message), close_span), avoid_log=True)
                    player.send_prompt()

        # Visto che anche gli altri loop sono legati a questo, non c'è bisogno
        # di controllarle tutti
        from src.loops.aggressiveness import aggressiveness_loop
        from src.loops.blob           import blob_loop
        from src.entitypes.corpse     import decomposer_loop
        from src.loops.digestion      import digestion_loop
        from src.fight                import fight_loop
        from src.game                 import game_loop
        from src.maintenance          import maintenance_loop
        from src.behaviour            import room_behaviour_loop
        if (game_loop and game_loop.running
        and maintenance_loop and maintenance_loop.running
        and room_behaviour_loop and room_behaviour_loop.running
        and fight_loop and fight_loop.running
        and decomposer_loop and decomposer_loop.running
        and aggressiveness_loop and aggressiveness_loop.running
        and blob_loop and blob_loop.running
        and digestion_loop and digestion_loop.running):
            loop_status = "L"
        else:
            loop_status = "l"

        now = datetime.datetime.now()
        message = "%02d:%02d:%02d [%s] {%s}%s: %s" % (
            now.hour,
            now.minute,
            now.second,
            log_type,
            loop_status,
            last_function,
            message)

        log_file = None
        if write_on_file and log_type.write_on_file:
            log_path = "log/%d-%02d-%02d.log" % (now.year, now.month, now.day)
            try:
                log_file = open(log_path, "a")
            except IOError:
                print "Impossibile aprire il file %s in append" % log_path
                log_file = None
            else:
                log_file.write("%s\n" % message)

        # Questo viene fatto perché alcune console purtroppo non supportano
        # i caratteri accentati e simili, viene così convertito l'accento
        # nel famoso e muddoso accento apostrofato, quindi attenzione che
        # in tal caso il messaggio nello stdout è falsato da quello originale
        # nel qual caso si voglia cercarlo nel codice
        if log_type.print_on_console:
            from src.config import config
            if config.ready and config.log_accents:
                if "à" in message:
                    message = message.replace("à", "a'")
                if "è" in message:
                    message = message.replace("è", "e'")
                if "é" in message:
                    message = message.replace("é", "e'")
                if "ì" in message:
                    message = message.replace("ì", "i'")
                if "ò" in message:
                    message = message.replace("ò", "o'")
                if "ù" in message:
                    message = message.replace("ù", "u'")
            print(message)

        # Se la tipologia di log non è un bug allora evita le informazioni di stack
        if log_type != LOG.BUG:
            log_stack = False

        if stack and write_on_file and log_type.write_on_file and log_stack:
            try:
                traceback.print_stack(file=log_file)
                traceback.print_stack(file=sys.stdout)
            except IOError:
                # (TT) non ho capito bene come mai mi fa così, ma semplicemente
                # saltandolo mi evita di fare il traceback, cmq il log avviene
                pass

        if log_file:
            log_file.close()
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def always(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.ALWAYS)
    #- Fine Metodo -

    def booting(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.BOOTING)
    #- Fine Metodo -

    def backup(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.BACKUP)
    #- Fine Metodo -

    def save(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.SAVE)
    #- Fine Metodo -

    def shutdown(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.SHUTDOWN)
    #- Fine Metodo -

    def fread(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.FREAD)
    #- Fine Metodo -

    def fwrite(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.FWRITE)
    #- Fine Metodo -

    def conn(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.CONN)
    #- Fine Metodo -

    def warning(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.WARNING)
    #- Fine Metodo -

    def error(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.ERROR)
    #- Fine Metodo -

    def bug(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.BUG)
    #- Fine Metodo -

    def input(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.INPUT)
    #- Fine Metodo -

    def delete(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.DELETE)
    #- Fine Metodo -

    def badword(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.BARDWORD)
    #- Fine Metodo -

    def offrpg(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.OFFRPG)
    #- Fine Metodo -

    def huh(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.HUH)
    #- Fine Metodo -

    def time(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.TIME)
    #- Fine Metodo -

    def convert(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.CONVERT)
    #- Fine Metodo -

    def command(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.COMMAND)
    #- Fine Metodo -

    def check_reset(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.CHECK_RESET)
    #- Fine Metodo -

    def reset(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.RESET)
    #- Fine Metodo -

    def repop(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.REPOP)
    #- Fine Metodo -

    def gamescript(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.GAMESCRIPT)
    #- Fine Metodo -
   
    def plant(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.PLANT)
    #- Fine Metodo -

    def http(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.HTTP)
    #- Fine Metodo -

    def admin(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.ADMIN)
    #- Fine Metodo -

    def monitor(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.MONITOR)
    #- Fine Metodo -

    def autoreload(self, message, log_stack=True, write_on_file=True, use_blink=False):
        from src.enums import LOG
        self.msg(message, log_stack=log_stack, write_on_file=write_on_file, use_blink=use_blink, log_type=LOG.AUTORELOAD)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def platform_infos(self):
        # (TT) codice clandestino di prova
        #http://www.doughellmann.com/PyMOTW/resource/
        #print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
        #try:
        #    import resource
        #    print "res0", resource.getrusage(0)
        #    print "res1",  resource.getrusage(1)
        #except ImportError:
        #    print "miu mio!"
        #print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

        from src.engine import engine

        lines = []
        dt = datetime.datetime.now()
        lines.append("Platform infos on %d %d %d" % (dt.year, dt.month, dt.day))
        lines.append("Bit Architecture: %s" % str(platform.architecture()))
        lines.append("Machine Type: %s" % platform.machine())
        lines.append("Network Node: %s" % platform.node())
        if platform.processor():
            lines.append("(Real) Processor: %s" % platform.processor())
        lines.append("System Name: %s" % platform.system())
        lines.append("System Version: %s" % platform.version())
        lines.append("System Release: %s" % platform.release())
        if any(platform.dist()):
            lines.append("Linux Distribution: %s" % str(platform.dist()))
        if any(platform.libc_ver()):
            lines.append("Linux Libc Version: %s" % str(platform.libc_ver()))
        lines.append("Python Build: %s" % str(platform.python_build()))
        lines.append("Python Compiler: %s" % platform.python_compiler())
        lines.append("Python Version: %s" % platform.python_version())
        lines.append("Python Executable: %s" % sys.executable)
        lines.append("Twisted Version: %s" % twisted_version.base())
        if engine.epoll:
            lines.append("Reactor: epoll")
        else:
            lines.append("Reactor: select")
        lines.append("PIL Version: %s" % Image.VERSION)
        if numpy_version:
            lines.append("Numpy Version: %s" % numpy_version)
        lines.append("\n")
        lines = "\n".join(lines)

        filename = "log/platform_infos.txt"
        try:
            platform_log_file = open(filename, "a")
            platform_log_file.write(lines + "\n")
            platform_log_file.close()
        except IOError:
            print "Impossibile aprire il file %s in scrittura" % filename

        print lines
    #- Fine Metodo -

    # (TD) da spostare nel modulo channel?
    def chat(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return

        # ---------------------------------------------------------------------

        chat_messages_path = "log/chat_messages.list"
        try:
            chat_messages_file = file(chat_messages_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append" % chat_messages_path)
            return
        chat_messages_file.write(argument)
        chat_messages_file.close()
    #- Fine Metodo -

    # (TD) da spostare nel modulo connection?
    # magari sì! visto che c'è il metodo conn.get_user_agent
    def user_agent(self, request):
        """
        Esegue il log su file degli user agent sconosciuti.
        Poiché va' a scrivere su file esegue un controllo sul contenuto dello stesso
        a vedere se l'user agent è già stato inserito oppure no.
        """
        if not request:
            log.bug("request non è una parametro valido")
            return

        # -------------------------------------------------------------------------

        if (not request or not request.received_headers
         or not "user-agent" in request.received_headers
         or not request.received_headers["user-agent"]):
            return ""

        user_agent_path = "log/user_agents.txt"

        # Provvede ad inizializzare la lista in memoria degli user agent
        if not self.user_agents:
            # Se il file non esiste allora lo crea da zero
            if not os.path.exists(user_agent_path):
                try:
                    user_agent_file = file(user_agent_path, "w")
                except IOError:
                    log.bug("Impossibile creare il file %s" % user_agent_path)
                    return
                user_agent_file.close()

            # Ora invece legge il file per ricavare la lista di user agent
            try:
                user_agent_file = open(user_agent_path, "r")
            except IOError:
                log.bug("Impossibile aprire il file %s in lettura" % user_agent_path)
                return
            for line in user_agent_file:
                line = line.strip()
                if not line:
                    continue
                self.user_agents.append(line)
            user_agent_file.close()

        # Se l'user agent della richiesta non esiste nella lista in memoria,
        # allora lo aggiunge al file di log apposito e alla stessa lista
        if request.received_headers["user-agent"] not in self.user_agents:
            try:
                user_agent_file = open(user_agent_path, "a")
            except IOError:
                log.bug("Impossibile aprire il file %s in append" % user_agent_path)
                return
            user_agent_file.write(request.received_headers["user-agent"] + "\n")
            user_agent_file.close()
            self.user_agents.append(request.received_headers["user-agent"])
    #- Fine Metodo -

    # (TD) da spostare nel modulo interpret?
    def huh_inputs(self, entity, wrong_input):
        """
        Esegue il log dei comandi digitati erroneamente su un file apposito.
        """
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not wrong_input:
            log.bug("wrong_input non è un parametro valido: %r" % wrong_input)
            return

        # -------------------------------------------------------------------------

        huh_inputs_path = "log/huh_inputs.list"
        try:
            huh_inputs_file = open(huh_inputs_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append" % huh_inputs_path)
            return

        huh_inputs_file = open(huh_inputs_path, "a")
        huh_inputs_file.write("(%s) %s: %s\n" % (datetime.datetime.now(), entity.code, wrong_input))
        huh_inputs_file.close()
    #- Fine Metodo -

    def html_output(self, html_code, player):
        """
        Salva su file separati l'output inviato ad ogni giocatore, serve a
        controllare che tutti i tag del codice html generato siano corretti.
        """
        if not html_code:
            log.bug("html_code non è un parametro valido: %r" % html_code)
            return

        if not player:
            log.bug("player non è un parametro valido: %r" % player)
            return

        # -------------------------------------------------------------------------

        if not hasattr(player, "game_request"):
            log.bug("Attributo game_request inesistente per %r, qui devono passare solo le entità player" % player)
            return

        if not player.game_request:
            log.bug("game_request non valido per l'entità %s: %r" % (player.code, player.game_request))
            return

        html_log_path = "log/%s %d.html.txt" % (player.code, id(player.game_request))
        try:
            html_log_file = open(html_log_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append" % html_log_path)
            return

        html_log_file.write(html_code)
        html_log_file.close()
    #- Fine Metodo -

    # (TD) da spostare nel modulo help?
    def huh_helps(self, entity, wrong_argument):
        """
        Esegue il log degli help digitati erroneamente su un file apposito.
        """
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not wrong_argument:
            log.bug("wrong_argument non è un parametro valido: %r" % wrong_argument)
            return

        # -------------------------------------------------------------------------

        huh_helps_path = "log/huh_helps.list"
        try:
            huh_helps_file = open(huh_helps_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append" % huh_helps_path)
            return

        huh_helps_file.write("(%s) %s: %s\n" % (datetime.datetime.now(), entity.code, wrong_argument))
        huh_helps_file.close()
    #- Fine Metodo -

    def cpu_time(self):
        """
        Stampa su di un file di log l'occupazione del processore.
        """
        from src.config import config
        from src.engine import engine
        from src.game   import game_loop

        elapsed_seconds = engine.boot_seconds + game_loop.elapsed_seconds
        if elapsed_seconds <= 0:
            return

        cpu_time_path = "log/cpu_times.stat"

        is_empty = False
        try:
            if os.stat(cpu_time_path).st_size == 0:
                is_empty = True
        except:
            is_empty = True

        try:
            cpu_time_file = open(cpu_time_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append" % cpu_time_path)
            return

        if is_empty:
            cpu_time_file.write("#versione gioco; pid del gioco; data e ora; secondi d'utilizzo del processore accumulati dal gioco; secondi d'utilizzo del processore accumulati dal sistema per il gioco\n")

        times_results = os.times()
        cpu_time_file.write("%s;%s;%s;%f;%f\n" % (
            config.engine_version,
            os.getpid(),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            times_results[0] / elapsed_seconds,
            times_results[1] / elapsed_seconds))

        cpu_time_file.close()
    #- Fine Metodo -

    # (TD) da spostare nel modulo connection?
    def connections(self):
        """
        Stampa su di un file di log il numero di connessioni attive e in gioco.
        """
        from src.connection import connections
        from src.config     import config

        connections_path = "log/connections.stat"

        is_empty = False
        try:
            if os.stat(connections_path).st_size == 0:
                is_empty = True
        except:
            is_empty = True

        try:
            connections_file = open(connections_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append" % connections_path)
            return

        if is_empty:
            connections_file.write("#versione gioco; pid del gioco; data e ora; giocatori collegati; connessioni al sito totali; lista degli eventuali giocatori online\n")

        counter = 0
        players = ""
        for conn in connections.itervalues():
            if conn.player and conn.player.game_request:
                counter += 1
                players += " %s" % conn.player.code

        connections_file.write("%s;%s;%s;%d;%d;%s\n" % (
            config.engine_version,
            os.getpid(),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            counter,
            len(connections),
            players.strip()))

        connections_file.close()
    #- Fine Metodo -

    def write_overbuffer(self, buffer):
        overbuffer_path = "log/overbuffer.log"

        try:
            overbuffer_file = open(overbuffer_path, "w")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura" % overbuffer_path)
            return

        overbuffer_file.write(buffer)
        overbuffer_file.close()
    #- Fine Metodo -


#= SINGLETON ===================================================================

log = Log()
