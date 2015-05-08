# -*- coding: utf-8 -*-

"""
Comando che permette di invocare un'istanza esistente di item.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_invoke", globals(), locals(), [""]))
from src.commands.command_invoke import invoke_handler


#= FUNZIONI ====================================================================

def command_iinvoke(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    return invoke_handler(entity, argument, "command_iinvoke", "items")
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "iinvoke\n"
    syntax += "iinvoke <codice oggetto o suo prefisso>\n"
    syntax += "iinvoke <nome oggetto o suo prefisso>\n"

    return syntax
#- Fine Funzione -
