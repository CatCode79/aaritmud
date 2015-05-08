# -*- coding: utf-8 -*-

"""
Comando che permette di aggiungere un'uscita nella direzione desiderata ed
eventualmente inserirvi una destinazione.
"""


#= IMPORT ======================================================================

from src.area    import get_area_from_argument
from src.command import get_command_syntax
from src.exit    import Exit, get_direction
from src.enums   import DIR
from src.log     import log
from src.room    import Destination
from src.utility import one_argument, multiple_arguments, is_number


#= FUNZIONI ====================================================================

def command_addexit(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_addexit")
        entity.send_output(syntax, break_line=False)
        return False

    if not entity.location.IS_ROOM:
        entity.send_output("Non ti trovi in una stanza ma in %s" % entity.location.code)
        return False

    room = entity.location

    arg1, argument = one_argument(argument)
    direction = get_direction(arg1)
    if direction == DIR.NONE:
        entity.send_output("Direzione non valida ricavata dall'argomento %s" % arg1)
        return False

    if direction in room.exits:
        if room.exits[direction].destination:
            destination_message = " che porta a %s" % room.exits[direction].destination
        else:
            destination_message = ""
        entity.send_output("C'è già un uscita %s%s, non puoi aggiungerne un'altra se non rimuovendola con il comando [limegreen]delexit[close] con il comando [limegreen]modifyexit[close]." % (
            direction.to_dir))
        return False

    # Supporto per la destinazione
    destination = None
    if argument:
        args = multiple_arguments(argument)
        if len(args) not in (3, 4):
            entity.send_output("Sintassi del comando non valida, se si vuole specificare una destinazione servono le relative coordinate ed eventualmente il codice dell'area.")
            return False
        if not is_number(args[0]):
            entity.send_output("La coordinata X non è un numero valido: %s" % args[0])
            return False
        if not is_number(args[1]):
            entity.send_output("La coordinata Y non è un numero valido: %s" % args[1])
            return False
        if not is_number(args[2]):
            entity.send_output("La coordinata Z non è un numero valido: %s" % args[2])
            return False
        if len(args) == 4:
            area = get_area_from_argument(args[3])
            if not area:
                entity.send_output("Area non trovata con argomento %s" % args[3])
                return False
        else:
            area = entity.area
        destination = Destination(int(args[0]), int(args[1]), int(args[2]), area)

    # Crea la nuova uscita da zero
    exit = Exit(direction)
    if destination:
        exit.destination = destination

    room.exits[direction] = exit
    entity.send_output("E' stata aggiunta l'uscita %s." % direction.to_dir)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "addexit\n"
    syntax += "addexit <direzione>\n"
    syntax += "addexit <direzione> <coordinata x> <coordinata y> <coordinata z>\n"
    syntax += "addexit <direzione> <coordinata x> <coordinata y> <coordinata z> <area di destinazione>\n"

    return syntax
#- Fine Funzione -
