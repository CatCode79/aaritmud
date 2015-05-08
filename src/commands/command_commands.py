# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command   import get_command_syntax
from src.enums     import CMDTYPE, OPTION, TRUST
from src.interpret import (inputs_command_it, inputs_command_en,
                           inputs_skill_it, inputs_skill_en,
                           inputs_social_it, inputs_social_en)
from src.log       import log
from src.utility   import is_same, is_prefix, one_argument


#= FUNZIONI ====================================================================

def command_commands(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    syntax = get_command_syntax(entity, "command_commands")
    entity.send_output(syntax, break_line=False)

    return commands_skills_socials_handler(entity, argument, "command")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return get_syntax_template_handler(entity, "commands")
#- Fine Funzione -


def commands_skills_socials_handler(entity, argument, inputs_type):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # argument può essere una stringa vuota

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    arg, argument = one_argument(argument)

    # Ricava in che lingua visualizzare i comandi
    language = "en"
    if entity.IS_PLAYER and OPTION.ITALIAN in entity.account.options:
        language = "it"

    if arg:
        if is_same(arg, ("italiano", "italian")):
            language = "it"
        if is_same(arg, ("inglese", "english")):
            language = "en"

    # Esegue il controllo degli argomenti
    if not arg or is_same(arg, ("italiano", "italian", "inglese", "english")):
        return show_list_normal(entity, language, inputs_type)
    elif is_same(arg, ("traduzione", "translation", "traduzioni", "translations")):
        return show_list_translation(entity, language, inputs_type)
    elif inputs_type == "command" and is_same(arg, ("tipo", "type", "tipi", "types")):
        return show_list_type(entity, language, inputs_type)
    elif entity.trust >= TRUST.MASTER and is_same(arg, ("fiducia", "trust", "fiduce", "trusts")):
        return show_list_trust(entity, language, inputs_type)
    else:
        return show_list_found(entity, language, inputs_type, arg)
#- Fine Funzione -


# (TD) switchare su tutti il parametro inputs_type con language
def show_list_normal(entity, language, inputs_type):
    """
    Visualizza la lista degli input nella lingua voluta.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if language != "it" and language != "en":
        log.bug("italiana non è un parametro valido: %r" % language)
        return False

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    inputs = globals()["inputs_%s_%s" % (inputs_type, language)]

    colspan = "colspan='2'"
    if inputs_type == "social":
        colspan = "colspan='7'"
    label = _get_label_from_type(inputs_type)

    if language == "en":
        result = '''<table class="mud"><tr><td %s>[white]%s in inglese:[close]</td></tr>''' % (colspan, label)
    else:
        result = '''<table class="mud"><tr><td %s>[white]%s in italiano:[close]</td></tr>''' % (colspan, label)

    for input_counter, input in enumerate(inputs):
        show, command, first_word = _check_input(input, entity, inputs_type)
        if not show:
            continue
        if inputs_type == "social":
            new_tr = ""
            if input_counter % 7 == 0:
                if input_counter != 0:
                    new_tr += '''</tr>'''
                new_tr += '''<tr>'''
            result += '''%s<td class='command'>&nbsp;%s&nbsp;</td>''' % (new_tr, first_word)
        else:
            result += '''<tr><td class='command'>%s&nbsp;</td><td>&nbsp;%s</td></tr>''' % (first_word, command.mini_help)

    if inputs_type == "social":
        result += '''</tr></table>'''
    else:
        result += '''</table>'''

    entity.send_output(result, False)
    return True
#- Fine Funzione -


def show_list_translation(entity, language, inputs_type):
    """
    Visualizza una lista degli input della lingua opposta con traduzione a fianco.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if language != "it" and language != "en":
        log.bug("language non è un parametro valido: %r" % language)
        return False

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    inputs_primary   = globals()["inputs_%s_%s" % (inputs_type, ("en" if language == "it" else "it"))]
    inputs_secondary = globals()["inputs_%s_%s" % (inputs_type, language)]

    translated = "tradotti"
    if inputs_type == "skill":
        translated = "tradotte"

    label = _get_label_from_type(inputs_type)

    # Se uno ha bisogno di un comando nella lingua in cui sta giocando, se non
    # lo ha in mente si scorre il commands normale, diversamente è facile che
    # facile che lo abbia in mente con l'altra lingua
    # Per questo qui anche se uno sta utilizzando la lingua italiana la prima
    # colonna è relativa ai comandi in inglese
    if language == "it":
        result = '''<table class="mud"><tr><td colspan='3'>[white]%s %s dall'inglese all'italiano.[close]</td></tr>''' % (label, translated)
    else:
        result = '''<table class="mud"><tr><td colspan='3'>[white]%s %s dall'italiano all'inglese.[close]</td></tr>''' % (label, translated)

    for input in inputs_primary:
        show, command, first_word = _check_input(input, entity, inputs_type)
        if not show:
            continue
        input_translated = get_input_from_fun_name(command.fun_name, inputs_secondary)
        first_word_translated = input_translated.words.split()[0]
        result += '''<tr><td class='command'>%-16s</td><td class='command'>%-16s</td><td>%s</td></tr>''' % (
            first_word, first_word_translated, command.mini_help)

    entity.send_output('''%s</table>''' % result, False)
    return True
#- Fine Funzione -


def show_list_type(entity, language, inputs_type):
    """
    Visualizza una lista degli input suddivisi per tipologia.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if language != "it" and language != "en":
        log.bug("language non è un parametro valido: %r" % language)
        return False

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    inputs = globals()["inputs_%s_%s" % (inputs_type, language)]
    result = '''<table class="mud">'''

    for cmdtype in CMDTYPE.elements:
        if cmdtype == CMDTYPE.SKILL or cmdtype == CMDTYPE.SOCIAL:
            continue
        result += '''<tr><td colspan='2'>[white]- %s:[close]</td></tr>''' % cmdtype.description

        discovered = False
        for input in inputs:
            show, command, first_word = _check_input(input, entity, inputs_type)
            if not show:
                continue
            if command.type != cmdtype:
                continue
            discovered = True
            result += '''<tr><td class='command'>%-16s</td><td>%s</td></tr>''' % (first_word, command.mini_help)
        if not discovered:
            result += '''<tr><td>Nulla.</td></tr>'''

    entity.send_output('''%s</table>''' % result, False)
    return True
#- Fine Funzione -


# (TT) da testare
def show_list_trust(entity, language, inputs_type):
    """
    Visualizza una lista con tutti gli input suddivisi per fiducia.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if language != "it" and language != "en":
        log.bug("language non è un parametro valido: %r" % language)
        return False

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    result = '''<table class="mud">'''

    label  = _get_label_from_type(inputs_type)
    inputs = globals()["inputs_%s_%s" % (inputs_type, language)]
    for trust in TRUST.elements:
        result += '''<tr><td colspan='2'>[white] - %s per la fiducia di %s:[close]</td></tr>''' % (label, trust)
        for input in inputs:
            show, command, first_word = _check_input(input, entity, inputs_type)
            if not show:
                continue
            if command.trust != trust:
                continue
            result += '''<tr><td class='command'>%-16s</td><td>%s</td></tr>''' % (first_word, command.mini_help)

    entity.send_output('''%s</table>''' % result, False)
    return True
#- Fine Funzione -


def show_list_found(entity, language, inputs_type, arg):
    """
    Visualizza una lista con tutti gli input che iniziano con l'argomento.
    passato.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if language != "it" and language != "en":
        log.bug("language non è un parametro valido: %r" % language)
        return False

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    label  = _get_label_from_type(inputs_type)
    result = '''<br><table class="mud"></td></tr>[white]%s trovati che iniziano per %s:[close]</td></tr>''' % (label, arg)

    inputs = globals()["inputs_%s_%s" % (inputs_type, language)]
    discovered = False
    for input in inputs:
        show, command, first_word = _check_input(input, entity, inputs_type)
        if not show:
            continue
        if not is_prefix(arg, input.findable_words):
            continue
        discovered = True
        result += '''<tr><td class='command'>%-16s</td><td>%s</td></tr>''' % (first_word, command.mini_help)

    if not discovered:
        result += '''<tr><td>Nessuno.</td></tr>'''

    entity.send_output('''%s</table>''' % result, False)
    return True
#- Fine Funzione -


def get_input_from_fun_name(fun_name, inputs):
    """
    Passato il nome della funzione di un comando e una lista di input ritorna
    il primo input, non sinonimo, corrispondente al nome della funzione.
    """
    if not fun_name:
        log.bug("fun_name non è un parametro valido: %s" % fun_name)
        return None

    if not inputs:
        log.bug("inputs non è un parametro valido: %s" % inputs)
        return None

    # -------------------------------------------------------------------------

    for input in inputs:
        if input.alternative:
            continue
        if input.command and input.command.fun_name == fun_name:
            return input

    # Se arriva qui è stata passata una funzione di comando inesistente
    log.bug("Il nome della funzione di comando passato è errato: %s" % fun_name)
    return None
#- Fine Funzione -


def get_syntax_template_handler(entity, command_name):
    """
    Esiste per essere chiamata anche dal comando command_skills e command_socials
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax +=  "%s\n" % command_name
    syntax += "%s italiano\n" % command_name
    syntax += "%s inglese\n" % command_name
    syntax += "%s traduzione\n" % command_name
    if command_name == "commands":
        syntax += "%s tipi\n" % command_name
    if entity.trust >= TRUST.MASTER:
        syntax += "%s fiducia\n" % command_name
    syntax += "%s <comando cercato>\n" % command_name

    return syntax
#- Fine Funzione -


def _check_input(input, entity, inputs_type):
    """
    E' una funzioncina che raggruppa dei controlli ricorrenti nelle funzioni
    chiamate dalla command_commands.
    Ritorna 3 argomenti, il primo indica se l'input deve essere visualizzato,
    il secondo è il comando relativo all'input e il terzo è la prima parola
    delle parole dell'input.
    """
    if not input:
        log.bug("input non è un parametro valido: %r" % input)
        return False, "", ""
       
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False, "", ""

    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False, "", ""

    # -------------------------------------------------------------------------

    show = True
    if input.alternative:
        show = False
    if input.command.trust > entity.trust:
        show = False
    if not input.command.fun_name.startswith("%s_" % inputs_type):
        show = False

    first_word = input.words.split()[0]

    return show, input.command, first_word
#- Fine Funzione -


def _get_label_from_type(inputs_type):
    """
    Ritorna la stringa che descrive la 'tipologia' di input visualizzati:
    comando, sociale o skill.
    """
    if not inputs_type:
        log.bug("inputs_type non è un parametro valido: %r" % inputs_type)
        return False

    # -------------------------------------------------------------------------

    if   inputs_type == "command":  return "Comandi"
    elif inputs_type == "skill":    return "Abilità"
    elif inputs_type == "social":   return "Sociali"
    else:
        log.bug("inputs_type passato è errato: %s" % inputs_type)
        return "!errore!"
#- Fine Funzione -
