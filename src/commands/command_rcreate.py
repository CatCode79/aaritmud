# -*- coding: utf-8 -*-

"""
Comando che permette di creare un'istanza di una stanza.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_create", globals(), locals(), [""]))
from src.commands.command_create import create_handler


#= FUNZIONI ====================================================================

def command_rcreate(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    entity.send_output("Il comando per ora non è ancora stato definito, ma forse un giorno...")
    return False

    # (TD)
    #return create_handler(entity, argument, "command_rcreate", "rooms", can_create_multiple=False)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "rcreate\n"
    syntax += "rcreate <codice stanza o suo prefisso>\n"
    syntax += "rcreate <nome stanza o suo prefisso>\n"

    return syntax
#- Fine Funzione -
