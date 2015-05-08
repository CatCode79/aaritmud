# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.log      import log
from src.utility  import is_same, is_prefix, one_argument


#= FUNZIONI ====================================================================

def command_usedexits(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_usedexits")
        entity.send_output(syntax, break_line=False)
        return False

    number_of_exits = 0
    arg, argument = one_argument(argument)
    try:
        number_of_exits = int(arg)
    except ValueError:
        entity.send_output("Il primo argomento dev'essere un numero che rappresenta la quantità di uscite volute.")
        return False

    counter = 0
    for room in database["rooms"].itervalues():
        if len(room.exits) == number_of_exits:
            entity.send_output("%s: %s" % (room.code, room.name))
            counter += 1

    if counter > 0:
        entity.send_output("\n")

    plural = "a" if counter == 1 else "e"
    result = "Trovat%s [white]%d[close] stanz%s con [white]%d[close] uscite" % (
        plural, counter, plural, number_of_exits)
    if arg2:
        result += " il cui codice è (o inizia per) [white]%s[close]" % arg2
    else:
        result += "."

    entity.send_output(result)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "usedexits <numero di uscite volute, da 0 in sù>\n"
    syntax += "usedexits <numero di uscite volute, da 0 in sù> <codice stanza, o suo prefisso>\n"

    return syntax
#- Fine Funzione -
