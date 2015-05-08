# -*- coding: utf-8 -*-

"""
Permette di spostarsi tra le coordinate della stessa area o in aree differenti
da quella in cui si trova l'amministratore del Mud.
"""


#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.config   import config
from src.enums    import TO
from src.grammar  import grammar_gender
from src.log      import log
from src.utility  import put_final_dot

if config.reload_commands:
    reload(__import__("src.commands.__goto__", globals(), locals(), [""]))
from src.commands.__goto__ import goto_entity_handler, goto_message


#= FUNZIONI ====================================================================

def command_mgoto(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_mgoto")
        entity.send_output(syntax, break_line=False)
        return False

    target, room, last_message = goto_entity_handler(entity, argument, "mobs")
    if not target or not room:
        return False

    if entity.location.IS_ROOM:
        old_coords = "%d %d %d" % (entity.location.x, entity.location.y, entity.location.z)
    else:
        old_coords = "$l"
    old_area_code = entity.location.area.code

    goto_message(entity, room, "mgoto")
    entity = entity.from_location(1, use_repop=True)
    entity.to_location(room, use_look=True)
    entity.act("$n arriva tramite un goto da %s %s" % (old_coords, old_area_code), TO.ADMINS)

    entity.send_output(put_final_dot(last_message))
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "mgoto\n"
    syntax += "mgoto <codice creatura o suo prefisso>\n"
    syntax += "mgoto <nome creatura o suo prefisso>\n"

    return syntax
#- Fine Funzione -
