# -*- coding: utf-8 -*-

"""
Gestisce i dialoghi e le conversazioni tra due entità.
"""


#= IMPORT ======================================================================

from src.log       import log
from src.interpret import interpret


#= CLASSI ======================================================================

class _GenericStatement(object):
    """
    Classe per la gestione di una singola risposta sia da parte di un'entità
    che da parte di un giocatore.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"actions"             : ("", "str"),
                   "speaker_statements"  : ("src.dialog", "SpeakerStatement"),
                   "listener_statements" : ("src.dialog", "ListenerStatement")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.choice_text         = ""  # Testo che viene visualizzato come scelta da cliccare per continuare il dialogo
        self.actions             = []  # Ogni elemento di statement contiene uno o più input da inviare in sequenza, servono a non dover utilizzare gamescript per forza
        self.before_check        = ""  # Codice in una linea o riferimento ad un gamescript, di solito serve a controllare se il testo deve essere visualizzato
        self.after_check         = ""  # Codice in una linea o riferimento ad un gamescript, di solito si utilizza per inviare comandi dopo scelto quel testo
        self.mark                = ""  # Segna con un nome questo testo per poterci tornare da una lista di statement differente
        self.goto_mark           = ""  # Salta al mark indicato una volta scelto questo statement, goto non centra nulla con il comando di admin
        self.icon                = ""  # Inserisce una icona grafica per questo statement
        self.speaker_statements  = []  # Se poi si vuole far parlare l'entità bisogna utilizzare questa
        self.listener_statements = []  # Se poi si vuole far parlare il pg bisogna utilizzare questa
    #- Fine Inizializzazione -

    def get_error_message(self):
        msg = ""
        if not self.speaker_statements and self.listener_statements:
            msg = "Non c'è nessun speaker_statements oppure listener_statements valido."
        else:
            return ""

        if self.__class__.__name__ in ("ListenerStatement", "SpeakerStatement"):
            log.bug("(%s) %s" % self.__class__.__name__, msg)
        return msg
    #- Fine Metodo -

    def send_statement(self, speaker, listener):
        if not speaker:
            log.bug("speaker non è un parametro valido: %s" % speaker)
            return

        if not listener:
            log.bug("listener non è un parametro valido: %s" % listener)
            return

    #--------------------------------------------------------------------------

        # (TD) import interno per essere sicuro di non avere le lista vuota
        # non ancora inizializzate
        from src.interpret import inputs_command_en, inputs_skill_en, inputs_social_en

        for action in self.actions:
            arg, argument = one_argument(action)
            input = action.find_input(arg, True, inputs_command_en + inputs_skill_en + inputs_social_en)
            if input:
                if self.__class__.__name__ == "ListenerStatement":
                    interpret(listener, action, use_check_alias=False)
                else:
                    interpret(speaker, action, use_check_alias=False)
            else:
                listener.send_output(action)

        statements = self.listener_statements or self.speaker_statements
        for counter, statement in enumerate(statements):
            listener.send_output('''%d] %s''' % (counter + 1, self.choice_text))
    #- Fine Metodo -

class ListenerStatement(_GenericStatement): pass
class SpeakerStatement(_GenericStatement): pass


class Dialog(_GenericStatement):
    """
    Classe per la gestione di un dialogo.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = _GenericStatement.VOLATILES + []
    MULTILINES  = _GenericStatement.MULTILINES + ["comment"]
    SCHEMA      = {}
    SCHEMA.update(_GenericStatement.SCHEMA)
    REFERENCES  = {}
    REFERENCES.update(_GenericStatement.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(_GenericStatement.WEAKREFS)

    def __init__(self, code=""):
        super(Dialog, self).__init__()
        self.comment      = ""    # Commento che serve a spiegare il motivo del dialogo e quando si attiva
        self.code         = code  # Codice identificativo del dialogo
        self.introduction = ""
    #- Fine Inizializzazione -

    def get_error_message(self):
        msg = super(ProtoEntity, self).get_error_message()
        if msg:
            pass
        elif not self.code:
            msg = "code non è una stringa valida: %s" % self.code
        else:
            return ""

        log.bug("(Dialog: %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -


class Conversation(object):
    """
    Classe per la gestione delle conversazioni in-game.
    """
    def __init__(self, player, entity, dialog):
        if not player:
            log.bug("player non è un parametro valido: %s" % player)
            return

        if not entity:
            log.bug("entity non è un parametro valido: %s" % entity)
            return

        if not dialog:
            log.bug("dialog non è un parametro valido: %s" % dialog)
            return

        # ---------------------------------------------------------------------

        self.already_choised = {}  # Memorizza gli statement già scelti per non visualizzarli più nella corrente conversazione
    #- Fine Inizializzazione -

    def show_dialog_msg(self, speaker, listener):
        if not speaker:
            log.bug("speaker non è valido: %s" % speaker)
            return

        if not listener:
            log.bug("listener non è valido: %s" % listener)
            return

        # ---------------------------------------------------------------------

        if speaker.IS_PLAYER:
            player = speaker
            entity = listener
        else:
            player = listener
            entity = speaker

        # Che il giocatore sia quello che parla o quello che ascolta deve
        # comunque visualizzare l'introduzione del dialogo
        

        # players_statements e entity_statements non possono essere utilizzati
        # tutti e due allo stesso tempo, solo uno alla volta, quindi il primo
        # che trova non vuoto lo utilizza per creare il menù iniziale della
        # conversazione
        if self.player_statements:
            statements = self.player_statements
        else:
            statements = self.entity_statements
        for statement in statements:
            # (TD)
            player.send_output("%d] %s" % (counter, statement.text))
    #- Fine Metodo -

    def get_error_message(self):
        # (TD)
        pass
    #- Fine Metodo -


#= FUNZIONI ====================================================================
