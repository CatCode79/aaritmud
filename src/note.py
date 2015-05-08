# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle note.
Servono ad inviare dei messaggi in gioco: attualmente typo, bug e idea.
"""


#= IMPORT ======================================================================

import datetime
import random

from src.calendar import calendar
from src.color    import remove_colors
from src.command  import get_command_syntax
from src.config   import config
from src.data     import Data
from src.database import fwrite, database
from src.enums    import GRAMMAR, LOG
from src.grammar  import add_article, get_article
from src.log      import log
from src.mail     import mail


#= CLASSI ======================================================================

class _Note(Data):
    PRIMARY_KEY = "code"
    VOLATILES   = []
    MULTILINES  = ["text"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, code="", who="", where="", when="", text=""):
        self.code    = code
        self.who     = remove_colors(who) if who else ""   # Chi ha inviato la nota
        self.where   = where                               # Da dove l'ha inviata
        self.when    = remove_colors(when) if when else "" # Quando l'ha inviata
        self.text    = text                                # Testo della nota
    #- Fine Inizializzazione -

    def get_error_message(self):
        if not self.code:
            msg = "code non è valido: %r" % self.code
        elif not self.who:
            msg = "who non è valido: %r" % self.who
        elif not self.where:
            msg = "where non è valido: %r" % self.where
        elif not self.when:
            msg = "when non è valido: %r" % self.when
        elif not self.text:
            msg = "text non è valido: %r" % self.text
        else:
            msg = ""

        if msg:
            return "[%d] %s" (self.code, msg)
        else:
            return ""
    #- Fine Metodo -


class Bug(_Note):
    """
    Tipologia di nota inviata come segnalazione di bug agli Admin del Mud.
    """
    SCHEMA = {"replies" : ("src.note", "Bug")}
    SCHEMA.update(_Note.SCHEMA)


class Typo(_Note):
    """
    Tipologia di nota inviata come typo agli Admin del Mud.
    """
    SCHEMA = {"replies" : ("src.note", "Typo")}
    SCHEMA.update(_Note.SCHEMA)


class Idea(_Note):
    """
    Tipologia di nota inviata come idea agli Admin del Mud.
    """
    SCHEMA = {"replies" : ("src.note", "Idea")}
    SCHEMA.update(_Note.SCHEMA)

class Comment(_Note):
    """
    Tipologia di nota inviata come comment agli Admin del Mud.
    """
    SCHEMA = {"replies" : ("src.note", "Comment")}
    SCHEMA.update(_Note.SCHEMA)


#= FUNZIONI ====================================================================

# (TD) devo fare qualcosa per tutti questi add_article e get_article, magari
# calcolando tot differenti parole all'inizio e riutilizzandole poi
def send_note(entity, argument, command_name, note_type, note_singular, note_plural, note_class, grammar_genre):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # argument può essere una stringa vuota

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    if not note_type:
        log.bug("note_type non è un parametro valido: %r" % note_type)
        return False

    if not note_singular:
        log.bug("note_singular non è un parametro valido: %r" % note_singular)
        return False

    if not note_class:
        log.bug("note_class non è un parametro valido: %r" % note_class)
        return False

    if not grammar_genre:
        log.bug("grammar_genre non è un parametro valido: %r" % grammar_genre)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, command_name)
        entity.send_output(syntax, break_line=False)
        return False

    if not entity.IS_PLAYER:
        entity.send_output("Solo i giocatori possono inviare %s." % (
            add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR)))
        return False

    if config.max_account_typos == 0:
        entity.send_output("L'invio %s è stata disabilitata." % (
            add_article(note_plural, grammar_genre, GRAMMAR.INDETERMINATE, GRAMMAR.PLURAL)))
        return False

    # Non dovrebbe mai capitare, ma non si sa mai, in teoria comunque non è un baco
    if not entity.account:
        entity.send_output("La sessione del tuo account è scaduta, devi riaccedere nuovamente al sito per poter inviare %s" % (
            add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR)))
        return False

    # Anche questa non dovrebbe mai capitare
    if not entity.location:
        entity.send_output("Ti è impossibile inviare %s da questo luogo." % (
            add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR)))
        log.bug("entity.location non è valido (%r) per entity %s mentre stava cercando di inviare una nota %s" % (
            entity.location, entity.code, note_type))
        return False

    # Crea il codice per la nota
    code_to_check = entity.account.name + "#"
    sended_notes = getattr(entity.account, "sended_%ss" % note_type)
    code = code_to_check + str(sended_notes)

    # Se il codice già esiste nel database probabilmente c'è una dicrepanza
    # tra il dato di account e quelli delle note quindi il codice si
    # incrementa fino a trovare un numero libero
    counter = 1
    while code in database[note_type + "s"]:
        code = code_to_check + str(sended_notes + counter)
        setattr(entity.account, "sended_%ss" % note_type, sended_notes + counter + 1)
        counter += 1

    who = entity.code
    if entity.IS_PLAYER and entity.account:
        who += " dell'account %s" % entity.account.name
    if entity.location.IS_ROOM:
        where = "%s (%r)" % (entity.location.code, entity.location.get_destination())
    else:
        where = "%s in %r  " % (entity.location.get_name(), entity.get_in_room.get_destination())
    when = "%s (%s %s %s %s)" % (datetime.datetime.now(), calendar.minute, calendar.hour, calendar.day, calendar.month)

    note = note_class(code, who, where, when, argument)
    if not note:
        log.bug("note non è valido (%r) per la tipologia %s" % (note, note_type))
        entity.send_output("Impossibile segnalare un%s nuov%s %s." % (
            "" if grammar_genre == GRAMMAR.MASCULINE else "a", "o" if grammar_genre == GRAMMAR.MASCULINE else "a", note_singular))
        return False

    # Evitare di inviare una nota subito dopo averne inviata un'altra,
    # così da evitare eventuali spammer
    last_note_sended_at = getattr(entity.account, "last_%s_sended_at" % note_type)
    if (datetime.datetime.now() - last_note_sended_at).days <= 0:
        # (TD) Python 2.7, così non servirà più il check su days
        #total_seconds = (datetime.datetime.now() - last_note_sended_at).total_seconds()
        total_seconds = (datetime.datetime.now() - last_note_sended_at).seconds
        if total_seconds < config.sending_interval:
            remaining_seconds = config.sending_interval - total_seconds
            random_id = random.random()
            entity.send_output('''Potrai inviare %s solo tra <span id="%s">%d %s</span><script>parent.countdown("%s");</script>''' % (
                add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR, GRAMMAR.POSSESSIVE),
                random_id, remaining_seconds, "secondo" if remaining_seconds == 1 else "secondi", random_id))
            return False

    # Inserisce un tetto massimo di note ancora aperte inviabili contando se
    # effettivamente le note dell'account ancora aperte sono così tante
    counter = 0
    for note_code in database[note_type + "s"]:
        if note_code.startswith(code_to_check):
            counter += 1
    if counter >= getattr(config, "max_account_%ss" % note_type):
        entity.send_output("Hai raggiunto il massimo di %s attualmente segnalabili, riprova tra qualche minuto." % (note_plural, config.game_name))
        log.monitor("%s ha raggiunto il numero massimo di %s inviabili, controllare e chiudere quelle obsolete cosicché possa inviarne delle altre.", (
            entity.code, note_plural))
        return False

    # Controlla che le altre note non abbiano lo stesso testo, altrimenti ci
    # troviamo davanti ad un possibile spammer, il sistema quindi fa finta
    # di salvarsi la nota e intanto segnala agli Amministratori lo spammer
    for other_note in database[note_type + "s"].itervalues():
        if other_note.text == argument and other_note.code.startswith(code_to_check):
            entity.send_output("%s è stato salvato. Grazie!" % (
                add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR, GRAMMAR.POSSESSIVE).capitalize()))
            log.warning("Qualcuno per sbaglio invia due volte la stessa nota %s. Se continua esageratemente è un possibile spammer (%s)" % (
                note_singular, entity.get_conn().get_id()))
            return False

    database[note_type + "s"][note.code] = note

    # Le note sono uno di quei dati slegati dal gioco che possono essere
    # scritti subito sul disco vista la relativa rarità del suo invio e quindi
    # la bassa probabilità che vada ad inficiare sulle prestazioni globali
    note_path = "data/%ss/%s.dat" % (note_type, note.code)
    try:
        note_file = open(note_path, "w")
    except IOError:
        entity.send_output("Per un errore interno al server è impossibile salvare %s." % (
            add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR, GRAMMAR.POSSESSIVE)))
        log.bug("Impossibile aprire il file %s in scrittura" % note_path)
        return False
    fwrite(note_file, note)
    note_file.close()

    # Poiché è stato salvata la nota bisogna anche salvare l'account che
    # contiene il numero di note inviate da sempre incrementato giusto qui
    # (TT) Bisogna fare attenzione al salvataggio facile dell'account,
    # potrebbero in futuro esservi informazioni duplicate o erroneamente
    # incrementate (dopo un crash) a seconda delle dipendenze tra i dati
    # nell'account ed altre tipologie di dati che non verrebbero salvate
    # se non alla chisura del Mud
    setattr(entity.account, "sended_%ss" % note_type, sended_notes + 1)
    setattr(entity.account, "last_%s_sended_at" % note_type, datetime.datetime.now())
    account_path = "persistence/accounts/%s.dat" % entity.account.name
    try:
        account_file = open(account_path, "w")
    except IOError:
        entity.send_output("Per un errore interno al server è impossibile salvare %s." % (
            add_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR, GRAMMAR.POSSESSIVE)))
        log.bug("Impossibile aprire il file %s in scrittura" % account_path)
        return False
    fwrite(account_file, entity.account)
    account_file.close()

    entity.send_output("Hai appena segnalato %s%d° %s. Grazie!" % (
        get_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR, GRAMMAR.POSSESSIVE),
        sended_notes+1,
        note_singular))

    # Invia la mail
    subject = "Invio %s" % note_singular
    text = "L'account %s ha appena segnalato %s%d° %s." % (
        entity.account.name,
        get_article(note_singular, grammar_genre, GRAMMAR.DETERMINATE, GRAMMAR.SINGULAR),
        sended_notes+1,
        note_singular)
    text += "\nWho: %s"   % note.who
    text += "\nWhere: %s" % note.where
    text += "\nWhen: %s"  % note.when
    text += "\nText: %s"  % note.text

    mail.send_to_admins(subject, text, show_players=False)
    return True
#- Fine Funzione -
