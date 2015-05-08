# -*- coding: utf-8 -*-

"""
Comando che permette di creare un'istanza di un oggetto.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_create", globals(), locals(), [""]))
from src.commands.command_create import create_handler


#= FUNZIONI ====================================================================

def command_icreate(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return create_handler(entity, argument, "command_icreate", "proto_items", can_create_multiple=True)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "icreate\n"
    syntax += "icreate <codice oggetto o suo prefisso>\n"
    syntax += "icreate <nome oggetto o suo prefisso>\n"
    syntax += "icreate <quantità> <codice oggetto o suo prefisso>\n"
    syntax += "icreate <quantità> <nome oggetto o suo prefisso>\n"

    return syntax
#- Fine Funzione -
