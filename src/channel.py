# -*- coding: utf-8 -*-

"""
Gestisce le comunicazioni rpg e off-rpg tra i giocatori.
"""


#= IMPORT ======================================================================

import datetime
import random
import re

from src.color      import remove_colors, get_first_color, close_color, color_first_upper
from src.config     import config
from src.enums      import CHANNEL, FLAG, LANGUAGE, LOG, POSITION, ROOM, SECTOR, SKILL
from src.database   import database
from src.grammar    import grammar_gender
from src.interpret  import send_input
from src.gamescript import check_trigger
from src.log        import log
from src.wild       import get_from_direction
from src.utility    import (clean_string, is_same, is_prefix, one_argument,
                            convert_urls, html_escape)


#= VARIABILI ===================================================================

# Bersagli di riferimento per il canale rpg
OBJECTIVE_ROOM   = 0
OBJECTIVE_TARGET = 1
OBJECTIVE_SELF   = 2
OBJECTIVE_GROUP  = 3

# Parolacce che se dette in un canale rpg vengono segnalate
swearwords = ("cazzo", "figa", "fica", "culo", "tette", "merda", "cacca",
              "piscia", "pipì",
              "porco dio", "porcodio", "dio porco", "dioporco",
              "cane dio", "canedio", "dio cane", "diocane",
              "porca madonna", "porcamadonna", "madonna porca", "madonnaporca")

# Lista delle parole che non andrebbero dette in un canale rpg
offrpg_words = ("tv", "maradona", "berlusconi", "jackson")

# regex pattern per la sostituzione di tutti i caratteri non alfanumerici
# della stringa nel controllo delle parolacce e della parole offrpg
ONLY_WORDS_PATTERN = re.compile("[\W_]+")


#= FUNZIONI ====================================================================

def rpg_channel(entity, argument, channel, ask=False, exclaim=False, behavioured=False):
    """
    Gestisce i canali rpg, ha le seguenti caratteristiche:
    - supporto per gli smile
    - supporto per i modi di esprimersi con esclamativo e punto di domanda
    - supporto per gli emote
    - gestione del bersaglio che può essere un'entità, il gruppo o sé stessi
    - (TD) parlata da ubriaco
    - (TD) espansione della potenza della voce in altre stanze
    - (TD) espressioni per le stanze attorno, anche per coloro che riconoscono la voce,
           pensare anche alla suddivisione tra social gestuali e 'rumorosi' per gli smile-espressioni around
    - (TD) modulazione della voce a seconda delle dimensioni di chi parla e della sua voice_potence
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not channel:
        log.bug("channel non è un parametro valido: %r" % channel)
        return False

    # -------------------------------------------------------------------------

    if entity.IS_ROOM:
        return False

    objective = OBJECTIVE_ROOM  # obiettivo del messaggio
    # Linguaggio utilizzato per dire il messaggio
    if entity.IS_ITEM:
        language = LANGUAGE.COMMON
    else:
        language = entity.speaking
    smile = ""            # conterrà l'eventuale espressione di uno smile-social
    emote = ""            # conterrà l'eventuale emote inviato con il messaggio tra due asterischi
    expres_entity = ""    # espressione per chi parla
    expres_room   = ""    # espressione per chi sta ascoltando nella stanza
    expres_objective = "" # espressione per chi riceverà il messaggio

    # Ricava i verbi e il colore relativi al canale
    # Se si sta parlando normalmente la propria lingua vengono utilizzati
    # i verbi razziali per descriverne timbro, flessione o pronuncia
    if channel == CHANNEL.SAY:
        verb_you, verb_it = entity.race.say_verb_you, entity.race.say_verb_it
    else:
        verb_you, verb_it = channel.verb_you, channel.verb_it
    color = get_first_color(channel.name)

    # Se non è stato passato nessun messaggio esce
    if not argument or not remove_colors(argument):
        entity.send_output("Cosa vorresti %s?" % channel)
        return False

    if len(argument) > config.max_google_translate:
        entity.send_output("Non puoi %s un messaggio così logorroico." % channel)
        return False

    # Copia l'argomento originale, in alcuni casi serve recuperarlo poi
    original_argument = argument

    # Controlla se si sta parlando a qualcuno, il controllo sulla particella
    # la esegue in minuscolo, dando per sottinteso che quando uno scrive
    # maiuscolo voglia iniziare un discorso
    target = None
    if argument[0 : 2] == "a ":
        arg, argument = one_argument(argument)
        # Se sta parlando a qualcuno cerca di acquisirlo dal nome successivo
        objective_name, argument = one_argument(argument)
        target = entity.find_entity_extensively(objective_name)
        # con me e self esegue un check senza la is_same volutamente, per evitare
        # ricerche con nome di player che iniziano con Me o Self
        if target == entity or objective_name in ("me", "self"):
            objective = OBJECTIVE_SELF
            # Se si parla da soli lo si fa utilizzando la lingua madre
            language = entity.race.natural_language
        elif target:
            objective = OBJECTIVE_TARGET
            # Se si parla con qualcuno della stessa razza lo si fa utilizzando
            # la lingua preferita dalla razza, è un fattore culturale
            if entity.race == target.race:
                language = entity.race.natural_language
        else:
            # Se non ha trovato nessun 'a <nome bersaglio>' riprende
            # l'argument originale
            argument = original_argument
    # Stessa cosa di sopra ma qui controlla se si stia parlando al gruppo
    elif argument[0 : 3] == "al ":
        arg, argument = one_argument(argument)
        objective_name, argument = one_argument(argument)
        if is_prefix(objective_name, "gruppo"):
            if not entity.group:
                entity.send_output("Non fai parte di nessun gruppo.")
                return False
            # Questa variabile verrà utilizza poi nell'invio del messaggio
            group_members = entity.get_members_here(entity.location)
            if not group_members:
                entity.send_output("Non trovi nessun membro del gruppo vicino a te con cui poter parlare.")
                return False
            objective = OBJECTIVE_GROUP
            # Se si parla in un gruppo in cui tutti sono formati dalla stessa
            # razza si preferirà parlare con la lingua della propria razza
            for group_member in group_members:
                if group_member.race != entity.race:
                    break
            else:
                language = entity.race.natural_language
        else:
            # Se il personaggio non vuole parlare al gruppo recupera
            # il valore originale inviato
            argument = original_argument

    # (TD) Gestisce il caso in cui l'entità si trovi immersa in un liquido
    #if entity.is_immersed():
    #    entity.send_output("Tenti di %s qualcosa ma subito l'acqua ti riempie la gola soffocandoti!" % channel)
    #    entity.points.life -= random.randint(entity.level / 6, entity.level / 4) + 1
    #    return False

    if not entity.location:
        log.bug("entity %s non si trova in una locazione valida: %r (original_argument: %s)" % (
            entity.code, entity.location, original_argument))
        return False

    # Gestisce le stanze che obbligano al silenzio
    if entity.location.IS_ROOM:
        if ROOM.SILENCE in entity.location.flags:
            entity.send_output("Il silenzio del luogo ti blocca la gola impedendoti di %s." % channel)
            return False

        # (TT) Se nella stanza c'è molto casino, tante persone etc etc è difficile
        # parlare piano
        if entity.location.mod_noise > 75 and channel <= CHANNEL.SAY:
            entity.send_output("Non puoi %s con tutta questa confusione!" % channel)
            return False

    # Invia l'appropriato messaggio nel caso in cui trovi argument vuoto
    if not argument:
        send_not_argument_message(entity, objective, channel)
        return False

    # Cerca eventuali smiles nella stringa controllando gli ultimi caratteri
    for social in database["socials"].itervalues():
        if not social.smiles:
            continue
        for single_smile in social.smiles.split():
            if single_smile in argument[-config.chars_for_smile : ]:
                break
        else:
            # Se non trova nessun smile esce dal ciclo dei social e continua
            # col prossimo set di smiles trovato
            continue

        cut_smile = argument.rfind(single_smile)
        # Se argument è formato solo dallo smile invia il corrispondente social
        if cut_smile == 0:
            social_name = social.fun_name[len("social_") : ]
            if objective == OBJECTIVE_TARGET:
                input_to_send = "%s %s" % (social_name, target.name)
            elif objective == OBJECTIVE_SELF:
                input_to_send = "%s %s" % (social_name, entity.name)
            else:
                input_to_send = social_name

            send_input(entity, input_to_send, "en", show_input=False, show_prompt=False)
            return True

        # Altrimenti ne ricava l'espressione dello smile-social e toglie lo
        # smile da argument, se il carattere dopo lo smile era un simbolo di
        # punteggiatura lo attacca alla frase togliendo gli spazi
        first_part  = argument[ : cut_smile]
        second_part = argument[cut_smile + len(single_smile) : ]
        if second_part.strip() and second_part.strip()[0] in "!?.,:;":
            first_part = first_part.rstrip()
            second_part = second_part.lstrip()
        argument = first_part.rstrip() + second_part.rstrip()
        smile = " %s" % social.expression
        break

    # Elabora i punti esclamativi e interrogativi per il canale say.
    # Qui viene utilizzata l'opzione chars_for_smile visto che si sta facendo
    # una cosa simile a sopra, ovvero considerare solo l'ultima parte
    # dell'argomento passato.
    exclamations = argument[-config.chars_for_smile : ].count("!")
    questions    = argument[-config.chars_for_smile : ].count("?")
    if exclamations > questions:
        if channel == CHANNEL.SAY:
            verb_you = "Esclami"
            verb_it  = " esclama"
        exclaim = True
    elif exclamations < questions:
        if channel == CHANNEL.SAY:
            verb_you = "Domandi"
            verb_it  = " domanda"
        ask = True
    # Questo elif sottintende che exclamations e questions siano uguali
    elif exclamations != 0 and questions != 0:
        # Con una stessa quantità di ! e di ? l'ultimo che viene trovato
        # ha maggiore peso rispetto all'altro
        exclamation_pos = argument.rfind("!")
        question_pos = argument.rfind("?")
        if exclamation_pos > question_pos:
            if channel == CHANNEL.SAY:
                verb_you = "Esclami"
                verb_it  = " esclama"
            exclaim = True
        else:
            if channel == CHANNEL.SAY:
                verb_you = "Domandi"
                verb_it  = " domanda"
            ask = True

    # Supporto per piccoli emote separati da * ad inizio argument
    if argument[0] == "*":
        cut_emote = argument[1 : ].find("*")
        if cut_emote != -1:
            emote = " %s" % argument[1 : cut_emote+1].strip()
            if smile:
                emote = " e%s" % emote
            argument = argument[cut_emote+2 : ].strip()

    # Unisce i vari pezzi per formare l'output
    expres_entity = verb_you
    expres_room = verb_it
    expres_target = ""
    if objective == OBJECTIVE_TARGET:
        name = target.get_name(entity)
        expres_entity += " a %s" % name
        expres_room   += " a %s" % name
        expres_target += " ti%s" % verb_it
    elif objective == OBJECTIVE_SELF:
        expres_entity += " a te stess%s" % grammar_gender(entity)
        expres_room   += " a sé stess%s" % grammar_gender(entity)
    elif objective == OBJECTIVE_GROUP:
        members = entity.get_members_here(entity.location)
        if len(members) == 1:
            expres_entity += " a %s" % members[0].name
            expres_room   += " a %s" % members[0].name
            expres_target += " ti%s" % verb_it
        else:
            if len(members) > 5:
                many = "folto "
            else:
                many = ""
            expres_entity += " al gruppo"
            expres_room   += " ad un %sgruppo" % many
            expres_target += "%s al gruppo" % verb_it
    # Aggiunge le eventuali espressioni dello smile e dell'emote
    expres_entity += smile + emote
    expres_room   += smile + emote
    expres_target += smile + emote

    if not argument:
        send_not_argument_message(entity, objective, channel)
        return False

    # Prepara il pezzo riguardante la lingua utilizzata
    language = ""
    if not entity.IS_ITEM and entity.speaking != LANGUAGE.COMMON:
        language = " in lingua %s" % entity.speaking

    # Mischia il testo se si è ubriachi
    original_argument = argument = color_first_upper(argument)
    argument = drunk_speech(argument, entity)

    # Parlando si impara la lingua
    if not entity.IS_ITEM:
        learn_language(entity, channel, entity.speaking)

    # Controlla se vi sono parolacce o parole offrpg e logga i relativi argument
    if entity.IS_PLAYER:
        check_for_badwords(entity, argument)

    # Invia il messaggio a tutti coloro che lo possono sentire
    for location in expand_voice_around(entity, channel):
        if not location:
            log.bug("location per il canale %s e per l'entità %s non è valida: %r" % (channel, entity.code, location))
            continue
        for listener in location.iter_contains(use_reversed=True):
            if listener.position <= POSITION.SLEEP:
                continue

            if listener == entity:
                force_return = check_trigger(entity, "before_rpg_channel", listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue
                force_return = check_trigger(entity, "before_" + channel.trigger_suffix, listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue

                # Invia all'entità il suo stesso messaggio
                first_part = (close_color(color) + expres_entity).rstrip()
                message = "%s: '%s'" % (first_part, close_color(argument))
                send_channel_message(entity, message, True)

                force_return = check_trigger(entity, "after_rpg_channel", listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue
                force_return = check_trigger(entity, "after_" + channel.trigger_suffix, listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue
            else:
                # Fa ascoltare solo ad un'entità di un eventuale gruppo fisico
                listener = listener.split_entity(1)

                force_return = check_trigger(listener, "before_listen_rpg_channel", listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue
                force_return = check_trigger(listener, "before_listen_" + channel.trigger_suffix, listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue

                # Prepara alcune cose a seconda della stanza di provenienza del messaggio
                if entity.location == listener.location:
                    entity_name = entity.get_name(listener)
                    entity_name = color_first_upper(entity_name)
                    from_direction = ""
                elif entity.location.IS_ROOM:
                    # (TD) invia qualcuno a meno che non lo si abbia conosciuto
                    # precedentemente con il sistema di presentazione
                    entity_name = "Qualcuno"
                    from_direction = get_from_direction(listener.location.x, listener.location.y, listener.location.z,
                                                        entity.location.x, entity.location.y, entity.location.z)
                elif entity.location.IS_ACTOR:
                    if entity.location != listener:
                        entity_name = "Qualcuno"  # (TD) come sopra
                    from_direction = " dall'inventario di %s" % entity.location.get_name(listener)
                else:
                    entity_name = "Qualcuno"  # (TD) come sopra
                    from_direction = " da dentro %s" % entity.location.get_name(listener)

                # Prepara la prima parte, quella senza il messaggio
                if objective == OBJECTIVE_ROOM:
                    output = "%s%s%s%s" % (entity_name, close_color(color) + expres_room, language, from_direction)
                elif objective == OBJECTIVE_TARGET or OBJECTIVE_SELF:
                    if listener == target:
                        output = "%s%s%s%s" % (entity_name, close_color(color) + expres_target, language, from_direction)
                    else:
                        output = "%s%s%s%s" % (entity_name, close_color(color) + expres_room, language, from_direction)
                elif objective == OBJECTIVE_GROUP:
                    if listener in group_members:
                        output = "%s%s%s%s" % (entity_name, close_color(color) + expres_target, language, from_direction)
                    else:
                        output = "%s%s%s%s" % (entity_name, close_color(color) + expres_room, language, from_direction)

                output = "<br>%s: '%s'" % (close_color(output).rstrip(), close_color(argument))
                send_channel_message(listener, output, False)
                listener.send_prompt()

                force_return = check_trigger(listener, "after_listen_rpg_channel", listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue
                force_return = check_trigger(listener, "after_listen_" + channel.trigger_suffix, listener, entity, target, argument, ask, exclaim, behavioured)
                if force_return:
                    continue

    return True
#- Fine Funzione -


def send_not_argument_message(entity, objective, channel):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if objective < OBJECTIVE_ROOM or objective > OBJECTIVE_GROUP:
        log.bug("objective non è un parametro valido: %r" % objective)
        return

    if not channel or channel == CHANNEL.NONE:
        log.bug("channel non è un parametro valido: %r" % channel)
        return

    # -------------------------------------------------------------------------

    channel_verb = color_first_upper(str(channel))

    if objective == OBJECTIVE_ROOM:
        entity.send_output("%s che cosa?" % channel_verb)
    elif objective == OBJECTIVE_TARGET:
        entity.send_output("%s a %s che cosa?" % (channel_verb, target.get_name(looker=entity)))
    elif objective == OBJECTIVE_SELF:
        entity.send_output("%s al gruppo che cosa?" % channel_verb)
#- Fine Funzione -


def expand_voice_around(entity, channel):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None

    if  not channel:
        log.bug("channel non è un parametro valido: %r" % channel)
        return None

    # -------------------------------------------------------------------------

    if entity.is_extracted():
        return None

    if entity.location.IS_ROOM or entity.location.is_extracted():
        return (entity.location, )
    else:
        return (entity.location, entity.location.location)
#- Fine Funzione -


def talk_channel(entity, channel, argument):
    """
    Gestisce i canali off rpg.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not channel:
        log.bug("channel non è un parametro valido: %r" % channel)
        return False

    # argument può essere una stringa vuota

    # -------------------------------------------------------------------------

    if not argument or not remove_colors(argument):
        entity.send_output("Con che messaggio vorresti %s?" % channel)
        return False

    if len(argument) > config.max_google_translate:
        entity.send_output("Non puoi %s un messaggio più lungo di %d caratteri" % (channel, config.max_google_translate))
        return False

    argument = convert_urls(argument)
    for player in database["players"].itervalues():
        if not player.game_request:
            continue
        if player == entity:
            continue
        if player.trust < channel.trust:
            continue
        message = "<br>%s%s: '%s'" % (entity.name, channel.verb_it, argument)
        send_channel_message(player, message, False)
        player.send_prompt()

    message = "%s: '%s'" % (channel.verb_you, argument)
    send_channel_message(entity, message, True)

    if channel == CHANNEL.CHAT:
        check_for_badwords(entity, argument)
        log.chat("%s %s: %s\n" % (datetime.datetime.now(), remove_colors(entity.name), remove_colors(argument)))

    return True
#- Fine Funzione -


def send_channel_message(entity, message, personal):
    if not message:
        log.bug("message non è un parametro valido: %r" % message)
        return

    if personal not in (True, False):
        log.bug("personal non è un parametro valido: %r" % personal)
        return

    # -------------------------------------------------------------------------

    if message[0] == "\n":
        message = message[1 : ]

    if personal:
        name = "[white]Tu[close]"
    else:
        name = entity.name

    entity.send_output(message + '''<script>sendChannelMessage("%s", "%s", %s);</script>''' % (
        html_escape(message.replace("<br>", "")), html_escape(name), str(personal).lower()))
#- Fine Funzione -


def check_for_badwords(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    alfanumeric_argument = ONLY_WORDS_PATTERN.sub("", argument)
    if alfanumeric_argument:
        args = clean_string(alfanumeric_argument).split()

        for swearword in swearwords:
            if swearword in args:
                log.badword("parolaccia detta da %s: %s (%s)" % (entity.code, swearword, argument))
                break

        for offrpg_word in offrpg_words:
            if offrpg_word in args:
                log.offrpg("parola offrpg detta da %s: %s (%s)" % (entity.code, offrpg_word, argument))
                break
#- Fine Funzione -


def learn_language(entity, channel, language):
    """
    Impara, con una piccolissima probabilità, una lingua parlandola.
    A seconda del canale utilizzato ha più o meno probabilità di impararla.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if  not channel:
        log.bug("channel non è un parametro valido: %r" % channel)
        return

    if  not language:
        log.bug("language non è un parametro valido: %r" % language)
        return

    # -------------------------------------------------------------------------

    if language not in entity.languages:
        return

    if entity.languages[language] >= config.max_skill_value:
        return

    # Le cose dette con tono normale vengono imparate più facilmente
    if channel == CHANNEL.SAY:
        difficulty = 250
    else:
        difficulty = 300

    if random.randint(0, difficulty) == 0 and entity.knowledged[language] < config.max_skill_value:
        entity.languages[language] += 1  # (BB) fino a che non ci saranno sul serio le skill qui crash
#- Fine Funzione -


#(TD) (bb) language qui deve essere una stringa e non più un elemento
def scramble_language(argument, entity, listener, language):
    """
    Mischia l'argomento passato a seconda del valore minimo conosciuto tra
    colui che parla e colui che ascolta nella lingua parlata.
    """
    if not argument:
        log.bug("listener non è un parametro valido: %r" % argument)
        return

    if not entity:
        log.bug("listener non è un parametro valido: %r" % entity)
        return

    if not listener:
        log.bug("listener non è un parametro valido: %r" % listener)
        return

    if  not language:
        log.bug("listener non è un parametro valido: %r" % language)
        return

    # -------------------------------------------------------------------------

    # Tutte le razze conoscono la lingua comune, quindi ritorna subito la frase
    # così com'è (TD) non proprio tutte le razze, in futuro aggiungere un altro alfabeto apposito
    if language == LANGUAGE.COMMON:
        return argument

    # (TD) Qui la quantità di conoscenza di una lingua dovrebbe variare a
    # seconda del tipo di entità (se mob quasi sempre è config.max_skill_value)
    language_knowledge = 0
    if language in listener.languages:
        language_knowledge = listener.languages[language]
    if language_knowledge >= config.max_skill_value:
        return argument

    # Pre conversione
    position = 0
    result = ""
    while position < len(argument):
        for words in language.pre_conversions:
            # (TD) attualmente viene utilizzato un 'in' al posto della
            # is_prefix per la difficoltà di aumentare la posizione di un certo
            # tot che può non essere uguale rispetto a len(words[0]) poiché
            # in argument vi possono essere colori e accenti-apostrofo
            if words[0] in argument[position : ]:
                result += words[1]
                position += len(words[0])
                break
        else:
            # (BB) se vi sono dei colori li tradurrebbe, e non va bene
            char = argument[position]
            if char.isalpha() and random.randint(1, config.max_skill_value) > language_knowledge:
                #print(ord(char) - ord("a"))
                if char.isupper():
                    result += language.alphabet[ord(char) - ord("a")].upper()
                else:
                    result += language.alphabet[ord(char) - ord("a")]
            else:
                result += char
            position += 1

    # Post conversione
    argument = result
    position = 0
    result = ""
    while position < len(argument):
        for words in language.post_conversions:
            # (TD) stesso problema di cui sopra
            if words[0] in argument[position : ]:
                result += words[1]
                position += len(words[0])
                break
        else:
            result += argument[position]
            position += 1

    return result
#- Fine Funzione -


def drunk_speech(argument, entity):
    """
    Se l'entità è ubriaca converte l'argomento e lo ritorna con la parlata
    da ubriaco.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    # (TD)
    return argument
#- Fine Funzione -


def dream_speech(argument, entity):
    """
    Gli rpg_channel che l'entità dice quando è dall'"altra parte" nel sogno
    vengono convertiti in parlato nel sonno.
    """
    if not argument:
        log.bug("argument non è parametro valido: %r" % argument)
        return

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    # (TD)
    return argument
#- Fine Funzione -
