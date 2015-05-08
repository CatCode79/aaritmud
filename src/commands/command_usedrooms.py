# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.log      import log
from src.utility  import is_prefix, one_argument


#= FUNZIONI ====================================================================

def command_usedrooms(entity, argument):
    if not entity:
        log.bug("entity non un parametro è valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_usedrooms")
        entity.send_output(syntax, break_line=False)
        return False

    number_of_resets = 0
    arg, argument = one_argument(argument)
    try:
        number_of_resets = int(arg)
    except ValueError:
        entity.send_output("Il primo argomento dev'essere un [white]numero[close] che rappresenta la quantità di [blue]reset[close] voluti.")
        return False

    proto_room_resets_counter = {}
    for proto_room_code in database["proto_rooms"]:
        if argument and not is_prefix(argument, proto_room_code):
            continue
        reset_counter = 0
        for room_code in database["rooms"]:
            if is_prefix(proto_room_code, room_code):
                reset_counter += 1
        proto_room_resets_counter[proto_room_code] = reset_counter

    for proto_room_code, reset_counter in proto_room_resets_counter.iteritems():
        if reset_counter == number_of_resets:
            entity.send_output("%s: %s" % (proto_room_code, database["proto_rooms"][proto_room_code].name))

    if len(proto_room_resets_counter) > 0:
        entity.send_output("\n")

    plural = "a" if len(proto_room_resets_counter) == 1 else "e"
    result = "Trovat%s [white]%d[close] stanz%s prototipo resettate [white]%d[close] volte" % (
        plural, len(proto_room_resets_counter), plural, number_of_resets)
    if argument:
        result += " il cui codice è (o inizia per) [white]%s[close]" % argument
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

    syntax += "usedrooms <numero di reset voluti, da 0 in sù>\n"
    syntax += "usedrooms <numero di reset voluti, da 0 in sù> <codice stanza, o suo prefisso>\n"

    return syntax
#- Fine Funzione -
