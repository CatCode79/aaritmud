# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.config  import config
from src.log     import log

if config.reload_commands:
    reload(__import__("src.commands.command_commands", globals(), locals(), [""]))
from src.commands.command_commands import get_syntax_template_handler, commands_skills_socials_handler


#= FUNZIONI ====================================================================

def command_socials(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    syntax = get_command_syntax(entity, "command_socials")
    entity.send_output(syntax, break_line=False)

    return commands_skills_socials_handler(entity, argument, "social")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return get_syntax_template_handler(entity, "socials")
#- Fine Funzione -
