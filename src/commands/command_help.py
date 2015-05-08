# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.database  import database
from src.enums     import TRUST, OPTION
from src.help      import get_help
from src.interpret import translate_input
from src.log       import log
from src.utility   import is_same, one_argument, format_for_admin


#= FUNZIONI ====================================================================

def command_help(entity, argument=""):
    """
    Comando che serve a trovare e visualizzare un argomento di help.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        help = get_help(entity, "help")
        if not help:
            entity.send_output("Nessun aiuto base trovato.")
            return False
    else:
        help = get_help(entity, argument)
        if not help:
            not_found_output  = "Nessun aiuto trovato con argomento [white]%s[close]\n" % argument
            similar_helps = get_similar_helps(entity, argument)
            if similar_helps:
                not_found_output += "%s\n" % similar_helps
            entity.send_output(not_found_output, break_line=False)
            log.huh_helps(entity, argument)
            return False

    output = ""
    # Se si è Admin fa visualizzare anche le parole chiave
    if entity.trust > TRUST.PLAYER:
        if is_same(help.italian_keywords, help.english_keywords):
            output += format_for_admin("Italian/EnlighKeywords: %s" % help.italian_keywords) + "\n"
        else:
            output += format_for_admin("ItalianKeywords: %s" % help.italian_keywords) + "\n"
            output += format_for_admin("EnglishKeywords: %s" % help.english_keywords) + "\n"

    if help.text:
        if is_same(help.code, "help") and help.syntax_function:
            output += help.syntax_function(entity)
        output += "%s\n" % help.text

    if help.admin_text and entity.trust > TRUST.PLAYER:
        output += "%s\n" % help.admin_text

    if help.see_also:
        output += "%s\n" % get_see_also_links(entity, help.see_also)

    entity.send_output(output, break_line=False)
    return True
#- Fine Funzione -


def get_similar_helps(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    output = ""
    # (TD)
    return output
#- Fine Funzione -


def get_see_also_links(entity, see_also):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not see_also:
        log.bug("see_also non è un parametro valido: %r" % see_also)
        return ""

    # -------------------------------------------------------------------------

    help_translation = translate_input(entity, "help", "en")
    if not help_translation:
        log.bug("help_translation non valido: %r" % help_translation)
        help_translation = "aiuto"

    output = "[white]Vedi anche[close]: "

    # Supporto ai SeeAlso composti da solo link
    if see_also.lower().startswith("<a "):
        return output + see_also

    for help_code in see_also.split():
        help_code = help_code.strip(",")
        if help_code not in database["helps"]:
            log.bug("help_code %s non si trova tra gli helps" % help_code)
            continue
        help = database["helps"][help_code]
        if entity.IS_PLAYER and OPTION.ITALIAN in entity.account.options:
            help_keyword, dummy = one_argument(help.italian_keywords)
        else:
            help_keyword, dummy = one_argument(help.english_keywords)
        javascript_code = '''javascript:parent.sendInput('%s %s');''' % (
            help_translation, help_keyword)
        output += '''<a href="%s">%s</a>, ''' % (javascript_code, help_keyword)

    return output.rstrip(", ")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "help\n"
    syntax += "help <argomento cercato>\n"

    return syntax
#- Fine Funzione -
