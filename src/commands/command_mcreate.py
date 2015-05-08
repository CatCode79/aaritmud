# -*- coding: utf-8 -*-

"""
Comando che permette di creare un'istanza di un mob.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_create", globals(), locals(), [""]))
from src.commands.command_create import create_handler


#= FUNZIONI ====================================================================

def command_mcreate(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return create_handler(entity, argument, "command_mcreate", "proto_mobs", can_create_multiple=True)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "mcreate\n"
    syntax += "mcreate <codice mob o suo prefisso>\n"
    syntax += "mcreate <nome mob o suo prefisso>\n"
    syntax += "mcreate <quantità> <codice mob o suo prefisso>\n"
    syntax += "mcreate <quantità> <nome mob o suo prefisso>\n"

    return syntax
#- Fine Funzione -
