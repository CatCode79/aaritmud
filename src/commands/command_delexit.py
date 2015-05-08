# -*- coding: utf-8 -*-

"""
Comando che permette di rimuovere un'uscita nella direzione desiderata.
"""

#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.enums   import DIR
from src.exit    import get_direction
from src.log     import log
from src.utility import one_argument


#= FUNZIONI ====================================================================

def command_delexit(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_delexit")
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

    if direction not in room.exits:
        entity.send_output("Non c'è nessuna uscita %s da distruggere." % direction.to_dir)
        return False

    del(room.exits[direction])
    entity.send_output("E' stata cancellata l'uscita %s." % direction.to_dir)
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "delexit\n"
    syntax += "delexit <direzione>\n"

    return syntax
#- Fine Funzione -
