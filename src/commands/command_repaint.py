# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.area    import get_area_from_argument
from src.color   import check_colors
from src.command import get_command_syntax
from src.log     import log
from src.utility import is_prefix, to_capitalized_words, multiple_arguments, one_argument


#= FUNZIONI ====================================================================

def command_repaint(entity, argument=""):
    """
    Permette di modificare la short, nome e descrizione di una stanza.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not entity.location.IS_ROOM:
        entity.send_output("Non ti trovi in una stanza ma in %s." % entity.location.code)
        return False

    room = entity.location

    if not argument:
        syntax = get_command_syntax(entity, "command_repaint")
        entity.send_output(syntax)

        output  = "[white]%s[close]:\n" % room.code
        output += '''<table class='mud'>'''
        output += '''<tr><td>Name:</td><td>%s</td></tr>''' % room.name
        if room.short:
            output += '''<tr><td>Short:</td><td>%s</td></tr>''' % room.short
        if room.short_night:
            output += '''<tr><td>ShortNight:</td><td>%s</td></tr>''' % room.short_night
        output += '''<tr><td valign="top">Descr:</td><td>%s</td></tr>''' % room.descr
        if room.descr_night:
            output += '''<tr><td valign="top">DescrNight:</td><td>%s</td></tr>''' % room.descr_night
        if room.descr_hearing:
            output += '''<tr><td valign="top">DescrHearing:</td><td>%s</td></tr>''' % room.descr_hearing
        if room.descr_hearing_night:
            output += '''<tr><td valign="top">DescrHearingNight:</td><td>%s</td></tr>''' % room.descr_hearing_night
        if room.descr_smell:
            output += '''<tr><td valign="top">DescrSmell:</td><td>%s</td></tr>''' % room.descr_smell
        if room.descr_smell_night:
            output += '''<tr><td valign="top">DescrSmellNight:</td><td>%s</td></tr>''' % room.descr_smell_night
        if room.descr_touch:
            output += '''<tr><td valign="top">DescrTouch:</td><td>%s</td></tr>''' % room.descr_touch
        if room.descr_touch_night:
            output += '''<tr><td valign="top">DescrTouchNight:</td><td>%s</td></tr>''' % room.descr_touch_night
        if room.descr_taste:
            output += '''<tr><td valign="top">DescrTaste:</td><td>%s</td></tr>''' % room.descr_taste
        if room.descr_taste_night:
            output += '''<tr><td valign="top">DescrTasteNight:</td><td>%s</td></tr>''' % room.descr_taste_night
        if room.descr_sixth:
            output += '''<tr><td valign="top">DescrSixth:</td><td>%s</td></tr>''' % room.descr_sixth
        if room.descr_sixth_night:
            output += '''<tr><td valign="top">DescrSixthNight:</td><td>%s</td></tr>''' % room.descr_sixth_night
        output += '''</table>'''
        entity.send_output(output, break_line=False)
        return False

    arg1, argument = one_argument(argument)
    attribute = ""
    if is_prefix(arg1, ("name", "nome")):
        attribute = "name"
        attr_descr = "il nome"
    elif is_prefix(arg1, ("short", "corta")):
        attribute = "short"
        attr_descr = "la short"
    elif is_prefix(arg1, ("ShortNight", "short_night", "CortaNotte", "corta_notte")):
        attribute = "short_night"
        attr_descr = "la short notturna"
    elif is_prefix(arg1, ("Descr", "descr", "Descrizione", "description")):
        attribute = "descr"
        attr_descr = "la descrizione"
    elif is_prefix(arg1, ("DescrNight", "descr_night")):
        attribute = "descr_night"
        attr_descr = "la descrizione notturna"
    elif is_prefix(arg1, ("DescrHearing", "descr_hearing")):
        attribute = "descr_hearing"
        attr_descr = "la descrizione uditiva"
    elif is_prefix(arg1, ("DescrHearingNight", "descr_hearing_night")):
        attribute = "descr_hearing_night"
        attr_descr = "la descrizione uditiva notturna"
    elif is_prefix(arg1, ("DescrSmell", "descr_smell")):
        attribute = "descr_smell"
        attr_descr = "la descrizione olfattiva"
    elif is_prefix(arg1, ("DescrSmellNight", "descr_smell_night")):
        attribute = "descr_smell_night"
        attr_descr = "la descrizione olfattiva notturna"
    elif is_prefix(arg1, ("DescrTouch", "descr_touch")):
        attribute = "descr_touch"
        attr_descr = "la descrizione tattile"
    elif is_prefix(arg1, ("DescrTouchNight", "descr_touch_night")):
        attribute = "descr_touch_night"
        attr_descr = "la descrizione tattile notturna"
    elif is_prefix(arg1, ("DescrTaste", "descr_taste")):
        attribute = "descr_taste"
        attr_descr = "la descrizione gustativa"
    elif is_prefix(arg1, ("DescrTasteNight", "descr_taste_night")):
        attribute = "descr_taste_night"
        attr_descr = "la descrizione gustativa notturna"
    elif is_prefix(arg1, ("DescrSixth", "descr_sixth")):
        attribute = "descr_sixth"
        attr_descr = "la descrizione intuitiva"
    elif is_prefix(arg1, ("DescrSixthNight", "descr_sixth_night")):
        attribute = "descr_sixth_night"
        attr_descr = "la descrizione intuitiva notturna"

    if not attribute:
        syntax = "L'etichetta da modificare all'entità '%s' è errata: %s" % (room.code, arg1)
        syntax += get_command_syntax(entity, "command_repaint")
        entity.send_output(syntax, break_line=False)
        return False

    if not argument:
        syntax = "Il testo da sostituire nell'etichetta è vuoto."
        syntax += get_command_syntax(entity, "command_repaint")
        entity.send_output(syntax, break_line=False)
        return False

    if not check_colors(argument):
        entity.send_output("Errore nella colorazione del testo: %s" % argument)
        return False

    if getattr(room, attribute) == argument:
        entity.send_output("Inutile modificare %s di '%s' con un'altra stringa uguale." % (attr_descr, room.code))
        return False

    setattr(room, attribute, argument)
    entity.send_output("Hai modificato il testo dell'etichetta %s di '%s' in %s" % (
        to_capitalized_words(attribute), room.code, argument))
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "repaint\n"
    syntax += "repaint KeywordsName <nuove chiavi>\n"
    syntax += "repaint KeywordsShort <nuove chiavi>\n"
    syntax += "repaint KeywordsShortNight <nuove chiavi>\n"
    syntax += "repaint Name <nuovo nome>\n"
    syntax += "repaint Short <nuova short>\n"
    syntax += "repaint ShortNight <nuova short>\n"
    syntax += "repaint Long <nuova long>\n"
    syntax += "repaint LongNight <nuova long>\n"
    syntax += "repaint Descr <nuova descrizione>\n"
    syntax += "repaint DescrNight <nuova descrizione>\n"
    syntax += "repaint DescrHearing <nuova descrizione>\n"
    syntax += "repaint DescrHearingNight <nuova descrizione>\n"
    syntax += "repaint DescrSmell <nuova descrizione>\n"
    syntax += "repaint DescrSmellNight <nuova descrizione>\n"
    syntax += "repaint DescrTouch <nuova descrizione>\n"
    syntax += "repaint DescrTouchNight <nuova descrizione>\n"
    syntax += "repaint DescrTaste <nuova descrizione>\n"
    syntax += "repaint DescrTasteNight <nuova descrizione>\n"
    syntax += "repaint DescrSixth <nuova descrizione>\n"
    syntax += "repaint DescrSixthNight <nuova descrizione>\n"

    return syntax
#- Fine Funzione -
