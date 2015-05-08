# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.log import log


#= FUNZIONI ====================================================================

def command_aliases(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    entity.send_output('''Puoi modificare gli alias in <a href="/aliases.html", target="aliases">questa pagina</a>.''')
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "aliases\n"
#- Fine Funzione -
