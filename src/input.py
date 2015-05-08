# -*- coding: utf-8 -*-

"""
Modulo per la classe degli inputi inviati al Mud da parte dei giocatori.
Qui vi è solo la classe rappresentante l'input per le funzioni relative
all'interpretazione dell'input inviato da parte dei giocatori andare a
vedere il file interpret.py
"""


#= IMPORT ======================================================================

from src.engine  import engine
from src.log     import log
from src.utility import clean_string


#= CLASSI ======================================================================

class Input(object):
    """
    Gestisce un input.
    """
    # Non ha una chiave primaria perché inserito in una lista
    # e non in un dizionario
    PRIMARY_KEY = ""
    VOLATILES   = ["counter_use", "findable_words"]
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {"command" : ["commands"]}
    WEAKREFS    = {}

    def __init__(self):
        self.comment       = ""
        self.alternative   = False  # Indica se l'input è quello considerato ufficiale oppure un'alternativa di un altro input
        self.command       = None  # Comando legato all'input
        self.words         = ""

        # Variabili volatili:
        self.counter_use    = 0
        self.findable_words = []  # Serve per migliorare le prestazioni alla find_input
    #- Fine Inizializzazione -

    def get_error_message(self):
        if not self.words:
            msg = "variabile words non valida"
        elif not self.findable_words:
            msg = "variabile words non valida"
        # (bb) disattivato momentaneamente per evitare spam nel log, non ho voglia di correggerle per ora
#        elif not self._check_correctness_of_words():
#            msg = "le parole non iniziano tutte con la stessa radice"
        elif not self.command:
            msg = "La funzione di comando non è valida"
        # Devo aggiungere il check riguardante la stringa per evitare che
        # scatti l'errore durante la funzione fread_input poiché self.command
        # nel caricamento dei dati è ancora una stringa e non un riferimento
        # ad un'istanza di comando
        elif (not (engine.booting and isinstance(self.command, basestring))
        and self.command.get_error_message() != ""):
            msg = self.command.get_error_message()
        elif self.counter_use < 0:
            msg = "Il contatore d'utilizzo è negativo: %s" % self.counter_use
        else:
            return ""
        # Se arriva qui ha trovato un errore
        log.bug("(Input: words %s) %s" % (self.words, msg))
        return msg
    #- Fine Metodo -

    def _check_correctness_of_words(self):
        # Controlla che le radici delle parole dell'input siano tutte uguali
        for word in self.findable_words[1 : ]:
            if word[ : 2] != self.findable_words[0][ : 2]:
                return False
        return True
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        """
        Ricava dalla linea passata gli attributi di un input.
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

        line = line.lower()
        if line[0] == "=":
            alternative, fun_name, words = line.split(None, 2)
        else:
            alternative = ""
            fun_name, words = line.split(None, 1)

        self.command = fun_name.strip()
        if alternative == "=":
            self.alternative = True
        self.words = words.strip()
        self.findable_words = clean_string(self.words).split()

        if self.get_error_message() != "":
            log.bug("Input letto dal file <%s> alla riga <%s> per l'attributo <%s> è errato" % (file.name, line, attr))
            return
    #- Fine Metodo -

    def fwrite(self, file):
        """
        Scrive su file tutte le informazioni relative ad un input.
        """
        if not file:
            log.bug("file non è valido: %s" % file)
            return

        # -------------------------------------------------------------------------

        if self.alternative:
            file.write("= ")
        else:
            file.write("  ")
        file.write("%s %s\n" % (self.fun_name, self.words))
    #- Fine Metodo -
