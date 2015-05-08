# -*- coding: utf-8 -*-

"""
Comando che permette di invocare un'istanza esistente di room.
"""


#= IMPORT ======================================================================

from src.config import config
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.command_invoke", globals(), locals(), [""]))
from src.commands.command_invoke import invoke_handler


#= FUNZIONI ====================================================================

def command_rinvoke(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    entity.send_output("Non ancora funzionante, ma chissà se un giorno...")
    return False
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "rinvoke\n"
    syntax += "rinvoke <codice stanza o suo prefisso o sua parte>\n"
    syntax += "rinvoke <nome stanza o suo prefisso o sua parte>\n"

    return syntax
#- Fine Funzione -
