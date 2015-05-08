# -*- coding: utf-8 -*-

"""
Modulo per per l'interpretazione dell'input inviato da parte dei giocatori:
che siano comandi, skill o social.
"""


#= IMPORT ======================================================================

import random
import sys
import time

from twisted.internet import error

from src.database   import database
from src.defer      import defer
from src.color      import remove_colors
from src.config     import config
from src.engine     import engine
from src.enums      import CMDFLAG, CMDTYPE, FLAG, INTENTION, LOG, OPTION, POSITION, TO
from src.gamescript import check_trigger
from src.grammar    import grammar_gender
from src.log        import log
from src.miml       import MIML_SEPARATOR
from src.utility    import is_same, is_prefix, one_argument, clean_string, is_number, html_escape

from src.commands.command_afk   import command_afk
from src.commands.command_sleep import command_sleep
from src.commands.command_rest  import command_rest
from src.commands.command_knee  import command_knee
from src.commands.command_sit   import command_sit
from src.commands.command_stand import command_stand


#= VARIABILI ===================================================================

inputs_command_it = []
inputs_command_en = []
inputs_skill_it   = []
inputs_skill_en   = []
inputs_social_it  = []
inputs_social_en  = []


#= CLASSI ======================================================================

class ActionInProgress(object):
    """
    Classe che viene utilizzata dopo l'invio di alcuni comandi, come il dig,
    che abbisognano di tempo per essere eseguiti.
    Vi è poi il pezzo di codice relativo all'action_in_progress che si trova
    nella funzione interpret serve ad interromperne l'esecuzione.
    """
    def __init__(self, seconds, defer_later_function, stop_function, *args):
        self.defer_later   = defer(seconds, defer_later_function, *args)
        self.stop_function = stop_function
        self.args          = args
    #- Fine Inizializzazione -

    def stop(self):
        try:
            self.defer_later.pause()
        except error.AlreadyCalled:
            log.bug("action in progress already called (stop_function %r): %s %s" % (
                self.stop_function, sys.exc_info()[0], sys.exc_info()[1]))
        self.defer_later = None
        self.stop_function(*self.args)
        self.stop_function = None
        self.args = None
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def interpret(entity, argument, use_check_alias=True, force_position=True, show_input=True, show_prompt=True, behavioured=False):
    """
    Funzione che interpreta gli inputi inviati dalle entità.
    L'argomento use_check_alias a False viene passato dalla find_alias per
    evitare chiamate di alias da altri alias e quindi ricorsioni.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    # Si assicura che colui che esegue l'azione sia un'entità unica e
    # non un mucchio fisico
    entity = entity.split_entity(1)

    if FLAG.CONVERSING in entity.flags and len(argument) == 1 and is_number(argument):
        # (TD)
        return

    arg, argument = one_argument(argument, search_separator=False)
    arg = arg.lower()

    input, huh_input, lang = multiple_search_on_inputs(entity, arg, use_check_alias=use_check_alias, argument=argument)
    # Utilizzo bislacco di lang per indicare che è stato trovato un alias
    # e che questo verrà processato tramite un'altra chiamata all'interpret
    if use_check_alias and lang == "alias":
        return

    # Resetta l'inattività di un player se ha inviato un comando
    if entity.IS_PLAYER:
        entity.inactivity = 0

    # Se non ha trovato nulla invia un messaggio apposito
    if not input:
        if show_input:
            entity.send_output(''' <span class="system">%s %s</span>''' % (remove_colors(arg), argument))
        entity.send_output("Huh?")
        # Se l'input non è stato trovato neanche nell'altra lingua allora
        # esegue il log dell'input, potrebbero esservene alcuni di sensati
        # da utilizzare in futuro come sinonimi
        # Scrive anche gli huh input dei mob così da ricavare gamescript o
        # random_do_inputs errati
        if not huh_input:
            log.huh_inputs(entity, arg)
        # Se serve visualizza il prompt
        if show_input:
            entity.send_prompt()
        return False

    # Poiché alcune words nello stesso input a volte hanno prefisso differente
    # tra loro allora cerca quello più simile possibile per farlo visualizzare
    # all'utente
    founded_input = input.findable_words[0]
    for word in input.findable_words:
        if is_prefix(arg, word):
            founded_input = word
            break

    # Se il giocatore è in stato di wait e l'input è un comando interattivo
    # allora evita di inviarlo subito ma lo mette in coda
    if entity.deferred_wait and CMDFLAG.INTERACT in input.command.flags:
        entity.waiting_inputs.append("%s %s" % (founded_input, argument))
        return False
    else:
        # Altrimenti scrive anche l'input a fianco del prompt
        if show_input:
            entity.send_output(''' <span class="system">%s %s</span>''' % (founded_input, argument))

    # Se il pg si è scollegato dalla pagina di gioco non esegue il comando
    if not entity.location:
        return False

    # Vengono salvate le informazioni sull'ultimo input inviato
    if argument:
        last_input = "%s %s" % (arg, argument)
    else:
        last_input = arg
    engine.last_input_sender = entity
    engine.last_input_sended = last_input
    # Si salva l'ultimo input inviato con successo
    if show_input and entity.IS_PLAYER and CMDFLAG.NO_LAST_INPUT not in input.command.flags:
        entity.last_input = last_input

    if CMDFLAG.GDR in input.command.flags:
        entity.sended_inputs.append("%s %s" % (founded_input, argument))

    if argument:
        argument = html_escape(argument)

    # Gestisce i comandi che devono essere digitati per intero
    command = input.command
    if CMDFLAG.TYPE_ALL in command.flags and not is_same(arg, input.findable_words):
        first_words, other_words = one_argument(input.words, search_separator=False)
        entity.send_output("Se vuoi veramente farlo devi scrivere per intero [limegreen]%s[close]." % first_words)
        execution_result = False
    elif not check_position(entity, command.position, force_position):
        # Se la posizione non è corretta invia il relativo messaggio d'errore
        vowel_of_genre = grammar_gender(entity)
        if entity.position == POSITION.DEAD:
            entity.send_output("Un po' difficile fino a che rimani MORT%s.." % vowel_of_genre.upper())
        elif (entity.position == POSITION.MORTAL
        or    entity.position == POSITION.INCAP):
            entity.send_output("Sei troppo ferit%s per farlo." % vowel_of_genre)
        elif entity.position == POSITION.STUN:
            entity.send_output("Sei troppo intontit%s per farlo." % vowel_of_genre)
        elif entity.position == POSITION.SLEEP:
            entity.send_output("Nei tuoi sogni, o cosa?")
        elif entity.position == POSITION.REST:
            entity.send_output("Nah.. Sei troppo rilassat%s ora.." % vowel_of_genre)
        elif entity.position == POSITION.KNEE:
            entity.send_output("Non puoi farlo da inginocchiat%s" % vowel_of_genre)
        elif entity.position == POSITION.SIT:
            entity.send_output("Non puoi farlo da sedut%s." % vowel_of_genre)
        else:
            log.bug("Manca la posizione %r" % entity.position)
        execution_result = False
    else:
        if command.type == CMDTYPE.SOCIAL:
            check_social(entity, command, argument=argument, behavioured=behavioured)

        if CMDFLAG.PRIVATE not in command.flags and (entity.IS_PLAYER or config.print_entity_inputs) and show_input and show_prompt:
            if entity.IS_PLAYER:
                write_on_file = True
            else:
                write_on_file = False
            log.input("'%s%s%s' digitato da %s in %s" % (
                founded_input,
                " " if argument else "",
                argument,
                entity.code,
                entity.location.get_name()), write_on_file=write_on_file)

        # Per comodità di sviluppo ricarica il modulo relativo al comando ogni
        # volta che lo si digita, così da poter testare le modifiche al codice
        # dei comandi senza aver bisogno di riavviare il gioco tutte le volte
        if config.reload_commands:
            reload(command.module)
            command.import_module_and_function()

        # Se si sta eseguendo un'azione che richiede tempo la interrompe
        if entity.action_in_progress and CMDFLAG.INTERACT in command.flags:
            if entity.action_in_progress.defer_later:
                entity.action_in_progress.stop()
            entity.action_in_progress = None

        # Esegue la funzione del comando cronometrandola
        input.counter_use += 1
        starting_time = time.time()
        execution_result = (command.function)(entity, argument)
        if command.fun_name[ : 8] == "command_" and execution_result != True and execution_result != False:
            log.bug("execution_result non è valido per il comando %s: %r" % (command.fun_name, execution_result))
        if command.fun_name[ : 6] == "skill_" and execution_result != "clumsy" and execution_result != "failure" and execution_result != "success" and execution_result != "magistral":
            log.bug("execution_result non è valido per la skill %s: %r" % (command.fun_name, execution_result))
        execution_time = time.time() - starting_time
        # Comandi che superano il tempo definito nella max_execution_time
        # possono portare a bachi creati dalla deferred impostata nel metodo
        # split_entity (nello stesso metodo c'è un commento con più informazioni)
        # Quindi devono essere il più possibile da evitare, allo stesso tempo
        # sarebbe meglio che il max_execution_time sia relativamente basso.
        if execution_time > config.max_execution_time:
            log.time("Il comando %s è stato eseguito in troppo tempo: %f secondi" % (command.fun_name, execution_time))
        command.timer += execution_time

    # Gestisce i comandi da loggare
    if CMDFLAG.LOG in command.flags:
        log.command("%s %s" % (command.fun_name, argument))

    if FLAG.AFK in entity.flags and command.fun_name != "command_afk":
        command_afk(entity)

    # Infine visualizza il prompt
    if show_prompt:
        entity.send_prompt()

    # Se la lista di input ancora da inviare non è vuota allora crea un
    # "falso wait" per forzarne l'invio. In teoria potrei inviarlo da qui, ma
    # il codice di ritorno execution_result andrebbe perduto, ecco perché
    # si fa uso della wait().
    if not entity.deferred_wait and entity.waiting_inputs:
        entity.wait(0.001)

    # Questa parte è da attivare con l'opzione check_references solo nei
    # server di test perché consuma molta cpu essendo eseguita su migliaia
    # di dati ad ogni invio di input, è una modalità di diagnostica
    # che non bada a spese in termini prestazionali
    if config.check_references and not database.reference_error_found:
        database.check_all_references()

    return execution_result
#- Fine Funzione -


def multiple_search_on_inputs(entity, arg, exact=False, use_check_alias=False, argument=""):
    """
    Funzione nucleo per la ricerca di un input tra tutti gli input relativi
    alla lingua dell'entità, oppure a tutte e due se ha configurato l'opzione
    apposita.
    """
    # entity può essere None

    if not arg:
        log.bug("arg non è un parametro valido : %r" % arg)
        return None, None, ""

    # -------------------------------------------------------------------------

    # Decide la lingua principale e quella secondaria
    if not entity:
        lang1 = "en"
        lang2 = "en"
    elif entity.IS_PLAYER and entity.account and OPTION.ITALIAN in entity.account.options:
        lang1 = "it"
        lang2 = "en"
    else:
        lang1 = "en"
        lang2 = "it"

    # Prepara le liste di comandi di lingua principale e secondaria per la ricerca
    inputs_command_1 = globals()["inputs_command_%s" % lang1]
    inputs_command_2 = globals()["inputs_command_%s" % lang2]
    inputs_skill_1   = globals()["inputs_skill_%s"   % lang1]
    inputs_skill_2   = globals()["inputs_skill_%s"   % lang2]
    inputs_social_1  = globals()["inputs_social_%s"  % lang1]
    inputs_social_2  = globals()["inputs_social_%s"  % lang2]

    founded_input = ""

    # Ricerca nella lingua principale in maniera esatta
    input = None
    if not input:  input = find_input(arg, inputs_command_1, True, entity)
    if entity and not input and use_check_alias and hasattr(entity, "account") and entity.account.check_alias(arg, argument):
        return None, None, "alias"
    if not input:  input = find_input(arg, inputs_skill_1,  True, entity)
    if not input:  input = find_input(arg, inputs_social_1, True, entity)

    # Ricerca nella lingua principale in maniera prefissa
    if not exact:
        if not input:  input = find_input(arg, inputs_command_1, False, entity)
        if not input:  input = find_input(arg, inputs_skill_1,   False, entity)
        if not input:  input = find_input(arg, inputs_social_1,  False, entity)

    founded_lang = ""
    if input:
        founded_lang = lang1

    # Ricerca esatta e poi prefissa nella lingua secondaria
    huh_input = None
    if entity and entity.IS_PLAYER:
        if not huh_input:  huh_input = find_input(arg, inputs_command_2, True,  entity)
        if not huh_input:  huh_input = find_input(arg, inputs_skill_2,   True,  entity)
        if not huh_input:  huh_input = find_input(arg, inputs_social_2,  True,  entity)
        if not exact:
            if not huh_input:  huh_input = find_input(arg, inputs_command_2, False, entity)
            if not huh_input:  huh_input = find_input(arg, inputs_skill_2,   False, entity)
            if not huh_input:  huh_input = find_input(arg, inputs_social_2,  False, entity)
        if not input and huh_input and entity.account and OPTION.DOUBLE_LANG in entity.account.options:
            founded_lang = lang2
            input = huh_input

    return input, huh_input, founded_lang
#- Fine Funzione -


def yield_inputs_items():
    """
    Ritorna man mano una coppia di valori di questo tipo:
    (nome della variabile degli inputs, lista degli inputs).
    """
    yield ("inputs_command_it", inputs_command_it)
    yield ("inputs_command_en", inputs_command_en)
    yield ("inputs_skill_it",   inputs_skill_it  )
    yield ("inputs_skill_en",   inputs_skill_en  )
    yield ("inputs_social_it",  inputs_social_it )
    yield ("inputs_social_en",  inputs_social_en )
#- Fine Funzione -


def find_input(arg, inputs, exact, entity=None):
    """
    Cerca l'argomento passato nella lista di input passata.
    """
    if not arg:
        log.bug("arg non è valido: %s" % arg)
        return None

    if not inputs:
        log.bug("inputs non è valido: %s" % inputs)
        return None

    # exact ha valore di verità

    # -------------------------------------------------------------------------

    # Ricerca dell'input relativo all'argomento passato
    if exact:
        if entity and entity.IS_PLAYER:
            for input in inputs:
                if not input.command:
                    continue
                if input.command.trust > entity.trust and input.command.fun_name not in entity.permissions:
                    continue
                # Viene utilizzata la clean_string invece della is_same per motivi prestazionali
                if clean_string(arg) in input.findable_words:
                    return input
        else:
            for input in inputs:
                if not input.command:
                    continue
                if entity and input.command.trust > entity.trust:
                    continue
                # Viene utilizzata la clean_string invece della is_same per motivi prestazionali
                if clean_string(arg) in input.findable_words:
                    return input

    else:
        if entity and entity.IS_PLAYER:
            for input in inputs:
                if not input.command:
                    continue
                if input.command.trust > entity.trust and input.command.fun_name not in entity.permissions:
                    continue
                if is_prefix(arg, input.findable_words):
                    return input
        else:
            for input in inputs:
                if not input.command:
                    continue
                if entity and input.command.trust > entity.trust:
                    continue
                if is_prefix(arg, input.findable_words):
                    return input

    return None
#- Fine Funzione -


def interpret_or_echo(entity, argument, looker=None, behavioured=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    if MIML_SEPARATOR in argument:
        argument = entity.parse_miml(argument)
    if not argument:
        return

    if "$" in argument:
        argument = looker.replace_act_tags(argument, target=entity)
    if "$" in argument:
        argument = looker.replace_act_tags_name(argument, looker=looker, target=entity)

    original_argument = argument
    arg, argument = one_argument(argument)

    input, huh_input, lang = multiple_search_on_inputs(entity, arg, exact=True)
    if input:
        interpret(entity, original_argument, use_check_alias=False, show_input=False, show_prompt=False, behavioured=behavioured)
    else:
        entity.location.echo(original_argument)
#- Fine Funzione -


def check_position(entity, position, force_position=True):
    """
    Controlla che la posizione del comando passata sia adatta a quella che
    l'entità ha in questo momento.
    Viene passata force_position a False quando bisogna evitare ricorsioni.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not position:
        log.bug("position non è un parametro valido: %r" % position)
        return False

    # -------------------------------------------------------------------------

    # Se un mob non può eseguire il comando allora cerca di mettersi
    # nella posizione adatta ad eseguirlo
    if force_position and not entity.IS_PLAYER and entity.position < position:
        if position == POSITION.SLEEP:
            command_sleep(entity, argument)
        elif position == POSITION.REST:
            command_rest(entity, argument)
        elif position == POSITION.KNEE:
            command_knee(entity, argument)
        elif position == POSITION.SIT:
            command_sit(entity, argument)
        elif position == POSITION.STAND:
            command_stand(entity, argument)

    # Se la posizione dell'entità è corretta allora può eseguire il comando
    if entity.position >= position:
        return True

    return False
#- Fine Funzione -


def translate_input(obj, argument, lang="", search_type=None, colorize=False, alert=False):
    """
    Converte l'argomento, relativo ad un input, passato nel linguaggio voluto
    se la lingua utilizzata dall'entità per inviare input non corrisponde.
    Quando viene passato l'argomento lang è importante che sia corrispondente
    alla lingua dell'input in argument.
    Oltre che essere utilizzata dalla send_input questa funzione serve per
    tradurre il comando negli help.
    """
    # Se obj non è valido probabilmente il giocatore si trova in una pagina web

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    # Se lang rimane a valore di default allora ricava, secondo alcune regole,
    # la lingua da cercare per prima
    if not lang:
        if not obj:
            lang = "en"
        elif "account" in obj.__dict__:
            if OPTION.ITALIAN in obj.account.options:
                lang = "it"
            else:
                lang = "en"
        else:
            lang = "en"

    # Controlla la validità del valore lang
    if lang != "it" and lang != "en":
        log.bug("lang passato errato: %s" % lang)
        if colorize:
            return "[limegreen]%s[close]" % argument
        else:
            return argument

    # Converte il comando passato solo in questi casi:
    translate_to = lang
    if not obj:
        translate_to = "it"
    elif "account" in obj.__dict__:
        if lang == "en" and OPTION.ITALIAN in obj.account.options:
            translate_to = "it"
        elif lang == "it" and OPTION.ITALIAN not in obj.account.options:
            translate_to = "en"
        else:
            translate_to = lang
    else:
        translate_to = "en"
    if translate_to == lang:
        if colorize:
            return "[limegreen]%s[close]" % argument
        else:
            return argument

    if not search_type:
        search_type = [True, False]

    # Fa prima una ricerca esatta e poi prefissa
    for exact in search_type:
        for input_type in ("command", "skill", "social"):
            inputs_from = globals()["inputs_%s_%s" % (input_type, lang)]
            inputs_to   = globals()["inputs_%s_%s" % (input_type, translate_to)]
            # Cerca argument passato tra gli input della lingua originale
            input = find_input(argument, inputs_from, exact)
            if not input:
                continue
            # Cerca il relativo input nella lingua voluta
            for translated_input in inputs_to:
                if translated_input.alternative:
                    continue
                if translated_input.command == input.command:
                    arg = translated_input.words.split()[0]
            if argument.isupper():
                arg = arg.upper()
            elif argument[0].isupper():
                arg = arg.capitalize()
            if colorize:
                return "[limegreen]%s[close]" % arg
            else:
                return arg

    # Qui è normale che arrivi e non è un errore, questo perché a volte la
    # translate_input viene utilizzata anche su testo inviato dal giocatore.
    # Quindi in questi casi viene inviato l'argument senza modifiche.
    if alert:
        log.bug("Non è stato trovato nessun input valido da tradurre per %s" % argument)
    if colorize:
        return "[limegreen]%s[close]" % argument
    else:
        return argument
#- Fine Funzione -


def send_input(entity, argument, lang="", show_input=True, show_prompt=True):
    """
    Invia un input preoccupandosi di convertirlo prima nella lingua corretta
    per essere trovata dall'interprete.
    E' importante che l'argomento lang sia corrispondente alla lingua dell'input
    in argument.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    if lang != "it" and lang != "en" and lang != "":
        log.bug("lang non è un parametro valido: %r" % lang)
        return ""

    if show_input != True and show_input != False:
        log.bug("show_input non è un parametro valido: %r" % show_input)
        return ""

    if show_prompt != True and show_prompt != False:
        log.bug("show_prompt non è un parametro valido: %r" % show_prompt)
        return ""

    # -------------------------------------------------------------------------

    args = argument.split()
    args[0] = translate_input(entity, args[0], lang)
    argument = " ".join(args)

    # Invia il comando ottenuto all'interprete
    interpret(entity, argument, show_input=show_input, show_prompt=show_prompt)
#- Fine Funzione -


#- FUNZIONI RELATIVE ALL'INTERPRETAZIONE DEI SOCIAL ----------------------------

def check_social(entity, command, argument="", behavioured=False):
    """
    Invia i messaggi corretti relativamente ad un comando di social.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not command:
        log.bug("command non è un parametro valido: %r" % command)
        return

    # -------------------------------------------------------------------------

    try:
        social = database["socials"][command.fun_name]
    except NameError:
        log.bug("Social %s, inviato dall'entità %s, errato o inesistente nel database dei social." % (entity.code, command.fun_name))
        return

    active_trigger_suffix  = "active_" + social.get_input_argument()
    passive_trigger_suffix = "passive_" + social.get_input_argument()

    # Se non è stato passato nessun argomento invia il messaggio di social adatto
    if not argument:
        force_return = check_trigger(entity, "before_" + active_trigger_suffix, entity, None, argument, behavioured)
        if force_return:
            return
        force_return = check_trigger(entity.location, "before_" + passive_trigger_suffix, entity, None, argument, behavioured)
        if force_return:
            return
        # Esegue il trigger anche sulle altre entità perché così funziona il
        # caso in cui per esempio un player ha eseguito un nod e un mob è in
        # attesa di un sì
        for contain in entity.location.iter_contains(use_reversed=True):
            force_return = check_trigger(contain, "before_" + passive_trigger_suffix, entity, None, argument, behavioured)
            if force_return:
                continue

        entity.act(social.get_racial_message(entity, "entity_no_arg"), TO.ENTITY)
        # others_no_arg è un messaggio facoltativo
        racial_message = social.get_racial_message(entity, "others_no_arg")
        if racial_message:
            entity.act(racial_message, TO.OTHERS)

        force_return = check_trigger(entity, "after_" + active_trigger_suffix, entity, None, argument, behavioured)
        if force_return:
            return
        force_return = check_trigger(entity.location, "after_" + passive_trigger_suffix, entity, None, argument, behavioured)
        if force_return:
            return
        for contain in entity.location.iter_contains(use_reversed=True):
            force_return = check_trigger(contain, "after_" + passive_trigger_suffix, entity, None, argument, behavioured)
            if force_return:
                continue
        return

    # Se invece è stato passato un argomento trova la vittima
    target = entity.find_entity_extensively(argument)
    if not target:
        target = entity.find_entity(argument, location=entity)
        if not target:
            entity.send_output("Non trovi nessun [white]%s[close] qui intorno." % argument)
            return

    # Se la vittima e l'entità sono uguali cerca il messaggio di sociale _auto
    # oppure se questo non esiste il no_arg che ne fa le veci
    if target == entity:
        force_return = check_trigger(entity, "before_" + active_trigger_suffix, entity, target, argument, behavioured)
        if force_return:
            return
        force_return = check_trigger(target, "before_" + passive_trigger_suffix, entity, target, argument, behavioured)
        if force_return:
            return

        # Se non c'è il messaggio entity_auto c'è entity_no_arg
        msg_auto = social.get_racial_message(entity, "entity_auto")
        if not msg_auto:
            msg_auto = social.get_racial_message(entity, "entity_no_arg")
        entity.act(msg_auto, TO.ENTITY, target)

        # Se non c'è il messaggio others_auto c'è others_no_arg
        msg_auto = social.get_racial_message(entity, "others_auto")
        if not msg_auto:
            msg_auto = social.get_racial_message(entity, "others_no_arg")
        entity.act(msg_auto, TO.OTHERS, target)

        force_return = check_trigger(entity, "after_" + active_trigger_suffix, entity, target, argument, behavioured)
        if force_return:
            return
        force_return = check_trigger(target, "after_" + passive_trigger_suffix, entity, target, argument, behavioured)
        if force_return:
            return
        return

    # Se la vittima non è entity provvede ad inviare il messaggio di social adatto
    force_return = check_trigger(entity, "before_" + active_trigger_suffix, entity, target, argument, behavioured)
    if force_return:
        return
    force_return = check_trigger(target, "before_" + passive_trigger_suffix, entity, target, argument, behavioured)
    if force_return:
        return

    entity.act(social.get_racial_message(entity, "entity_found", target, "tuo"), TO.ENTITY, target)
    entity.act(social.get_racial_message(entity, "others_found", target, "suo"), TO.OTHERS, target)
    entity.act(social.get_racial_message(entity, "target_found"), TO.TARGET, target)

    force_return = check_trigger(entity, "after_" + active_trigger_suffix, entity, target, argument, behavioured)
    if force_return:
        return
    force_return = check_trigger(target, "after_" + passive_trigger_suffix, entity, target, argument, behavioured)
    if force_return:
        return

    # Da qui in poi gestisce l'invio dei social automatici da parte dei mob
    # rispondendo ai social dei pg
    if not entity.IS_PLAYER or not target.IS_MOB:
        return

    # Invia a caso e dopo un secondo invia un social con la stessa intenzione.
    # Non viene inviata la risposta social automatica se ci sono dei trigger
    # relativi a quel social da qualche parte
    # (bb) tuttavia la ricerca così dei trigger è fallace e ci vorrebbe una funzione a parte
    if ("before_" + active_trigger_suffix not in entity.gamescripts and "after_" + active_trigger_suffix not in entity.gamescripts
    and "before_" + active_trigger_suffix not in target.gamescripts and "after_" + active_trigger_suffix not in target.gamescripts
    and "before_" + active_trigger_suffix not in entity.location.gamescripts and "after_" + active_trigger_suffix not in entity.location.gamescripts
    and random.randint(0, 3) == 0 and not behavioured):
        defer(1, social.send_to, target, entity)
#- Fine Funzione -
