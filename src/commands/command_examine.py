# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando 'esamina', è come il look ma dona maggiori
informazioni su certe cose.
"""


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.config  import config
from src.enums   import OPTION, TO
from src.log     import log

if config.reload_commands:
    reload(__import__("src.commands.command_look", globals(), locals(), [""]))
from src.commands.command_look import command_look


#= COSTANTI ====================================================================

VERBS = {}
VERBS["infinitive"] = "[orange]esaminare[close]"


#= FUNZIONI ====================================================================

def command_examine(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_examine")
            entity.send_output(syntax, break_line=False)
        return False

    # (TD)
    return command_look(entity, argument, behavioured=behavioured, use_examine=True)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "examine\n"
    syntax += "examine <qualcuno o qualcosa da guardare>\n"
    syntax += "examine dentro <qualcuno o qualcosa da guardare>\n"
    syntax += "examine dietro <qualcuno o qualcosa da guardare>\n"
    syntax += "examine sotto <qualcuno o qualcosa da guardare>\n"
    syntax += "examine sopra <qualcuno o qualcosa da guardare>\n"
    syntax += "examine <in una direzione>\n"
    syntax += "examine cielo\n"

    return syntax
#- Fine Funzione -
