# -*- coding: utf-8 -*-

"""
Permette di spostarsi tra le coordinate della stessa area o in aree differenti
da quella in cui si trova l'amministratore del Mud.
"""


#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.config   import config
from src.database import database
from src.enums    import AREA, TO
from src.grammar  import grammar_gender
from src.log      import log
from src.utility  import is_number, nifty_value_search, multiple_arguments
from src.wild     import create_wild_room

if config.reload_commands:
    reload(__import__("src.commands.__goto__", globals(), locals(), [""]))
from src.commands.__goto__ import goto_message


#= FUNZIONI ====================================================================

def command_rgoto(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_rgoto")
        entity.send_output(syntax, break_line=False)
        return False

    room, more_search = get_room_from_coords(entity, argument)
    if not room:
        if more_search:
            room = entity.find_room(argument)
            if not room:
                if " " in argument and argument[0] not in "'\"":
                    entity.send_output("Stanza non trovata con argomento [green]%s[close], se l'argomento cercato è formato da una frase con spazi inserirlo tra virgolette." % argument)
                else:
                    entity.send_output("Stanza non trovata con argomento [green]%s[close]." % argument)
                return False
        else:
            return False

    goto_message(entity, room, "rgoto")
    entity = entity.from_location(1, use_repop=True)
    entity.to_location(room, use_look=True)
    if entity.previous_location():
        if entity.previous_location().IS_ROOM:
            entity.act("$n arriva tramite un rgoto da %s" % entity.previous_location().get_destination(), TO.ADMINS)
        else:
            entity.act("$n arriva tramite un rgoto da %s" % entity.previous_location().get_name(), TO.ADMINS)
    else:
        entity.act("$n arriva tramite un rgoto", TO.ADMINS)

    return True
#- Fine Funzione -


def get_room_from_coords(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None, False

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return None, False

    # -------------------------------------------------------------------------

    in_room = entity.get_in_room()
    if not in_room:
        log.bug("L'entità %s non si trova in nessuna stanza valida: %r" % (entity.get_name, in_room))
        return None, True

    args = multiple_arguments(argument)
    if len(args) == 2:
        if not is_number(args[0]) or not is_number(args[1]):
            return None, True
        coord_x = int(args[0])
        coord_y = int(args[1])
        coord_z = in_room.z
        area = in_room.area
    elif len(args) == 3:
        if not is_number(args[0]) or not is_number(args[1]) or not is_number(args[2]):
            return None, True
        coord_x = int(args[0])
        coord_y = int(args[1])
        coord_z = int(args[2])
        area = in_room.area
    elif len(args) == 4:
        if not is_number(args[0]) or not is_number(args[1]) or not is_number(args[2]):
            return None, True
        coord_x = int(args[0])
        coord_y = int(args[1])
        coord_z = int(args[2])
        area = nifty_value_search(database["areas"], args[3])
        if not area:
            entity.send_output("Codice d'area simile a [green]%s[close] inesistente." % args[3])
            return None, False
    else:
        return None, True

    coords = "%d %d %d" % (coord_x, coord_y, coord_z)
    if coords in area.rooms:
        return area.rooms[coords], False
    else:
        if area.wild:
            room = create_wild_room(area, coords)
            return room, False
        else:
            entity.send_output("Coordinate [green]%s[close] non trovate nell'area [white]%s[close]." % (coords, area.name))
            return None, False
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "rgoto\n"
    syntax += "rgoto <coordinata x> <coordinata y>\n"
    syntax += "rgoto <coordinata x> <coordinata y> <coordinata z>\n"
    syntax += "rgoto <coordinata x> <coordinata y> <coordinata z> <codice area>\n"
    syntax += "rgoto <codice stanza o suo prefisso o sua parte>n"
    syntax += "rgoto <nome stanza o suo prefisso o sua parte>\n"

    return syntax
#- Fine Funzione -
