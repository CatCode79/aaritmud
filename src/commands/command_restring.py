# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.account import get_error_message_name
from src.color   import check_colors, color_first_upper
from src.command import get_command_syntax
from src.log     import log
from src.utility import is_prefix, to_capitalized_words, one_argument


#= FUNZIONI ====================================================================

def command_restring(entity, argument=""):
    """
    Permette di modificare la short il nome e la descrizione dell'oggetto voluto.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_restring")
        entity.send_output(syntax, break_line=False)
        return False

    arg1, argument = one_argument(argument)

    target = entity.find_entity_extensively(arg1, inventory_pos="first")
    if not target:
        entity.send_output("Nessuna entità trovata con argomento [white]%s[close]." % arg1)
        return False

    if not argument:
        output  = "[white]%s[close]:\n" % target.code
        output += '''<table class='mud'>'''
        if not target.IS_PLAYER:
            output += '''<tr><td>KeywordsName:</td><td>%s</td></tr>''' % target.keywords_name
            output += '''<tr><td>KeywordsShort:</td><td>%s</td></tr>''' % target.keywords_short
            output += '''<tr><td>KeywordsShortNight:</td><td>%s</td></tr>''' % target.keywords_short_night
        output += '''<tr><td>Name:</td><td>%s</td></tr>''' % target.name
        if target.short:
            output += '''<tr><td>Short:</td><td>%s</td></tr>''' % target.short
        if target.short_night:
            output += '''<tr><td>ShortNight:</td><td>%s</td></tr>''' % target.short_night
        if target.long:
            output += '''<tr><td>Long:</td><td>%s</td></tr>''' % target.long
        if target.long_night:
            output += '''<tr><td>LongNight:</td><td>%s</td></tr>''' % target.long_night
        output += '''<tr><td>Descr:</td><td>%s</td></tr>''' % target.descr
        if target.descr_night:
            output += '''<tr><td valign="top">DescrNight:</td><td>%s</td></tr>''' % target.descr_night
        if target.descr_hearing:
            output += '''<tr><td valign="top">DescrHearing:</td><td>%s</td></tr>''' % target.descr_hearing
        if target.descr_hearing_night:
            output += '''<tr><td valign="top">DescrHearingNight:</td><td>%s</td></tr>''' % target.descr_hearing_night
        if target.descr_smell:
            output += '''<tr><td valign="top">DescrSmell:</td><td>%s</td></tr>''' % target.descr_smell
        if target.descr_smell_night:
            output += '''<tr><td valign="top">DescrSmellNight:</td><td>%s</td></tr>''' % target.descr_smell_night
        if target.descr_touch:
            output += '''<tr><td valign="top">DescrTouch:</td><td>%s</td></tr>''' % target.descr_touch
        if target.descr_touch_night:
            output += '''<tr><td valign="top">DescrTouchNight:</td><td>%s</td></tr>''' % target.descr_touch_night
        if target.descr_taste:
            output += '''<tr><td valign="top">DescrTaste:</td><td>%s</td></tr>''' % target.descr_taste
        if target.descr_taste_night:
            output += '''<tr><td valign="top">DescrTasteNight:</td><td>%s</td></tr>''' % target.descr_taste_night
        if target.descr_sixth:
            output += '''<tr><td valign="top">DescrSixth:</td><td>%s</td></tr>''' % target.descr_sixth
        if target.descr_sixth_night:
            output += '''<tr><td valign="top">DescrSixthNight:</td><td>%s</td></tr>''' % target.descr_sixth_night
        output += '''</table>'''
        if target.IS_PLAYER and not target.game_request:
            entity.send_output("Il giocatore %s è [darkslategray]offline[close]")
        entity.send_output(output, break_line=False)
        return True

    arg2, argument = one_argument(argument)
    attribute = ""
    if is_prefix(arg2, ("KeywordsName", "keywords_name")):
        attribute = "keywords_name"
        attr_descr = "le parole chiavi del nome"
    elif is_prefix(arg2, ("KeywordsShort", "keywords_short")):
        attribute = "keywords_short"
        attr_descr = "le parole chiavi della short"
    elif is_prefix(arg2, ("KeywordsShortNight", "keywords_short_night")):
        attribute = "keywords_short_night"
        attr_descr = "le parole chiavi della short notturna"
    elif is_prefix(arg2, ("Name", "nome")):
        attribute = "name"
        attr_descr = "il nome"
    elif is_prefix(arg2, ("Short", "corta")):
        attribute = "short"
        attr_descr = "la short"
    elif is_prefix(arg2, ("ShortNight", "short_night")):
        attribute = "short_night"
        attr_descr = "la short notturna"
    elif is_prefix(arg2, ("Long", "lunga")):
        attribute = "long"
        attr_descr = "la long"
    elif is_prefix(arg2, ("LongNight", "long_night")):
        attribute = "long_night"
        attr_descr = "la long notturna"
    elif is_prefix(arg2, ("Descr", "descr", "Descrizione", "description")):
        attribute = "descr"
        attr_descr = "la descrizione"
    elif is_prefix(arg2, ("DescrNight", "descr_night")):
        attribute = "descr_night"
        attr_descr = "la descrizione notturna"
    elif is_prefix(arg2, ("DescrHearing", "descr_hearing")):
        attribute = "descr_hearing"
        attr_descr = "la descrizione uditiva"
    elif is_prefix(arg2, ("DescrHearingNight", "descr_hearing_night")):
        attribute = "descr_hearing_night"
        attr_descr = "la descrizione uditiva notturna"
    elif is_prefix(arg2, ("DescrSmell", "descr_smell")):
        attribute = "descr_smell"
        attr_descr = "la descrizione olfattiva"
    elif is_prefix(arg2, ("DescrSmellNight", "descr_smell_night")):
        attribute = "descr_smell_night"
        attr_descr = "la descrizione olfattiva notturna"
    elif is_prefix(arg2, ("DescrTouch", "descr_touch")):
        attribute = "descr_touch"
        attr_descr = "la descrizione tattile"
    elif is_prefix(arg2, ("DescrTouchNight", "descr_touch_night")):
        attribute = "descr_touch_night"
        attr_descr = "la descrizione tattile notturna"
    elif is_prefix(arg2, ("DescrTaste", "descr_taste")):
        attribute = "descr_taste"
        attr_descr = "la descrizione gustativa"
    elif is_prefix(arg2, ("DescrTasteNight", "descr_taste_night")):
        attribute = "descr_taste_night"
        attr_descr = "la descrizione gustativa notturna"
    elif is_prefix(arg2, ("DescrSixth", "descr_sixth")):
        attribute = "descr_sixth"
        attr_descr = "la descrizione intuitiva"
    elif is_prefix(arg2, ("DescrSixthNight", "descr_sixth_night")):
        attribute = "descr_sixth_night"
        attr_descr = "la descrizione intuitiva notturna"

    if not attribute:
        syntax = "L'etichetta da modificare all'entità '%s' è errata: %s" % (target.code, arg2)
        syntax += get_command_syntax(entity, "command_restring")
        entity.send_output(syntax, break_line=False)
        return False

    if not argument:
        syntax = "Il testo da sostituire nell'etichetta è vuoto."
        syntax += get_command_syntax(entity, "command_restring")
        entity.send_output(syntax, break_line=False)
        return False

    if not check_colors(argument):
        entity.send_output("Errore nella colorazione del testo: %s" % argument)
        return False

    if getattr(target, attribute) == argument:
        entity.send_output("Inutile modificare %s di '%s' con un'altra stringa uguale." % (attr_descr, target.code))
        return False

    # Se si sta rinominando un giocatore allora si tiene traccia del vecchio nome
    if target.IS_PLAYER:
        if attribute == "name":
            argument = color_first_upper(argument)
            err_msg_name = get_error_message_name(argument, True, "players")
            if err_msg_name:
                entity.send_output(err_msg_name)
                return False
            if not is_same(argument, target.name):
                target.old_names += " " + target.name
            # (TD) fare anche i messaggi d'avviso per gli altri attributi? da pensare
            target.send_output("\nTi è stato cambiato il nome da %s a %s" % (target.name, argument))
            target.send_prompt()
        elif attribute in ("keywords_name", "keywords_short", "keywords_short_night"):
            entity.send_output("È impossibile modificare %s nei giocatori." % attr_descr)
            return False

    setattr(target, attribute, argument)
    entity.send_output("Hai modificato il testo dell'etichetta %s di '%s' in %s" % (
        to_capitalized_words(attribute), target.code, argument))
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "restring <nome o codice entità>\n"
    syntax += "restring <nome o codice entità> KeywordsName <nuove chiavi>\n"
    syntax += "restring <nome o codice entità> KeywordsShort <nuove chiavi>\n"
    syntax += "restring <nome o codice entità> KeywordsShortNight <nuove chiavi>\n"
    syntax += "restring <nome o codice entità> Name <nuovo nome>\n"
    syntax += "restring <nome o codice entità> Short <nuova short>\n"
    syntax += "restring <nome o codice entità> ShortNight <nuova short>\n"
    syntax += "restring <nome o codice entità> Long <nuova long>\n"
    syntax += "restring <nome o codice entità> LongNight <nuova long>\n"
    syntax += "restring <nome o codice entità> Descr <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrNight <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrHearing <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrHearingNight <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrSmell <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrSmellNight <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrTouch <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrTouchNight <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrTaste <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrTasteNight <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrSixth <nuova descrizione>\n"
    syntax += "restring <nome o codice entità> DescrSixthNight <nuova descrizione>\n"

    return syntax
#- Fine Funzione -
