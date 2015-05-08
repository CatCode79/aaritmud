# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.log import log


#= FUNZIONI ====================================================================

def command_areas(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    entity.send_output('''Una lista delle aree è visualizzabile <a href="/areas.html", target="areas">qui</a>.''')
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "areas\n"
#- Fine Funzione -
