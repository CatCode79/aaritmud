# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.log import log


#= FUNZIONI ====================================================================

def command_colors(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    entity.send_output('''Una lista dei colori si può vedere alla pagina <a href="/builder_pages/colors.htm", target="colors">questa pagina</a>.''')
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "colors\n"
#- Fine Funzione -
